# We're Hired — Progress & Roadmap
> **"ทำงานวันนี้ เสร็จงานได้เงินทันที"**

อัปเดต: 25 พฤษภาคม 2568

---

## ✅ Production — Live แล้ว

### 🔧 Infrastructure
- [x] Supabase PostgreSQL + PostGIS setup
- [x] FastAPI + asyncpg connection pool (PgBouncer transaction mode)
- [x] JWT Auth middleware (HS256 — token ของเราเอง)
- [x] Google OAuth via Supabase — verify ด้วย JWKS + ES256
- [x] bcrypt password hashing (cost=12)
- [x] CORS configuration
- [x] Health check endpoint
- [x] Deploy: Railway (backend) + Cloudflare Workers (frontend)
- [x] GitHub Actions auto-deploy — push → Cloudflare อัตโนมัติ ✅ live

### 🔐 Auth
- [x] POST /auth/register (worker / employer)
- [x] POST /auth/login
- [x] GET /auth/me
- [x] GET /auth/google/url + POST /auth/google/callback
- [x] Google OAuth Consent Screen → Published

### 👷 Worker
- [x] GET/POST/PATCH /workers/profile/me (รองรับ nationality_type, work_permit_url, work_permit_expiry)
- [x] GET /workers/applications (พร้อม maps_link + contact เมื่อ hired)
- [x] ปุ่ม 🗺️ นำทางไปที่ทำงาน (เฉพาะ hired)
- [x] ปุ่ม 📞 ดูเบอร์ + email employer (เฉพาะ hired)
- [x] **Work Permit Enforcement** — POST /jobs/{id}/apply block ถ้า foreign worker ไม่มี work_permit หรือหมดอายุ (403)

### 🏭 Employer
- [x] GET/POST/PATCH /employers/profile/me
- [x] ปุ่ม 📞 ดูเบอร์ worker (เฉพาะ hired)

### 💼 Jobs
- [x] POST /jobs
- [x] GET /jobs/mine
- [x] PATCH /jobs/{id}/status (open / closed)
- [x] Job categories cascade dropdown (4 หมวด, 16 ตำแหน่ง)
- [x] GET /zones (50 เขตกรุงเทพ + ปริมณฑล)

### 🎯 Matching Engine
- [x] GET /jobs/nearby — PostGIS ST_DWithin radius filter (1–30km)
- [x] Skill filter แก้แล้ว — รองรับ worker ที่ไม่มี skills (cardinality fix)
- [x] POST /jobs/{id}/apply — match score: skills 60% / distance 25% / rate 15%
- [x] GET /jobs/{id}/candidates (ranked list)
- [x] PATCH /applications/{id}/decide (hired / rejected / shortlisted)
- [x] Auto Google Maps navigation link เมื่อ hired

### 🔒 Contact Reveal
- [x] GET /applications/{id}/contact
- [x] เปิดเผยเบอร์โทร + email เฉพาะคู่ที่ hired เท่านั้น (Contact Lock)

### 📋 Job Lifecycle
- [x] hired → checked_in → working → completed → verified / disputed
- [x] POST /applications/{id}/checkin — GPS ≤ 150m (PostGIS)
- [x] POST /applications/{id}/start — ±30 นาที จาก work_start
- [x] POST /applications/{id}/complete
- [x] POST /applications/{id}/verify
- [x] Auto-verify cron ทุก 30 นาที (≥ 90% duration → verified, < 90% → disputed)
- [x] Migrations: 007_work_hours, 008_job_lifecycle, 009_disputed_status ✅ run แล้ว

### 👻 Anti-Ghosting System
- [x] status `no_show` — worker hired แต่ไม่มา
- [x] GET /jobs/{id}/backup-workers — top 10 backup candidates (ranked by match score)
- [x] POST /applications/{id}/send-backup — employer ส่ง offer ด่วนไป backup worker
- [x] POST /applications/{id}/accept-backup — worker รับงานสำรอง → hired ทันที
- [x] PATCH /applications/{id}/mark-noshow — employer mark no-show → slot freed
- [x] Cron ทุก 5 นาที: alert +30 นาที, auto no_show +60 นาที หลัง work_start
- [x] Cron 18:00 ทุกวัน: D-1 reminder ไป hired workers ที่มีงานพรุ่งนี้
- [x] Migration: 012_anti_ghosting.sql ✅ run แล้ว

### ⭐ Review System
- [x] Blind review — ซ่อนจนทั้งคู่ส่ง หรือครบ 7 วัน
- [x] 1–5 ดาว + tag buttons
- [x] GET /review-tags, POST /reviews, GET /reviews/me, GET /reviews/pending
- [x] Migrations: 003_review_system, 004_review_star_rating ✅ run แล้ว

### 🛡️ Trust & Safety
- [x] POST /reports, POST /blocks
- [x] ปุ่ม 🚩 Report ใน frontend
- [x] Migration: 006_trust_safety ✅ run แล้ว

### 🔔 Notifications
- [x] Notification badge (unread count) ใน sidebar — poll ทุก 30 วิ
- [x] cache: no-store fix — ป้องกัน browser cache ทำให้ list ว่าง
- [x] หน้า Notifications list พร้อม filter ทั้งหมด / ยังไม่อ่าน
- [x] Smart date labels (วันนี้ / เมื่อวาน / full Thai date)
- [x] Type badges + icon ต่างกันตามประเภท
- [x] ปุ่มอ่านแล้ว ทีละอัน + อ่านทั้งหมด
- [x] Deep-link navigation — กดการ์ดแล้วไปหน้าที่เกี่ยวข้อง
  - hired / rejected / shortlisted → หน้าใบสมัคร
  - new_applicant → หน้างานของฉัน
  - review_pending → หน้ารีวิว
- [x] Auto-mark as read เมื่อกดการ์ดนำทาง

### 🌐 Frontend UX
- [x] **Multi-language UI (TH/MM/EN)** — lang toggle บน auth page + sidebar
- [x] ทุก worker-facing string ใช้ `t()` — login/register, หางานใกล้บ้าน, status badges, action buttons
- [x] Language preference เก็บใน localStorage (`wh_lang`)
- [x] **Work Permit section** บน worker profile — badge, link เอกสาร, คำเตือนใกล้หมดอายุ (< 30 วัน), error ถ้าหมดแล้ว
- [x] Nationality selector ใน edit profile form — ไทย / ต่างด้าว

### 🗄️ Database Migrations (run ครบแล้วทุกอัน)
| ไฟล์ | สถานะ |
|------|--------|
| supabase_setup_full.sql | ✅ |
| 003_review_system.sql | ✅ |
| 004_review_star_rating.sql | ✅ |
| 005_job_categories.sql | ✅ |
| 006_trust_safety.sql | ✅ |
| 007_work_hours.sql | ✅ |
| 008_job_lifecycle.sql | ✅ |
| 009_disputed_status.sql | ✅ |
| 010_kyc.sql | ✅ |
| 011_job_categories_expanded.sql | ✅ |
| 012_anti_ghosting.sql | ✅ |

---

## 🔧 ต้องทำต่อ (งาน Manual)

- [x] **GitHub Secrets** — `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID` ✅ 2026-05-24
- [x] **GitHub PAT** — scope `workflow` เพิ่มแล้ว, CI pipeline active ✅ 2026-05-24
- [ ] **Review summary** — ดาวเฉลี่ย + top tags แสดงบน profile card
- [ ] **Contact button reload** — ปุ่ม 📞 โผล่ทันทีหลังกด hired โดยไม่ต้อง refresh

---

## 📋 Roadmap

### Phase 2A — KYC Level 1 (Free) 🪪
> ยืนยันตัวตนด้วยบัตรประชาชน / Passport + Selfie — admin verify มือ, ฟรี 100%

**ทำแล้ว ✅**
- [x] Migration: 010_kyc.sql — 12 columns (nationality_type, kyc docs, review tracking)
- [x] Work Permit enforcement — block apply ถ้า foreign worker ไม่มีหรือหมดอายุ (403)
- [x] Work Permit section บน worker profile card + expiry warning < 30 วัน
- [x] Multi-language UI 🌐 TH/MM/EN — worker ต่างด้าวเข้าใจแอพได้ทันที

**ยังต้องทำ**
- [ ] Worker upload เอกสาร → Supabase Storage (endpoint `POST /workers/kyc/upload`)
- [ ] Admin `GET /admin/kyc/pending` + `POST /admin/kyc/{id}/decide` (approve/reject + note)
- [ ] Badge **✓ KYC Verified** แสดงบน profile card หลัง admin approve
- [ ] Cron รายวัน: Work Permit expiry alert + auto-reject ถ้า expired
- [ ] รูปโปรไฟล์ worker (Supabase Storage)
- [ ] Employer verification flow

### Phase 2B — Behavioral Score System 🧮
> วัดความน่าเชื่อถือ worker จากพฤติกรรมจริง — ไม่ใช่แค่ review

**ต้องการ Phase 2A (KYC) ก่อน**

**Score Components** (เก็บใน `worker_profiles`):
```
reliability_score = (completion_rate × 5.0) + ((1 - noshow_rate) × 3.0) + (review_avg × 2.0)
MAX: 10.00 | MIN: 0.00
```

| Signal | น้ำหนัก | อัปเดตเมื่อ |
|--------|---------|------------|
| Checkin ตรงเวลา / งาน verified ครบ | +5.0 | status → `verified` |
| ไม่ no-show | +3.0 (penalty ถ้า no-show) | status → `no_show` |
| Review ดาวเฉลี่ย | +2.0 | หลัง submit review |

**Badge ตาม score:**
| Score | Badge แสดงบน profile |
|-------|---------------------|
| ≥ 9.0 | 🌟 Top Worker |
| ≥ 7.0 | ✅ Reliable |
| ≥ 5.0 | — (ไม่มี badge) |
| < 5.0 | ⚠️ แสดงเฉพาะ admin |

- [ ] Migration: `013_behavioral_score.sql` (columns: reliability_score, jobs_completed, jobs_noshow, jobs_hired)
- [ ] Backend: คำนวณ + update score อัตโนมัติทุก lifecycle event
- [ ] Frontend: แสดง "ความน่าเชื่อถือ ⭐⭐⭐⭐☆" บน worker profile card
- [ ] Employer: filter ผู้สมัครตาม reliability_score ขั้นต่ำ

### Phase 3 — Wallet & Escrow 💰 + Mobile App 📱
> นี่คือ moat หลักของ We're Hired — ถ้าเงินอยู่ในแอพ ไม่มีใครอยากโทรตรง
- [ ] Wallet schema (wallets, escrow_locks, wallet_transactions)
- [ ] Employer deposit → lock เมื่อ hired
- [ ] Release อัตโนมัติเมื่อ verified
- [ ] Pro-rata payout เมื่อ disputed (worker_pct × ค่าจ้าง)
- [ ] Worker withdrawal request
- [ ] PromptPay / Omise / 2C2P integration
- [ ] Dispute button ฝั่ง Employer + POST /applications/{id}/dispute
- [ ] **Mobile App (React Native / Expo)** — พัฒนาคู่กับ Wallet
  - Auth, Nearby Jobs, GPS Checkin, KYC upload (camera), Notifications, Wallet

### Phase 3.5 — NDID Integration 🏛️
> ยืนยันตัวตนระดับรัฐ ผ่านแอพธนาคาร — ดึงประวัติจริงจากราชการ
- [ ] เชื่อมต่อ NDID API (National Digital ID — ธปท.)
- [ ] Worker ยืนยันตัวตนผ่านแอพธนาคาร (กสิกร / SCB / กรุงไทย ฯลฯ)
- [ ] ดึงประวัติอาชญากรรมจากระบบราชการอัตโนมัติ
- [ ] Badge **🏛️ NDID Verified** บน worker profile
- [ ] Worker Tier System:
  - `Unverified` — สมัครงานได้, ข้อมูลน้อย
  - `KYC` — บัตรประชาชน + Selfie ผ่าน admin
  - `NDID` — ยืนยันผ่านธนาคาร + ประวัติอาชญากรรมสะอาด

### Phase 4 — AI Integration 🤖
> ใช้ Claude API ลด overhead ของ admin + เพิ่มคุณภาพ matching

**Strategy: Haiku filter ก่อน → ซับซ้อนค่อยส่ง Sonnet**

| Use Case | Model | Input → Output |
|----------|-------|---------------|
| **Support Bot** | Haiku | คำถาม worker/employer → ตอบ FAQ, deep-link แอพ |
| **KYC Pre-filter** | Haiku | รูปบัตรประชาชน → ตรวจว่าอ่านออกหรือเปล่า, ก่อนส่ง admin |
| **Behavioral Classify** | Haiku | pattern การสมัคร/no-show → flag risk worker เร็ว |
| **Dispute Resolution** | Sonnet | evidence ทั้งสองฝั่ง → recommend ratio + เหตุผล |
| **Matching v2** | Sonnet | job desc (free text) → extract skills + match worker |
| **Fraud Detection** | Sonnet | pattern account → detect fake employer/worker |

- [ ] เชื่อมต่อ Anthropic API (claude-haiku-4-5, claude-sonnet-4-6)
- [ ] POST /support/chat — LINE OA bot backend
- [ ] POST /admin/kyc/precheck — Haiku pre-filter ก่อน admin queue
- [ ] POST /admin/disputes/{id}/ai-suggest — Sonnet recommend settlement ratio
- [ ] Matching v2: รองรับ job description แบบ free text (ไม่ต้อง select skill เท่านั้น)
- [ ] Cost guardrail: Haiku limit 1,000 tokens/req, Sonnet limit 2,000 tokens/req

### Phase 5 — Notifications & Communication
- [ ] Push notifications (LINE Notify หรือ Firebase FCM)
- [ ] Worker ↔ Employer in-app chat (เฉพาะหลัง hired)
- [ ] Email notification backup

### Phase 6 — Scale & Production
- [ ] Rate limiting (per IP / per user)
- [ ] Logging + monitoring (Sentry / Grafana)
- [ ] pg_cron: reveal reviews hourly, expire old jobs
- [ ] Custom domain + HTTPS
- [ ] Dockerize (Dockerfile + docker-compose)

### Phase 7 — Growth
- [ ] Landing page / Marketing site
- [ ] Job recommendation engine (ML-based)
- [ ] Worker availability calendar
- [ ] Multi-zone posting
- [ ] Referral system
- [ ] ขยายนอก BKK

---

## 🤝 KEY PARTNERS Strategy (Phase 2)

> เป้าหมาย: onboard employer กลุ่มใหญ่ที่ต้องการแรงงานรายวันต่อเนื่อง

| กลุ่ม | ตัวอย่าง | ความต้องการหลัก | วิธี approach |
|-------|---------|----------------|--------------|
| **โรงงาน** | นิคมอุตสาหกรรม ลาดกระบัง, บางปู, บางชัน | แรงงานสายพานและแพ็กสินค้า จำนวนมาก, ต้องการทุกวัน | Direct call ฝ่าย HR, นำเสนอ cost/worker ที่ต่ำกว่า agency |
| **โรงแรม** | Airbnb Host, Boutique Hotel, Budget Hotel | แม่บ้าน, ต้อนรับ, ครัว — ช่วง high season หรือแทนพนักงานลา | Line OA + Walk-in พื้นที่สุขุมวิท, สีลม, สาทร |
| **7-Eleven / ร้านสะดวกซื้อ** | 7-Eleven, FamilyMart, Lotus Express | Part-time กะดึก, fill-in เมื่อพนักงานขาด | เจรจาผ่าน CP Franchise head office ระดับเดียว |
| **ร้านอาหาร** | ร้าน SME, Chain, Food Court | ครัว, เสิร์ฟ, ล้างจาน — weekends + holidays | Facebook Group เจ้าของร้าน + Walk-in ตลาด, ห้าง |
| **ขนส่ง / โลจิสติกส์** | Lazada, Flash, Kerry hub | พนักงานคัดแยก, โหลดสินค้า — ช่วงเทศกาล | LinkedIn outreach ทีม Ops + Pitch deck นำเสนอ flexibility |

**KPI Phase 2 Partners:** 5 signed employers แต่ละกลุ่ม ภายใน 3 เดือน → รวม 25 employer partners

---

## 📣 CHANNELS

### Online
| ช่องทาง | Target | เนื้อหา | KPI |
|---------|--------|---------|-----|
| **Facebook** | Worker (18–40 ปี, กรุงเทพ+ปริมณฑล) | วิดีโอสั้น "หางานง่ายๆ ผ่านมือถือ", success story | Reach 10k/เดือน |
| **Instagram** | Worker Gen Z + Employer SME | Infographic ค่าแรงรายวัน, behind-the-scenes | Follower 1k ใน 60 วัน |
| **LINE Official** | Worker + Employer ทุกกลุ่ม | Broadcast งานใหม่ใกล้บ้าน, แจ้งเตือน D-1, support bot | 500 friends ใน 30 วัน |
| **X (Twitter)** | Employer / HR community | Thread "ปัญหา No-show คือต้นทุนที่มองไม่เห็น" | Thought leadership |

### Offline
| ช่องทาง | วิธี | เป้าหมาย |
|---------|------|---------|
| **Walk-in** | แจก flyer ใน นิคมอุตสาหกรรม, ตลาดแรงงาน, BTS/MRT | Worker sign-up 50 คน/อาทิตย์ |
| **Direct Call** | โทรหา HR ของ target employer list | Employer onboard 2 ราย/อาทิตย์ |

---

## 💬 CUSTOMER RELATIONSHIP

### Worker
- **LINE Official Bot** — ตอบคำถามอัตโนมัติ 24/7:
  - "หางานใกล้ฉัน" → deep-link เปิดแอพ + หน้า Nearby
  - "สถานะงานฉัน" → แจ้ง status ล่าสุด
  - "ต่ออายุ Work Permit" → link ขั้นตอน + remind อีก 7 วัน
- **Response SLA:** ตอบภายใน 2 ชั่วโมง (admin จริง), 24/7 (bot)

### Employer
- **Dedicated onboarding:** Admin โทรหา employer ใหม่ภายใน 24 ชม. หลัง sign up
- **Priority support:** Employer ที่มี posted job > 3 ใบ ได้ LINE ส่วนตัว admin
- **Monthly report:** สรุปจำนวน hires, completion rate, cost-per-hire ส่ง email ทุกสิ้นเดือน
- **Response SLA:** Business hours 09:00–18:00 ตอบภายใน 1 ชั่วโมง

---

## 📊 USER METRICS Definitions

> วัดผลทุกสัปดาห์ — dashboard ใน Supabase / Grafana (Phase 5)

| Metric | นิยาม | สูตร | Target (Month 3) |
|--------|-------|------|-----------------|
| **DAU** (Daily Active Users) | User ที่ login หรือ perform action ใดๆ ใน 24 ชม. | `COUNT(DISTINCT user_id) WHERE last_active > NOW() - 1 day` | 200 DAU |
| **Job Completion Rate** | % งานที่จบด้วย status `verified` จากงานที่เริ่ม `working` | `verified / (working + completed + verified + disputed)` | ≥ 85% |
| **Worker Retention Rate** | % worker ที่กลับมาสมัครงานอีกครั้งใน 30 วัน | `workers with 2nd application within 30d / total workers with 1st application` | ≥ 40% |
| **Time to Hire** | เวลาเฉลี่ยตั้งแต่ employer โพสต์งาน จนถึงมี worker ถูก `hired` ครั้งแรก | `AVG(decided_at - created_at) WHERE status = 'hired'` | ≤ 4 ชั่วโมง |

**Secondary metrics (track แต่ไม่ใช่ primary goal ตอนนี้):**
- No-show Rate: `no_show / hired` → target < 10%
- Dispute Rate: `disputed / completed` → target < 5%
- KYC Approval Rate: `approved / submitted` → target > 90%

---

## 🗂️ ไฟล์ปัจจุบัน

| ไฟล์ | คำอธิบาย | สถานะ |
|------|----------|--------|
| main.py | FastAPI backend — 47+ endpoints | ✅ live |
| index.html | Single-file frontend (Vanilla JS) | ✅ live |
| worker.js | Cloudflare Worker entry point (serve HTML) | ✅ |
| wrangler.toml | Cloudflare Workers config | ✅ |
| .github/workflows/deploy-frontend.yml | GitHub Actions auto-deploy | ✅ live |
| requirements.txt | Python dependencies | ✅ |
| Procfile | Railway start command | ✅ |
| .env | Env vars (ไม่ commit) | ✅ |

---

## 💡 Key Business Logic

| หลักการ | วิธีทำ |
|---------|--------|
| **Contact Lock** | เบอร์โทร/email เปิดเผยเฉพาะคู่ที่ `hired` — ป้องกัน bypass แอพ |
| **Blind Review** | review ซ่อนจนทั้งคู่ส่ง หรือครบ 7 วัน — ป้องกัน bias |
| **Wallet Escrow** *(Phase 3)* | เงินอยู่ในแอพ — ไม่มีใครอยากออกนอกระบบ |
| **GPS Checkin** | ต้องอยู่ภายใน 150m จากสถานที่งานถึงจะ checkin ได้ |
| **Auto-verify** | ≥ 90% ชั่วโมง + ไม่มีการกระทำใน 2 ชม. → system verify อัตโนมัติ |
| **Anti-Ghosting** | no-show ที่ +60 นาที → slot freed + แจ้ง employer → เปิด backup workers |
| **D-1 Reminder** | 18:00 ทุกวัน → push แจ้งเตือน hired worker ที่มีงานพรุ่งนี้ |
| **Work Permit Lock** | foreign worker สมัครงานไม่ได้ถ้าไม่มี work_permit หรือหมดอายุแล้ว |
| **Multi-language** | worker UI รองรับ 🇹🇭 TH / 🇲🇲 MM / 🇬🇧 EN — toggle ได้ทันที |
