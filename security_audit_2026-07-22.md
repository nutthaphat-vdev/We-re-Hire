# Security Audit — WeHire (รอบ 2)

> วันที่ตรวจ: **2026-07-22** · ต่อจาก audit เดิม 26 พ.ค.
> Scope: `main.py` (~4,400 บรรทัด) + `index.html` (~6,480 บรรทัด)
> วิธี: ไล่ตรวจโค้ดจริงทีละชั้น (auth · SQL · authorization · frontend) ไม่ได้เขียนจากความจำ
>
> ⚠️ **ผมไม่ใช่ผู้เชี่ยวชาญ security มืออาชีพ** — นี่คือการตรวจเชิงโครงสร้างที่ครอบ OWASP ระดับ MVP
> ก่อน pilot ที่มีเงินจริงไหลผ่าน (Phase 3 escrow) ควรจ้าง pentest จริงอีกรอบ

---

## 🎯 สรุปผู้บริหาร

**ข่าวดี: พื้นฐาน security แน่นเกินคาดสำหรับ solo + AI**
JWT ทำถูก (ES256+JWKS), SQL parameterized ทั้งหมด, ownership check ครบ, XSS guard ครอบเกือบหมด, rate limit มี, timing-safe login มี, upload จำกัด size/type แล้ว

**ที่ต้องแก้ — ไม่มี Critical แต่มี 1 ตัวที่ควรรีบ:**

| # | ระดับ | เรื่อง | แก้ยากไหม |
|---|-------|-------|-----------|
| 1 | 🔴 **สูง** | GitHub token `ghp_9Qiy…` ยัง live + เคยโผล่ plaintext | ง่าย (revoke) |
| 2 | 🟠 กลาง | CORS มี `"null"` origin ใน default | 1 บรรทัด |
| 3 | 🟠 กลาง | admin secret เทียบด้วย `!=` ไม่ใช่ timing-safe | 1 บรรทัด |
| 4 | 🟡 ต่ำ | rate limit ครอบแค่ 2 endpoint | เพิ่มได้เรื่อยๆ |
| 5 | 🟡 ต่ำ | error message เผย exception ดิบ (`Token ไม่ถูกต้อง: {e}`) | เล็ก |
| 6 | 🔵 ข้อสังเกต | `_notifTranslateTitle` EN-fallback ผ่าน esc แล้ว แต่ควรจำ pattern |  — |

---

## ✅ สิ่งที่ตรวจแล้วผ่าน (ยืนยันจากโค้ดจริง)

### Auth / JWT
- **JWT ของเรา** — `jwt.decode` ระบุ `algorithms` ชัด (ไม่มี `verify_signature: False` หลุดที่ไหน) ✅
- **Google OAuth** — verify แบบ ES256 + ดึง JWKS + match `kid` ถูกต้องตาม CLAUDE.md เป๊ะ · ไม่มี fallback ไป HS256/RS256 ✅
- **bcrypt rounds=12** ทั้ง register + login ✅
- **Timing-safe login** — user ไม่มีจริงก็ยัง `bcrypt.checkpw` กับ `_DUMMY_BCRYPT_HASH` เพื่อกัน user-enumeration ผ่านเวลาตอบ ✅ (ทำได้ดีมาก หาไม่ค่อยเจอใน MVP)
- **Rate limit** — `slowapi` มี · login `10/minute` · apply `20/minute` ✅

### SQL Injection — ผ่านทั้งหมด (ตรวจ 217 query)
มี f-string ใน query 5 จุด (1277, 1422, 2043, 3678, 3957) — **ตรวจทีละอันแล้ว ปลอดภัยทุกอัน:**
- ค่าที่ interpolate เป็น **`$1 $2 ${idx}` placeholder หรือ column name จาก whitelist** (`updates` dict ที่ key มาจากโค้ดเราเอง ไม่ใช่ user input)
- **ไม่มีจุดไหนเอา user value ต่อ string ตรงๆ** · value ทุกตัวไปทาง `*params` (parameterized)
- ✅ ปลอดภัย

### Authorization (IDOR) — ผ่าน
ตรวจ 18 endpoint ที่รับ id จาก path · **ทุกตัวมี ownership check:**
- ฝั่ง worker → `_get_app_for_worker()` มี `WHERE ja.worker_id = <ตัวเอง>`
- ฝั่ง employer → `_get_app_for_employer()` มี `WHERE jp.employer_id = <ตัวเอง>`
- 5 ตัวที่ scan อัตโนมัติ flag ว่า "ไม่เห็น user[sub]" — **ตรวจมือแล้วปลอดภัย** เพราะเช็คผ่าน helper `_get_app_for_*` (คนละชื่อตัวแปร) ⇒ false positive
- admin ทุกตัว (14 endpoint) ผ่าน `Depends(require_admin)` ✅

### Frontend XSS — ผ่าน (ตรวจ 64 จุด interpolate)
- กรองเหลือ user-content จริง 4 จุด → ตรวจมือทุกอัน:
  - `n.body` → **ผ่าน `esc()`** ✅
  - `_notifTranslateTitle` → **ผ่าน `esc()`** ทั้ง TH และ EN-fallback ✅
  - `maps_link` → backend สร้างเอง (`https://google.com/maps/...`) ไม่ใช่ user ป้อน ✅
  - `address_text` ใน `value="..."` → อยู่ใน attribute ของ input · เสี่ยงต่ำ (แต่ดูข้อ 6)
- `esc()` ใช้ **99 จุด** ทั่วไฟล์ ✅

### Upload — ผ่าน
- KYC + payment slip → เช็ค `content_type ∈ {jpeg,png,webp}` + `len > 5MB → reject` ✅
- Delete account → มี `Depends(get_current_user)` ✅

---

## 🔴 1. [สูง] GitHub token ยัง live + เคยโผล่ plaintext

```
git remote: https://nutthaphat-vdev:ghp_9Qiy…ePT2P@github.com/...
```
- ยัง valid · โผล่เต็มใน git config และใน session ที่ผ่านมา
- ใครเข้าถึง git config เครื่องได้ = push โค้ดใน repo ได้

**แก้:**
1. GitHub → revoke token `ghp_9Qiy…`
2. สร้างใหม่ ติ๊ก `repo` + `workflow`
3. `git remote set-url origin https://github.com/nutthaphat-vdev/We-re-Hire.git` (ไม่ฝัง token) + `git config credential.helper manager`

---

## 🟠 2. [กลาง] CORS มี `"null"` origin

`main.py:59` default:
```
cors_origins = "...localhost:5500,...,null"
```
`Origin: null` ส่งมาจาก `file://`, sandboxed iframe, บาง redirect ⇒ **attacker หลอกให้ browser ส่ง `Origin: null` ได้** · เมื่อ `allow_credentials=True` ยิ่งเสี่ยง

**แก้:** ถอด `null` ออกจาก default และจาก env var บน Render · ไม่ควรมีในโปรดักชัน
> เช็คว่า env var จริงบน Render มี `null` ไหมด้วย (default นี้อาจถูก override แล้ว)

---

## 🟠 3. [กลาง] admin secret เทียบแบบไม่ timing-safe

```python
if x_admin_secret != settings.admin_secret:   # ← == comparison
```
เทียบ string ด้วย `!=` รั่ว timing เล็กน้อย ⇒ ทฤษฎีเดา secret ทีละตัวอักษรได้ (ยากมากผ่าน network แต่แก้ง่าย)

**แก้:**
```python
import secrets
if not secrets.compare_digest(x_admin_secret, settings.admin_secret):
```

---

## 🟡 4. [ต่ำ] rate limit ครอบแค่ 2 endpoint

`login (10/min)` + `apply (20/min)` มีแล้ว · แต่ **register ไม่มี** ⇒ spam สมัครบัญชีได้ · endpoint upload (KYC/slip) ก็ไม่มี ⇒ ยิงไฟล์ 5MB รัวได้

**แก้ (ทำเรื่อยๆ):** เพิ่ม `@limiter.limit("5/minute")` ที่ register + upload endpoints

---

## 🟡 5. [ต่ำ] error เผย exception ดิบ

```python
raise HTTPException(401, detail=f"Token ไม่ถูกต้อง: {e}")
```
`{e}` ดิบอาจเผยโครงสร้างภายใน (library, path) · ควร log เต็มไว้ฝั่ง server แต่ตอบ client แบบ generic

**แก้:** `detail="Token ไม่ถูกต้อง"` เฉยๆ · ตัว `{e}` เก็บใน `logger.error` (ซึ่งทำอยู่แล้วบรรทัดก่อนหน้า — แค่เอาออกจาก detail)

---

## 🔵 6. [ข้อสังเกต] pattern ที่ต้องจำ ไม่ใช่บั๊ก

**`address_text` ใน `value="${...}"`** — ตอนนี้เสี่ยงต่ำเพราะ `esc()` แปลง `"` เป็น `&quot;` แล้ว (กัน attribute breakout ได้) · **แต่ถ้าวันหลังมีใครลืม `esc()` ใน value attribute = XSS ได้** ⇒ จดใน COUPLING_MAP ข้อ 9 ครอบแล้ว

---

## 📋 ลำดับที่แนะนำ

**ทำวันนี้/พรุ่งนี้ (ก่อน pilot):**
1. 🔴 revoke + rotate GitHub token
2. 🟠 ถอด `null` จาก CORS (Render env + default)
3. 🟠 `secrets.compare_digest` สำหรับ admin secret

**ทำเรื่อยๆ (ไม่ block pilot):**
4. rate limit register + upload
5. generic error message

**Phase 3 (ก่อนมีเงินจริง):**
- จ้าง pentest จริง — escrow/wallet เป็น attack surface ใหม่ที่ audit นี้ยังไม่ครอบ (ยังไม่มีโค้ด)
- idempotency key ทุก financial transaction (CLAUDE.md เขียนไว้แล้ว)

---

## เทียบกับ audit เดิม (26 พ.ค.)
โค้ดโตจาก 2,580 → 4,400 บรรทัด แต่ **ไม่มี regression ด้าน security** · ของใหม่ที่เพิ่มวันนี้ (checklist, multi-skill, avatar) ผ่าน esc ครบ · logger fix ไม่เปิดช่องอะไร · POLICY_VERSION refactor ปลอดภัย
