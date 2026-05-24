# WeHire — Claude Context & Knowledge Base
> คู่มือนี้เขียนโดย Claude Chat สำหรับ Claude Code
> อ่านทั้งหมดก่อนแตะ code ทุกครั้ง

---

## 🏗️ Project Overview

**WeHire** — แพลตฟอร์มจ้างงานรายวัน เชื่อมต่อ Worker ↔ Employer ในกรุงเทพฯ
- Founder: NUTTHAPHAT VICHITASUTANUN
- Stage: BKK MVP v0.1 — Production Live แล้ว

---

## 🌐 URLs & Infrastructure

| Service | URL |
|---------|-----|
| Frontend | https://divine-bar-29c7.vi-nutthaphat.workers.dev |
| Backend | https://web-production-03c5a.up.railway.app |
| GitHub | https://github.com/abc147258/We-re-Hire |
| Supabase | wexupoegrynxbhdzioym (ap-northeast-1 Tokyo) |

**Stack:**
- Backend: FastAPI + asyncpg + PyJWT + bcrypt + httpx
- Database: Supabase PostgreSQL + PostGIS
- Frontend: Vanilla JS Single HTML file
- Deploy: Railway (backend) + Cloudflare Workers (frontend)

---

## ⚠️ CRITICAL — อ่านก่อนแตะ code ทุกครั้ง

### 1. PgBouncer Fix — ห้ามลบออก!
```python
pool = await asyncpg.create_pool(
    settings.database_url,
    min_size=2,
    max_size=10,
    command_timeout=30,
    statement_cache_size=0,  # ❗ ห้ามลบ! Supabase ใช้ PgBouncer transaction mode
)
```
ถ้าลบออก → `DuplicatePreparedStatementError` ทั้งระบบพัง

### 2. Google OAuth — Supabase JWT ใช้ ES256 + JWKS เท่านั้น
```python
# ✅ ถูกต้อง — ES256 + JWKS + match kid
from jwt.algorithms import ECAlgorithm
async with httpx.AsyncClient() as client:
    r = await client.get(f"{supabase_url}/auth/v1/.well-known/jwks.json")
    jwks = r.json()
header = jwt.get_unverified_header(access_token)
for key in jwks["keys"]:
    if key["kid"] == header["kid"]:
        public_key = ECAlgorithm.from_jwk(key)
payload = jwt.decode(access_token, public_key, algorithms=["ES256"], options={"verify_aud": False})

# ❌ ห้ามทำ! Supabase ไม่ได้ใช้ HS256 หรือ RS256
jwt.decode(token, settings.supabase_jwt_secret, algorithms=["HS256"])  # จะ fail
jwt.decode(token, rsa_key, algorithms=["RS256"])                        # จะ fail

# ❌ ห้ามทำ! ช่องโหว่ระดับรูหนอนจักรวาล
options={"verify_signature": False}  # ใครก็ forge token ได้!
```

### 3. DATABASE_URL — Connection Pooler เท่านั้น
```
# ✅ ถูก — port 6543 = Transaction Pooler
postgresql://postgres.wexupoegrynxbhdzioym:PASSWORD@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres

# ❌ ผิด — port 5432 = Direct Connection (ไม่มี PgBouncer)
postgresql://...supabase.com:5432/postgres
```

### 4. Decimal vs Float — matching engine
```python
# ✅ ถูก
ratio = float(worker_rate) / float(job_rate)

# ❌ ผิด — TypeError: decimal.Decimal / float
ratio = worker_rate / job_rate
```

---

## 📁 File Structure

```
We-re-Hire/
├── main.py              # FastAPI backend — 39+ endpoints
├── requirements.txt     # Python deps (มี httpx, PyJWT[crypto])
├── Procfile             # web: uvicorn main:app --host 0.0.0.0 --port $PORT
├── index.html           # Single-file frontend (Vanilla JS)
├── CLAUDE.md            # ไฟล์นี้
└── PROGRESS.md          # Roadmap และสิ่งที่ทำแล้ว
```

---

## 🗄️ Database Schema (สำคัญ)

```sql
users                    -- auth core
worker_profiles          -- skills[], location GEOGRAPHY, daily_rate_expected DECIMAL
employer_profiles        -- company_name, business_type
job_postings             -- location GEOGRAPHY(POINT,4326), required_skills TEXT[]
job_applications         -- match_score, distance_km, matched_skills TEXT[]
reviews                  -- blind review system
review_tags              -- tag definitions
worker_review_summary    -- denormalized cache
employer_review_summary
notifications
job_categories           -- 4 หมวด
job_titles               -- 16 ตำแหน่ง
zones                    -- 7 zones (ต้องเพิ่มเป็น 50 เขต + ปริมณฑล)
user_reports
user_blocks
```

**Migrations ที่ run แล้ว:**
- supabase_setup_full.sql
- 003_review_system.sql
- 004_review_star_rating.sql
- 005_job_categories.sql
- 006_trust_safety.sql

---

## 🎯 Matching Algorithm

```python
# Scoring weights (main.py)
W_SKILLS   = 0.60   # skill overlap
W_DISTANCE = 0.25   # linear decay จาก radius
W_RATE     = 0.15   # worker_rate vs job_rate

# GPS query ใช้ PostGIS ST_DWithin — ไม่ใช่ Haversine
```

---

## 🔐 Auth Flow

```
Email/Password:
  POST /auth/register → bcrypt hash → JWT ของเรา

Google OAuth:
  GET /auth/google/url → Supabase OAuth URL
  [user login กับ Google]
  Supabase redirect → Frontend ได้ access_token
  POST /auth/google/callback → verify JWKS → JWT ของเรา
```

**JWT ของเรา** (ไม่ใช่ Supabase token):
```python
payload = {"sub": user_id, "role": "worker"|"employer", "exp": ...}
```

---

## 🔄 Job Lifecycle Flow

```
hired → checked_in → working → completed → verified → (review)
                                        ↘ disputed (< 90% ทุก 2 ชม.)
```

| Step | ใคร | Endpoint | Condition |
|------|-----|----------|-----------|
| hired | Employer | PATCH /applications/{id}/decide | slot available |
| checked_in | Worker | POST /applications/{id}/checkin | GPS ≤ 150m (PostGIS) |
| working | Employer | POST /applications/{id}/start | ±30 นาที จาก work_start |
| completed | Worker | POST /applications/{id}/complete | status = working |
| verified | Employer | POST /applications/{id}/verify | status = completed |

**Auto-verify (Cron ทุก 30 นาที):**
- `work_ended_at IS NOT NULL` AND employer ไม่กด verify ภายใน 2 ชม.
- AND `actual_duration ≥ 90%` ของ expected shift → auto verify + notify ทั้งคู่ → trigger review
- `< 90%` AND ไม่มีการกระทำใน 2 ชม. → status = `disputed` → admin ตัดสิน

**Dispute Flow (< 90% duration — Phase 3 full implementation):**
```
Worker กด complete (ชม. ไม่ครบ 90%)
→ notify Employer ทันที: "งานอาจไม่ครบ กรุณาตรวจสอบ"
→ Employer มี 2 ชม. ตัดสิน:
   ✅ กด verify ปกติ → จ่ายเต็ม (Employer ยอมรับ)
   ⚠️  กด dispute → ส่ง admin พร้อม evidence
→ ถ้าไม่กดอะไรใน 2 ชม. → auto escalate admin (status = disputed)
→ Admin เห็น evidence ทั้งสองฝั่ง → ตัดสิน ratio
```
⚠️ **MVP Current**: cron auto-disputed ตาม 2 ชม. อย่างเดียว (ยังไม่มี employer dispute button)
ปุ่ม "Dispute" ฝั่ง Employer + endpoint `POST /applications/{id}/dispute` → TODO Phase 3

**GPS Checkin:**
- Radius: 150 เมตร (ใช้ PostGIS ST_Distance — ไม่มี cost เพิ่ม)
- Worker ส่ง lat/lng จาก `navigator.geolocation`
- เกิน 150m → 400 error พร้อมบอก distance จริง
- GPS Spoofing: ยอมรับ risk ใน MVP → Phase ถัดไปเพิ่ม Selfie checkin

**Work Hours:**
- `work_start`, `work_end` อยู่ใน `job_postings` (TIME column)
- asyncpg ต้องการ `datetime.time` object ไม่ใช่ string — ต้อง `time_type.fromisoformat()` ก่อน INSERT
- Max 8 ชม./วัน (enforce ทั้ง frontend + backend)
- OT แยก: `ot_rate` (฿/ชม.)

---

## 💰 Phase 3 — Escrow & Pro-rata Settlement

> ยังไม่ implement — เป็น moat หลักของ WeHire

**Pro-rata สูตร (เมื่อ Dispute):**
```
total_locked      = ค่าจ้างทั้งหมดที่ lock ไว้
actual_work_ratio = เวลาจริง / เวลาที่ตกลง  (เช่น 0.70)

worker_gross         = total_locked × ratio           (420)
platform_penalty_fee = worker_gross × 10%             (42)   ← penalty สำหรับ worker ทำไม่ครบ
worker_payout_net    = worker_gross - platform_penalty (378)
employer_refund_net  = total_locked × (1 - ratio)     (180)

✅ Balance: worker_payout_net + employer_refund_net + platform_fee = total_locked
```

**Edge cases:**
- ratio = 1.0 → Worker ได้เต็ม, employer คืน 0, platform_fee = 0
- ratio = 0.0 → Worker ได้ 0, employer คืนเต็ม, platform_fee = 0
- Worker ออกเพราะ employer (สั่งหยุด/อันตราย) → admin กำหนด ratio = 1.0

**Tables ที่ต้องสร้าง (Phase 3):**
```sql
escrow_locks        -- amount, status, worker_pct, settled_by, admin_note
wallets             -- available, locked per user
wallet_transactions -- audit log ทุก movement
```

---

## 🪪 KYC System (Phase 2 — Level 1 Free)

> Manual admin verify — ฟรี 100% ใช้ Supabase Storage

**Flow:** Worker upload รูปบัตรประชาชน (หน้า-หลัง) + Selfie คู่บัตร → Admin กด Approve/Reject

**Migration (ยังไม่รัน — ใช้ชื่อ 010_kyc.sql เพราะ 009 ถูก disputed_status ใช้แล้ว):**
```sql
ALTER TABLE worker_profiles
  ADD COLUMN IF NOT EXISTS id_card_front_url TEXT,
  ADD COLUMN IF NOT EXISTS id_card_back_url  TEXT,
  ADD COLUMN IF NOT EXISTS selfie_url        TEXT,
  ADD COLUMN IF NOT EXISTS kyc_submitted_at  TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS kyc_reviewed_by   UUID REFERENCES users(id),
  ADD COLUMN IF NOT EXISTS kyc_note          TEXT;
```
- `background_check_status` ที่มีอยู่แล้วใช้ได้เลย
- Scale ได้ถึง ~1,000 workers โดยไม่มีปัญหา
- ถ้า volume เกิน → upgrade iDenfy (~$0.5/verification)

---

## 🚫 Pitfalls ที่เคยเจอ — ห้ามทำซ้ำ

| ปัญหา | สาเหตุ | วิธีแก้ |
|-------|--------|---------|
| Circuit Breaker | retry DB password ผิดซ้ำๆ | รอ 5-10 นาที + แก้ password |
| CORS error | Cloudflare URL ไม่อยู่ใน CORS_ORIGINS | เพิ่มใน Railway Variables |
| uvicorn not found | requirements.txt ถูก Cloudflare install | ใช้ NIXPACKS_INSTALL_CMD |
| Dropdown ว่าง | initCategoryDropdowns() ก่อน form render | เรียกอีกครั้งหลัง form render |
| Railway URL เปลี่ยน | redeploy บางครั้งเปลี่ยน subdomain | เช็ค Railway dashboard ทุกครั้ง |

---

## 🌍 Railway Environment Variables

```
DATABASE_URL        = postgresql://postgres.wexupoegrynxbhdzioym:...
JWT_SECRET          = (random string ยาวๆ)
JWT_ALGORITHM       = HS256
JWT_EXPIRE_MINUTES  = 1440
CORS_ORIGINS        = http://localhost:5500,...,https://divine-bar-29c7.vi-nutthaphat.workers.dev
SUPABASE_URL        = https://wexupoegrynxbhdzioym.supabase.co
SUPABASE_JWT_SECRET = (Legacy JWT Secret จาก Supabase)
FRONTEND_URL        = https://divine-bar-29c7.vi-nutthaphat.workers.dev
NIXPACKS_INSTALL_CMD= pip install -r requirements.txt
```

---

## 📋 TODO ที่ต้องทำต่อ

### ด่วน (ก่อน Pitch)
- [x] ตั้ง `ADMIN_SECRET` ใน Railway env vars ✅ 2026-05-23
- [x] เพิ่ม zones กรุงเทพ 50 เขต + ปริมณฑล (INSERT ใน Supabase) ✅ 2026-05-23
- [x] Run migration 004_review_star_rating.sql ✅ 2026-05-23
- [x] Run migration 008_job_lifecycle.sql ✅ 2026-05-23
- [x] Run migration 009_disputed_status.sql ✅ 2026-05-23
- [x] Google OAuth Consent Screen → Published ✅ 2026-05-23
- [x] Restrict Google Maps API Key ให้ใช้แค่ domain We're Hired ✅ 2026-05-23
- [ ] หน้า Notifications UI
- [x] Upload index.html → Cloudflare Workers ✅ 2026-05-23
- [x] ตั้ง wrangler CLI สำหรับ Cloudflare auto-deploy ✅ 2026-05-24

### Phase 3 — Wallet & Payment
- [ ] Escrow system
- [ ] PromptPay integration
- [ ] Worker withdrawal

### Phase 5 — Growth
- [ ] Mobile App (React Native)
- [ ] ขยายนอก BKK

---

## 💡 Key Business Logic ที่ต้องเข้าใจ

**Contact Lock** — เบอร์โทรเปิดเผยเฉพาะคู่ที่ `hired` เท่านั้น
→ ป้องกัน employer โทรตรง bypass แอพ

**Blind Review** — review ซ่อนจนกว่าทั้งคู่ส่ง หรือครบ 7 วัน
→ ป้องกัน bias จากการรู้ review ฝั่งตรงข้ามก่อน

**Wallet Escrow (Phase 3)** — เงินอยู่ในแอพ → ไม่มีใครอยากออกนอกระบบ
→ นี่คือ moat ที่แท้จริงของ WeHire

---

## 🤝 Working Style กับ Founder

- พูดตรงๆ เป็นกันเอง เหมือน Senior Dev คู่หู
- ถ้าจะแก้อะไร **บอกเหตุผลก่อนเสมอ**
- Security และ Cost-optimization ต้องคิดทุกครั้ง
- ถ้าไม่แน่ใจ **ถามก่อน อย่า assume**
- Founder ชื่อ **พี่** — เรียกแบบนี้เสมอ

