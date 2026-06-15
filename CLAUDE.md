# WeHire — Claude Context & Knowledge Base
> คู่มือนี้เขียนโดย Claude Chat สำหรับ Claude Code
> อ่านทั้งหมดก่อนแตะ code ทุกครั้ง

---

## 🔌 Cowork Connectors & Tools (อัปเดต 2 มิ.ย. 2568)

> เครื่องมือที่ใช้งานได้ใน Cowork session — บอก Claude ให้ใช้ให้ถูก tool

| Tool | ใช้ทำอะไร |
|------|-----------|
| `mcp__wehire-fs__*` | อ่าน/เขียนไฟล์ใน `C:\Users\User\Downloads\Hire` โดยตรง |
| `mcp__shell__run_command` | รัน shell command บนเครื่อง Windows (git, powershell ฯลฯ) |
| `mcp__workspace__bash` | bash ใน Linux sandbox (สำหรับ Python, grep, file processing) |
| `mcp__54bf20c7-...__*` | Canva MCP — อ่าน/แก้ไข/บันทึก Canva designs |
| `mcp__computer-use__*` | ควบคุม desktop (screenshot, click, type) |
| `mcp__Claude_in_Chrome__*` | ควบคุม Chrome browser — navigate, click, read page (ใช้แทน computer-use สำหรับ web) |

**หลักการเลือก tool:**
1. แก้ไฟล์ใน Hire folder → `mcp__wehire-fs__edit_file` หรือ `Edit` tool
2. รัน git / powershell → `mcp__shell__run_command`
3. Python script / bash → `mcp__workspace__bash`
4. เปิด/อ่านเว็บ → `mcp__Claude_in_Chrome__*` ก่อนเสมอ (เร็วกว่า computer-use)
5. native desktop app → `mcp__computer-use__*`
6. Canva deck → `mcp__54bf20c7-...__*`

---

## 🏗️ Project Overview

**WeHire** — แพลตฟอร์มจ้างงานรายวัน เชื่อมต่อ Worker ↔ Employer ในกรุงเทพฯ
- Founder: NUTTHAPHAT VICHITASUTANUN
- Stage: BKK MVP v0.1 — Production Live แล้ว

---

## 🌐 URLs & Infrastructure

| Service | URL |
|---------|-----|
| Frontend | https://wearehiredmvp.vi-nutthaphat.workers.dev |
| Backend | https://web-production-1db39.up.railway.app |
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
- 007_work_hours.sql
- 008_job_lifecycle.sql
- 009_disputed_status.sql
- 010_kyc.sql (nationality_type, KYC document columns, index on background_check_status)
- 011_job_categories_expanded.sql (เพิ่ม factory/event/interpreter/caregiver + is_special column)

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

**Flow:** Worker upload รูปโปรไฟล์ + บัตรประชาชน (หน้า-หลัง) + Selfie คู่บัตร → Admin กด Approve/Reject

**Migration: 010_kyc.sql ✅ run แล้ว**

รองรับทั้งคนไทยและต่างด้าว:
- `thai`: บัตรประชาชน (หน้า-หลัง) + Selfie
- `foreign`: Passport + Work Permit + Selfie

```sql
-- nationality_type: 'thai' | 'foreign'
ALTER TABLE worker_profiles
  ADD COLUMN IF NOT EXISTS nationality_type    VARCHAR(10) NOT NULL DEFAULT 'thai',
  ADD COLUMN IF NOT EXISTS profile_photo_url   TEXT,
  ADD COLUMN IF NOT EXISTS id_card_front_url   TEXT,   -- Thai only
  ADD COLUMN IF NOT EXISTS id_card_back_url    TEXT,   -- Thai only
  ADD COLUMN IF NOT EXISTS passport_url        TEXT,   -- Foreign only
  ADD COLUMN IF NOT EXISTS work_permit_url     TEXT,   -- Foreign only
  ADD COLUMN IF NOT EXISTS work_permit_expiry  DATE,   -- Foreign only
  ADD COLUMN IF NOT EXISTS selfie_url          TEXT,
  ADD COLUMN IF NOT EXISTS kyc_submitted_at    TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS kyc_reviewed_at     TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS kyc_reviewed_by     UUID REFERENCES users(id),
  ADD COLUMN IF NOT EXISTS kyc_note            TEXT;
```
- `background_check_status` ที่มีอยู่แล้วใช้ได้เลย (values: none / pending / approved / rejected)
- Badge แสดงบน profile card: **✓ KYC Verified**
- Index บน `background_check_status = 'pending'` สำหรับ Admin dashboard
- Scale ได้ถึง ~1,000 workers โดยไม่มีปัญหา
- ถ้า volume เกิน → upgrade iDenfy (~$0.5/verification)

---

## 🏛️ NDID Integration (Phase 3.5)

> National Digital ID — ระบบยืนยันตัวตนแห่งชาติของ ธปท. (ธนาคารแห่งประเทศไทย)

**Worker Tier System:**
| Tier | วิธียืนยัน | Badge | สิทธิ์ |
|------|-----------|-------|--------|
| `Unverified` | — | ไม่มี | สมัครงานได้ ข้อมูลน้อย |
| `KYC` | บัตรประชาชน + Selfie (admin) | ✓ KYC Verified | สมัครงานได้ เพิ่มความน่าเชื่อถือ |
| `NDID` | ยืนยันผ่านแอพธนาคาร (รัฐ) | 🏛️ NDID Verified | สมัครงาน high-trust ได้ + ประวัติอาชญากรรมสะอาด |

**Flow:**
```
Worker กด "ยืนยันตัวตนระดับ NDID"
→ Redirect ไปแอพธนาคาร (กสิกร / SCB / กรุงไทย ฯลฯ)
→ ธนาคารดึงข้อมูลจากทะเบียนราษฎร์ + ประวัติอาชญากรรม
→ Callback พร้อม verified status + consent token
→ เก็บ ndid_verified_at + ndid_ref บน worker_profiles
→ Badge NDID Verified ปรากฏบน profile
```

**DB columns ที่ต้องเพิ่ม (migration 011_ndid.sql):**
```sql
ALTER TABLE worker_profiles
  ADD COLUMN IF NOT EXISTS ndid_verified_at  TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS ndid_ref          TEXT,
  ADD COLUMN IF NOT EXISTS criminal_check_passed BOOLEAN DEFAULT FALSE;
```

**Business value:**
- Employer กรองหา "NDID only" เมื่อต้องการงานที่ trust สูง (รปภ., เลี้ยงเด็ก, ดูแลผู้สูงอายุ)
- ดึงประวัติอาชญากรรมจาก สำนักงานตำรวจแห่งชาติ ผ่าน NDID โดยตรง — ไม่ต้องรอ manual
- Moat สำคัญ: platform ทั่วไปทำไม่ได้ เพราะต้องเป็น NDID Member

---

## 🔄 Production URL Change Checklist

> ทุกครั้งที่เปลี่ยน Frontend URL ต้องแก้ครบทุกจุด — ลืมจุดไหนจุดหนึ่ง OAuth พัง

### 1. Cloudflare Dashboard
- Workers & Pages → เลือก Worker → Settings → Rename worker

### 2. wrangler.toml
```toml
name = "ชื่อใหม่"
```
→ git commit + push → GitHub Actions deploy อัตโนมัติ

### 3. Google Cloud Console ⚠️ (รอ 5–30 นาที หลัง save)
- APIs & Services → Credentials → OAuth 2.0 Client ID
- **Authorized redirect URIs** → เพิ่ม URL ใหม่
  ```
  https://[new-url]/index.html
  https://[new-url]/**
  ```

### 4. Supabase Dashboard ← สำคัญมาก มักลืม!
- Authentication → URL Configuration
- **Site URL** → เปลี่ยนเป็น URL ใหม่
- **Redirect URLs** → เพิ่ม `https://[new-url]/**`

### 5. Railway Environment Variables
```
FRONTEND_URL  = https://[new-url]
CORS_ORIGINS  = ...,https://[old-url],https://[new-url]   ← เพิ่ม อย่าลบเก่า
```
→ Save → Railway redeploy อัตโนมัติ

### 6. main.py
- ตรวจว่าไม่มี URL hardcode
- OAuth callback ใช้ `settings.frontend_url` เสมอ
- CORS อ่านจาก `settings.cors_origins` + `settings.frontend_url`

### 7. Verify ด้วย curl
```bash
curl -I -X OPTIONS "https://web-production-1db39.up.railway.app/auth/google/url" \
  -H "Origin: https://[new-url]" \
  -H "Access-Control-Request-Method: GET"
```
✅ ต้องเห็น `Access-Control-Allow-Origin: https://[new-url]`  
❌ ถ้าเห็น `400 Bad Request` → Railway env var ยังไม่ได้ update หรือยังไม่ redeploy

### 8. Railway Source Repo ← มักลืม!
- Railway → Project → Settings → **Source**
- ตรวจว่า repo ชี้ถูก account ไหม
- ถ้าเปลี่ยน GitHub account → disconnect แล้ว reconnect ใหม่
- ถ้าไม่แก้ → Railway ไม่ได้รับ webhook → ไม่ redeploy!

> **Note:** GitHub redirect repo เก่าให้อัตโนมัติ เลยดูเหมือนทำงานได้ แต่จริงๆ Railway ไม่ได้รับ push webhook จาก repo ใหม่

> **Note:** Phase 3 → React Native จะจัดการ env var ได้ง่ายกว่า ไม่ต้องแก้ทีละจุดแบบนี้

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
CORS_ORIGINS        = http://localhost:5500,...,https://wearehiredmvp.vi-nutthaphat.workers.dev
SUPABASE_URL        = https://wexupoegrynxbhdzioym.supabase.co
SUPABASE_JWT_SECRET = (Legacy JWT Secret จาก Supabase)
FRONTEND_URL        = https://wearehiredmvp.vi-nutthaphat.workers.dev
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
- [x] หน้า Notifications UI ✅ 2026-05-24
- [x] Upload index.html → Cloudflare Workers ✅ 2026-05-23
- [x] ตั้ง wrangler CLI สำหรับ Cloudflare auto-deploy ✅ 2026-05-24

### Phase 3 — Wallet & Payment + Mobile App
- [ ] Escrow system
- [ ] PromptPay integration
- [ ] Worker withdrawal
- [ ] React Native Mobile App (Expo) — พัฒนาคู่กัน

### Phase 5 — Growth
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

## 👻 Active Anti-Ghosting System (Phase 2 — ✅ Live)

> ป้องกัน worker hired แล้วหายตัวไป — auto-detect + backup workflow

**Migration: 012_anti_ghosting.sql ✅ run แล้ว**

```sql
ALTER TABLE job_applications
  ADD COLUMN IF NOT EXISTS noshow_marked_at    TIMESTAMPTZ,  -- เมื่อถูก mark no-show
  ADD COLUMN IF NOT EXISTS noshow_alerted_at   TIMESTAMPTZ,  -- cron alert ครั้งแรก (กัน spam)
  ADD COLUMN IF NOT EXISTS backup_priority     INTEGER,      -- 1,2,3 = ลำดับ backup
  ADD COLUMN IF NOT EXISTS backup_offered_at   TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS backup_accepted_at  TIMESTAMPTZ;
-- status เพิ่ม: 'no_show' (ใน CHECK constraint)
```

**Endpoints:**
| Endpoint | ใคร | Logic |
|----------|-----|-------|
| `GET /jobs/{id}/backup-workers` | Employer | top 10 applied/shortlisted ranked by match_score |
| `POST /applications/{id}/send-backup` | Employer | mark backup_priority + แจ้ง worker ด่วน |
| `POST /applications/{id}/accept-backup` | Worker | → `hired` + slot filled + Google Maps link |
| `PATCH /applications/{id}/mark-noshow` | Employer | → `no_show` + slot freed + แจ้ง worker |

**Cron Jobs (APScheduler):**
```
check_noshow_workers — ทุก 5 นาที:
  +30 นาที หลัง work_start → alert employer (noshow_alerted_at IS NULL)
  +60 นาที หลัง work_start → auto no_show + free slot + notify ทั้งคู่

send_d1_reminders — 11:00 UTC = 18:00 Bangkok ทุกวัน:
  หา status='hired' + start_date = พรุ่งนี้ → push แจ้ง worker ทุกคน
```

**No-Show Flow:**
```
Worker hired แต่ไม่เช็คอิน
→ +30 min: alert employer "Worker ยังไม่เช็คอิน"
→ +60 min: auto no_show → slot_filled - 1 → employer เห็น backup list
→ Employer กด send-backup ไป top candidate
→ Worker รับ backup offer → hired ทันที (มี Maps link)
```

---

## 🧮 Behavioral Score System (Design — Phase 2.5)

> วัดความน่าเชื่อถือของ worker จากพฤติกรรมจริง ไม่ใช่แค่ review

**Score Components (เก็บไว้ใน `worker_profiles`):**
```sql
ALTER TABLE worker_profiles
  ADD COLUMN IF NOT EXISTS reliability_score   DECIMAL(4,2),  -- 0.00–10.00 (computed)
  ADD COLUMN IF NOT EXISTS jobs_completed      INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS jobs_noshow         INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS jobs_hired          INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS score_updated_at    TIMESTAMPTZ;
```

**สูตรคำนวณ:**
```
completion_rate = jobs_completed / MAX(jobs_hired, 1)        -- 0.0–1.0
noshow_rate     = jobs_noshow    / MAX(jobs_hired, 1)        -- 0.0–1.0
review_avg      = (ค่าเฉลี่ยดาวจาก worker_review_summary) / 5.0

reliability_score =
  (completion_rate × 5.0) +
  ((1 - noshow_rate) × 3.0) +
  (review_avg × 2.0)
  → MAX: 10.00 | MIN: 0.00
```

**เมื่อใดให้ update score:**
- เมื่อ status → `verified` → jobs_completed + 1
- เมื่อ status → `no_show`  → jobs_noshow + 1
- เมื่อ `decided_at` SET (hired) → jobs_hired + 1
- หลัง submit review → recompute review_avg

**Badge ตาม score:**
| Score | Badge |
|-------|-------|
| ≥ 9.0 | 🌟 Top Worker |
| ≥ 7.0 | ✅ Reliable |
| ≥ 5.0 | — (ไม่มี badge) |
| < 5.0 | ⚠️ (แสดงเฉพาะ admin) |

**Migration ที่ต้องสร้าง: `013_behavioral_score.sql`**

---

## 🪪 KYC Foreign Worker — Detail Spec

> รองรับแรงงานต่างด้าว (Myanmar, Lao, Cambodian) ซึ่งต้องใช้เอกสารต่างจากคนไทย

**nationality_type routing:**
```
'thai'   → id_card_front_url + id_card_back_url + selfie_url
'foreign' → passport_url + work_permit_url + work_permit_expiry + selfie_url
```

**Work Permit Expiry Alert:**
- Cron (รายวัน) เช็ค `work_permit_expiry - NOW() < 30 วัน`
- แจ้ง worker: "Work Permit ของคุณใกล้หมดอายุ กรุณาอัปเดตเอกสาร"
- ถ้า expired → `background_check_status` → `rejected` อัตโนมัติ
- Migration: เพิ่มใน `send_d1_reminders` หรือ cron ใหม่แยก

**Flow หลัง Upload:**
```
Worker upload เอกสาร → background_check_status: none → pending
Admin เปิดดูใน Supabase Storage → กด Approve/Reject
  Approve → background_check_status: approved + kyc_reviewed_at + kyc_reviewed_by
  Reject  → background_check_status: rejected + kyc_note (เหตุผล)
→ Notify worker ทันที
```

**Storage Path แนะนำ (Supabase Storage):**
```
kyc/{user_id}/profile_photo.jpg
kyc/{user_id}/id_card_front.jpg   (Thai)
kyc/{user_id}/id_card_back.jpg    (Thai)
kyc/{user_id}/passport.jpg        (Foreign)
kyc/{user_id}/work_permit.jpg     (Foreign)
kyc/{user_id}/selfie.jpg
```

---

## 💰 Pro-rata Settlement v2 (Phase 3 — Escrow)

> สูตรสุดท้ายที่ balance เสมอ — ไม่มีเงินรั่วไหล

**สูตรคำนวณ:**
```
total_locked         = 600 บาท
actual_work_ratio    = 0.70

worker_gross         = total_locked × ratio            = 420
platform_penalty_fee = worker_gross × 10%              = 42   ← penalty ทำงานไม่ครบ
worker_payout_net    = worker_gross - platform_penalty  = 378
employer_refund_net  = total_locked × (1 - ratio)      = 180

✅ Balance: 378 + 180 + 42 = 600
```

**Fields ที่ต้องเพิ่มใน `escrow_locks`:**
```sql
ALTER TABLE escrow_locks
  ADD COLUMN IF NOT EXISTS actual_work_ratio    DECIMAL(5,4),  -- 0.7000
  ADD COLUMN IF NOT EXISTS worker_payout_net    DECIMAL(10,2), -- 378
  ADD COLUMN IF NOT EXISTS employer_refund_net  DECIMAL(10,2), -- 180
  ADD COLUMN IF NOT EXISTS platform_penalty_fee DECIMAL(10,2); -- 42
```

**Edge cases สำคัญ:**
- `ratio = 1.0` → Worker ได้เต็ม, platform_fee = 0, employer คืน 0
- `ratio = 0.0` → Worker ได้ 0, employer คืนเต็ม, platform_fee = 0
- Worker ออกเพราะ employer (สั่งหยุด/อันตราย) → admin set `ratio = 1.0`
- `ratio > 1.0` → reject ทันที (validation)
- Double settlement → เช็ค `status = 'disputed'` ก่อนทุกครั้ง
- Balance check: ต้อง pass `worker_payout_net + employer_refund_net + platform_penalty_fee = total_locked` ก่อน execute transaction

**Admin Settlement Flow (atomic):**
```
Admin กรอก actual_work_ratio → validate → คำนวณ 3 amounts
→ atomic transaction:
  1. Worker wallet available  += worker_payout_net
  2. Employer wallet available += employer_refund_net
  3. Platform wallet           += platform_penalty_fee
→ escrow status = 'settled_by_admin'
→ log: admin_id, timestamp, ratio, amounts
→ notify worker + employer พร้อมรายละเอียดตัวเลข
```

---

## 🗂️ Job Categories Expansion (Phase 2 — ✅ Live)

> Migration 011_job_categories_expanded.sql — 8 categories, 32+ titles

**`is_special` column:**
```sql
ALTER TABLE job_categories
  ADD COLUMN IF NOT EXISTS is_special BOOLEAN NOT NULL DEFAULT FALSE;
```
- `is_special = TRUE` → ต้องการ NDID verification (Phase 3.5)
- ปัจจุบันมีเฉพาะ `caregiver` category

**Categories ทั้งหมด (8 หมวด):**
| code | ชื่อ | Icon | is_special |
|------|------|------|------------|
| warehouse | โกดังและโลจิสติกส์ | 📦 | FALSE |
| fnb | อาหารและเครื่องดื่ม | 🍜 | FALSE |
| maintenance | ช่างและซ่อมบำรุง | 🔧 | FALSE |
| cleaning | ทำความสะอาด | 🧹 | FALSE |
| factory | โรงงานและการผลิต | 🏭 | FALSE |
| event | งาน Event และ Seasonal | 🎪 | FALSE |
| interpreter | ล่ามภาษา | 🗣️ | FALSE |
| caregiver | งานดูแลบุคคล | ⚠️ | **TRUE** |

**Titles ที่เพิ่ม (24 titles ใหม่):** welder, machinist, machine_repair, qc_inspector, line_supervisor, packer_factory, delivery_driver, receiving_clerk, cashier, store_crew, general_repair, tile_worker, event_staff, pretty_mc, fair_sales, data_entry_temp, event_photo, interp_th_my, interp_th_la, interp_th_kh, interp_th_en, elderly_care, temp_nanny, patient_assist

---

## 🛡️ Admin Team Plan

> ปัจจุบัน: single admin via `X-Admin-Secret` header — เพียงพอสำหรับ MVP
> Phase 3+: multi-admin roles

**Admin Capabilities ปัจจุบัน:**
```python
# ทุก admin endpoint ต้องส่ง header:
# X-Admin-Secret: {settings.admin_secret}

POST   /admin/workers/{id}/verify      # approve/reject KYC
POST   /admin/employers/{id}/verify    # approve employer
GET    /debug/trigger-cron             # manual trigger auto-verify
```

**Admin Capabilities ที่ต้องเพิ่ม (Phase 3):**
```
GET  /admin/kyc/pending          # ดูรายการ KYC รอ approve
POST /admin/kyc/{id}/decide      # approve/reject พร้อม note
GET  /admin/noshow               # รายการ no-show ทั้งหมด
GET  /admin/disputes             # รายการ disputed งาน
POST /admin/disputes/{id}/settle # ตัดสิน ratio + สั่ง escrow release
```

**Multi-Admin Design (Phase 3+):**
```sql
CREATE TABLE admin_users (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id    UUID REFERENCES users(id),
  role       VARCHAR(20) CHECK (role IN ('admin', 'super_admin')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
-- super_admin: settle disputes, ban users
-- admin: KYC verify, view reports only
```

**Security Notes:**
- `admin_secret` เก็บใน Railway env var — ไม่อยู่ใน code
- Production: เปลี่ยนเป็น admin JWT หลัง MVP
- Log ทุก admin action พร้อม timestamp + admin_id

---

## 📱 React Native — Phase 3

> ตัดสินใจ: พัฒนาคู่กับ Phase 3 (Wallet & Escrow) — ไม่รอ Phase 6

**ข้อดีที่ทำได้เลย:** Backend เป็น REST API ทั้งหมด — Mobile app เรียก endpoint เดิมได้ 100%

**Tech Stack:**
```
Framework : Expo (React Native) — build iOS + Android จาก codebase เดียว
State     : Zustand หรือ Context API
Navigation: React Navigation v6
HTTP      : fetch / axios
Maps      : react-native-maps (Google Maps SDK)
GPS       : expo-location
Camera    : expo-camera (KYC upload)
Storage   : expo-secure-store (JWT token)
Push      : expo-notifications (FCM/APNs)
```

**Features ที่ Priority สูงสุด:**
1. Auth (register/login/Google OAuth)
2. Worker: ค้นหางาน nearby + apply + checkin GPS
3. Employer: post job + ดู candidates + hire
4. Notifications (real-time via polling หรือ FCM)
5. KYC upload (camera → Supabase Storage)
6. Wallet (Phase 3)

**API Compatibility:**
- ทุก endpoint ใช้ได้เลย — ไม่ต้องแก้ backend
- GPS checkin: `expo-location` → ส่ง lat/lng ไป `POST /applications/{id}/checkin`
- D-1 reminder: backend ส่ง notification แล้ว — mobile รับผ่าน FCM

**Environment:**
```
API_URL = https://web-production-1db39.up.railway.app
(เหมือนกับ frontend ปัจจุบัน)
```

---

## 🤝 Working Style กับ Founder

- พูดตรงๆ เป็นกันเอง เหมือน Senior Dev คู่หู
- ถ้าจะแก้อะไร **บอกเหตุผลก่อนเสมอ**
- Security และ Cost-optimization ต้องคิดทุกครั้ง
- ถ้าไม่แน่ใจ **ถามก่อน อย่า assume**
- Founder ชื่อ **พี่** — เรียกแบบนี้เสมอ

---

## Proactive Code Quality

### ก่อน implement ทุกครั้ง
- คาดการณ์ edge cases ที่อาจเกิดขึ้น
- เช็ค type safety — asyncpg Decimal vs float เสมอ
- เช็ค null/None handling ทุก field
- เช็ค status transitions ว่า logic ถูกต้องไหม
- เช็ค foreign key constraints ก่อน INSERT/DELETE

### หลัง implement ทุกครั้ง
- ระบุ side effects ที่อาจเกิดจาก code นี้
- บอกพี่ว่ามี endpoint/function ไหนที่อาจได้รับผลกระทบ
- แนะนำ test case ที่ควรลองก่อน deploy
- ถ้าแก้ bug — เช็คว่ามี bug แบบเดียวกันซ่อนอยู่ที่อื่นไหม

### Red flags ต้องแจ้งพี่ทันที
- SQL ที่ไม่มี parameterized query
- JWT/auth logic ที่เปลี่ยน
- Migration ที่ DROP column หรือ ALTER type
- CORS หรือ security header ที่เปลี่ยน
- Cron job ที่อาจ overlap กัน
- Loop ที่อาจเกิด N+1 query

### Format การรายงานหลัง implement
✅ สิ่งที่ทำ
⚠️ สิ่งที่ต้องระวัง
🧪 Test case ที่แนะนำ
🔗 Endpoints/functions ที่อาจได้รับผลกระทบ

---

## Advanced Skills & Domain Knowledge

### Performance
- รู้จัก N+1 query และหลีกเลี่ยงเสมอ
- ใช้ EXPLAIN ANALYZE ก่อน query หนักๆ
- รู้ว่า index ไหนมีอยู่แล้วใน schema (ดู supabase_setup_full.sql)

### Migration Safety
- ห้าม DROP COLUMN โดยไม่แจ้งพี่ก่อน
- ทุก migration ต้องคิด rollback plan ไว้ด้วย
- ห้าม ALTER TYPE column ที่มีข้อมูลอยู่แล้ว

### Cron Job Awareness
- cron ที่รันอยู่: auto-verify (30m), noshow-check (5m), D-1 reminder (18:00 BKK)
- เช็ค overlap ก่อนเพิ่ม cron ใหม่ทุกครั้ง
- ระวัง race condition ระหว่าง cron jobs

### Payment Logic (Phase 3)
- Escrow state machine ต้อง atomic ทุกครั้ง
- ทุก financial transaction ต้องมี idempotency key
- ห้าม double-charge ไม่ว่ากรณีใดทั้งสิ้น
- Pro-rata calculation ต้องแม่นยำ — ใช้ Decimal ไม่ใช่ float

### React Native (Phase 3)
- ใช้ Expo — ไม่ใช่ bare React Native
- TypeScript strict mode — ห้ามใช้ `any`
- API ทุกตัวต้องผ่าน `/services/api.ts` เท่านั้น
- GPS ใช้ Expo Location
- Push notification ใช้ Expo Notifications


---

## 💼 Revenue Streams & Business Roadmap

> บันทึกจาก Investor Discussion — verified ข้อมูลจากกรมการจัดหางาน 2025

### Stream 1 — Matching Fee (✅ Live)
- **6% per transaction**, Gross Margin ~90%
- ตัวอย่าง: งาน 400 บาท/วัน → fee 24 บาท → margin ~21 บาท
- **Key Insight:** Daily wage = Rotation market — employer ต้องกลับมาใช้ platform เสมอ แม้จะจ้าง worker ตรงก็ตาม เพราะ worker ไม่ได้ว่างตลอด

### Stream 2 — Work Permit Service (Phase 2)
- **ราคาขาย: 10,000 บาท/คน** (ตลาดเรียก 12,000 บาท)
- **ต้นทุนจริง (verified กรมการจัดหางาน):**
  - ค่าธรรมเนียมรัฐ work permit: 900 บาท/ปี
  - ค่าธรรมเนียมยื่นคำขอ: 100 บาท/ฉบับ
  - รวมเอกสาร + วีซ่า: ~1,500–2,500 บาท/คน
- **Margin: ~7,500 บาท/คน**
- **Recurring:** ต่ออายุทุก 2 ปี
- **Moat:** employer ที่ทำ work permit ผ่าน WeHire = ไม่มีวัน bypass platform
- Target: แรงงานต่างด้าว เมียนมา ลาว กัมพูชา (MOU)
- ต้องการ: ใบอนุญาตนำคนต่างด้าวมาทำงาน (ตรวจสอบกับกรมการจัดหางานก่อน scale)

### Stream 3 — White Collar Job Board (Phase 3)
- Flat fee โพสต์งาน (ไม่ต้องใบอนุญาตพิเศษ)
- เจาะ SME / โรงงานที่ใช้ WeHire อยู่แล้ว — upsell ได้เลย
- ใช้ฐาน employer เดิม ไม่ต้อง CAC ใหม่

### Stream 4 — Premium Matching / Subscription (Phase 4)
- AI shortlist + subscription รายเดือน
- ใช้ data สะสมจาก Stream 1-3 มา train model
- Employer เห็น candidates ก่อน + filter advanced

### Stream 5 — Headhunter / HH (Phase 5)
- **ต้องมีก่อน:** ใบอนุญาตจัดหางานในประเทศ
  - ค่าธรรมเนียม: **5,000 บาท** (อายุ 2 ปี)
  - ค่ายื่นคำขอ: 100 บาท
  - ยื่นที่: กองทะเบียนจัดหางานกลาง กรมการจัดหางาน ดินแดง
- **Fee model:** 15–20% เงินเดือนเดือนแรก หรือ flat fee
- เริ่มได้เมื่อมี track record + employer trust

### Gross Margin เป้าหมาย
| Stream | Margin |
|--------|--------|
| Matching Fee | ~90% |
| Work Permit | ~75% |
| Job Board | ~85% |
| HH | ~70% |
| **รวม target** | **>80%** |

### Key Business Insight (จาก Investor)
> "จ้างยาวตรง = โอกาสขาย premium tier / direct hire fee ไม่ใช่ปัญหา"
- Platform Bypass ไม่ใช่ภัยคุกคามใน daily wage market เพราะ rotation เกิดขึ้นตามธรรมชาติ
- Work permit ผูก employer กับ platform แน่นกว่า contract ใดๆ
- Ladder model: ใช้ฐาน daily wage → upsell work permit → upsell white collar

