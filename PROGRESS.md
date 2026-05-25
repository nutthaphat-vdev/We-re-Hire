# We're Hired — Progress & Roadmap
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
- [x] GET/POST/PATCH /workers/profile/me
- [x] GET /workers/applications (พร้อม maps_link + contact เมื่อ hired)
- [x] ปุ่ม 🗺️ นำทางไปที่ทำงาน (เฉพาะ hired)
- [x] ปุ่ม 📞 ดูเบอร์ + email employer (เฉพาะ hired)

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

### Phase 2 — KYC Level 1 (Free)
> ยืนยันตัวตนด้วยบัตรประชาชน + Selfie — admin verify มือ, ฟรี 100%
- [ ] รูปโปรไฟล์ worker (Supabase Storage)
- [ ] Worker upload บัตรประชาชน (หน้า-หลัง) + Selfie คู่บัตร
- [ ] Admin approve/reject KYC — manual via Supabase dashboard
- [ ] Badge **✓ KYC Verified** บน worker profile card
- [x] Migration: 010_kyc.sql ✅ run แล้ว
- [ ] Employer verification flow

### Phase 3 — Wallet & Escrow 💰 + Mobile App 📱
> นี่คือ moat หลักของ We're Hired — ถ้าเงินอยู่ในแอพ ไม่มีใครอยากโทรตรง
- [ ] Wallet schema (wallets, escrow_locks, wallet_transactions)
- [ ] Employer deposit → lock เมื่อ hired
- [ ] Release อัตโนมัติเมื่อ verified
- [ ] Pro-rata payout เมื่อ disputed (worker_pct × ค่าจ้าง)
- [ ] Worker withdrawal request
- [ ] PromptPay / Omise / 2C2P integration
- [ ] Dispute button ฝั่ง Employer + POST /applications/{id}/dispute
- [ ] **Mobile App (React Native)** — พัฒนาคู่กับ Phase 3

### Phase 3.5 — NDID Integration 🪪
> ยืนยันตัวตนระดับรัฐ ผ่านแอพธนาคาร — ดึงประวัติจริงจากราชการ
- [ ] เชื่อมต่อ NDID API (National Digital ID — ธปท.)
- [ ] Worker ยืนยันตัวตนผ่านแอพธนาคาร (กสิกร / SCB / กรุงไทย ฯลฯ)
- [ ] ดึงประวัติอาชญากรรมจากระบบราชการอัตโนมัติ
- [ ] Badge **NDID Verified** บน worker profile
- [ ] Worker Tier System:
  - `Unverified` — สมัครงานได้, ข้อมูลน้อย
  - `KYC` — บัตรประชาชน + Selfie ผ่าน admin
  - `NDID` — ยืนยันผ่านธนาคาร + ประวัติอาชญากรรมสะอาด

### Phase 4 — Notifications & Communication
- [ ] Push notifications (LINE Notify หรือ Firebase FCM)
- [ ] Worker ↔ Employer in-app chat (เฉพาะหลัง hired)
- [ ] Email notification backup

### Phase 5 — Scale & Production
- [ ] Rate limiting (per IP / per user)
- [ ] Logging + monitoring (Sentry / Grafana)
- [ ] pg_cron: reveal reviews hourly, expire old jobs
- [ ] Custom domain + HTTPS
- [ ] Dockerize (Dockerfile + docker-compose)

### Phase 6 — Growth
- [ ] Landing page / Marketing site
- [ ] Job recommendation engine (ML-based matching)
- [ ] Worker availability calendar
- [ ] Multi-zone posting
- [ ] Referral system
- [ ] ขยายนอก BKK

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
