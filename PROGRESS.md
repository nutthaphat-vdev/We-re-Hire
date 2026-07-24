# We're Hired — Progress & Roadmap

> **"ทำงานวันนี้ เสร็จงานได้เงินทันที"**
> อัปเดตล่าสุด: 2026-07-24 · Session Log (เรียงตามวันที่) อยู่ท้ายไฟล์

**สารบัญ:** [Strategy](#-strategy) · [Key Business Logic](#-key-business-logic) · [Business & GTM](#-business--gtm) · [Production Live](#-production--live-แล้ว) · [Migrations](#-database-migrations) · [ต้องทำต่อ](#-ต้องทำต่อ) · [ไฟล์ปัจจุบัน](#-ไฟล์ปัจจุบัน) · [Roadmap](#-roadmap) · [Session Log](#-session-log)

---

## 🧭 Strategy

> north star — ภาพรวมที่ต้องจำไว้เสมอ (บันทึก 18 มิ.ย.)

### Core Strategy: น้ำซึมหิน
ไม่ชนตลาดใหญ่ตรงๆ — เริ่มจากช่องที่ไม่มีใครสน แล้วซึมเข้าไปทีละตลาด

```
daily wage (ไม่มีใครทำจริงจัง)
  → สะสม volume + data + trust
  → calendar + full-time job board (แย่ง SME จาก JobThai/JobsDB)
  → behavioral score + HH mode (แย่ง enterprise จาก headhunter)
  → work permit (ล็อก employer ต่างด้าวออกไม่ได้)
```

### Moats ที่มีอยู่แล้ว
| Moat | ที่มา | ทำไมคู่แข่ง copy ไม่ได้ |
|------|-------|------------------------|
| **Data** | behavioral score สะสมจากการใช้จริง | ต้องใช้เวลา — มาทีหลังไม่มีทาง catch up |
| **Work Permit** | employer ทำ work permit ผ่าน WeHire | ออกจาก platform ไม่ได้ |
| **Trust** | KYC + NDID + behavioral รวมกัน | ไม่มีแพลตฟอร์มไหนในไทยทำครบขนาดนี้ |
| **Network** | worker เยอะ → employer มา → วนซ้ำ | ยิ่ง dense ยิ่งทำลายยาก |
| **Switching Cost** | เงินอยู่ใน wallet (Phase 3) | ไม่มีใครอยากย้าย |

### คู่แข่งและช่องว่าง
| เจ้า | ทำอะไร | ที่ WeHire เข้าแทรกได้ |
|------|--------|----------------------|
| JobsDB / JobThai | งานประจำอย่างเดียว | ไม่มี daily wage, ไม่มี GPS, ไม่มี behavioral data |
| Workmate / Temp agency | มีคนกลาง, แพง, ช้า | real-time matching, ถูกกว่า, direct |
| Fastwork | freelance ดิจิทัล | คนละตลาด — blue-collar general ไม่มีใครทำ |
| LINE MAN / Grab | gig delivery | ไม่ครอบ general labor |

**ความเสี่ยงจริง:** เจ้าใหญ่ที่มีทุนหนา (Grab, SCB) pivot มาชน → ต้องรีบสร้าง moat ก่อน

### Ladder Model
```
ตลาดล่าง  → daily wage → volume + data
ตลาดกลาง → calendar + full-time → SME จ่ายมากขึ้น
ตลาดบน   → HH mode → enterprise → margin สูงสุด
```
feature แต่ละอันไม่ได้รู้สึกว่ากำลังบุก — แต่พอมองย้อนหลัง 3 ปี ซึมเข้าไปในทุกตลาดแล้ว

---

## 💡 Key Business Logic

| หลักการ | วิธีทำ |
|---------|--------|
| **Contact Lock** | เบอร์โทร/email เปิดเผยตลอด `hired → verified` — ป้องกัน bypass แอพ |
| **Blind Review** | review ซ่อนจนทั้งคู่ส่ง หรือครบ 7 วัน — ป้องกัน bias |
| **Wallet Escrow** *(Phase 3)* | เงินอยู่ในแอพ — ไม่มีใครอยากออกนอกระบบ |
| **GPS Checkin** | ต้องอยู่ภายใน 150m จากสถานที่งานถึงจะ checkin ได้ |
| **Auto-verify** | ≥ 90% ชั่วโมง + ไม่มีการกระทำใน 2 ชม. → system verify อัตโนมัติ |
| **Anti-Ghosting** | no-show ที่ +60 นาที → slot freed + แจ้ง employer → เปิด backup workers |
| **D-1 Reminder** | 18:00 ทุกวัน → push แจ้งเตือน hired worker ที่มีงานพรุ่งนี้ |
| **Work Permit Lock** | foreign worker สมัครงานไม่ได้ถ้าไม่มี work_permit หรือหมดอายุแล้ว |
| **Multi-language** | worker UI รองรับ 🇹🇭 TH / 🇬🇧 EN — toggle ได้ทันที ครอบคลุมทุกหน้า |
| **Job Auto-Close** | `auto_close_at` — 48 ชม. ก่อน start_date → auto-close + notify employer พร้อมเหตุผล |

---

## 💼 Business & GTM

### Revenue Streams (verified — กรมการจัดหางาน 2025)
| Stream | โมเดล | Margin | Phase |
|--------|-------|--------|-------|
| **Matching Fee** | 6% per transaction (rotation market — employer ต้องกลับมาเสมอ) | ~90% | ✅ Live |
| **Work Permit Service** | ขาย 10,000 บาท/คน (ต้นทุน ~1,500–2,500) · recurring ทุก 2 ปี | ~75% | Phase 2 |
| **White Collar Job Board** | flat posting fee — upsell ฐาน employer เดิม ไม่ต้อง CAC ใหม่ | ~85% | Phase 3 |
| **Headhunter (HH)** | 15–20% เงินเดือนเดือนแรก · ต้องมีใบอนุญาตจัดหางาน (5,000 บาท/2 ปี) | ~70% | Phase 5 |

- **Key insight:** Work permit = lock-in mechanism ที่แข็งแกร่งที่สุด — employer ที่ทำผ่าน WeHire ออกไม่ได้
- **Key insight:** Rotation market = worker ไม่ว่างตลอด → employer ต้องกลับมาใช้ platform แม้เคยจ้างตรง

### Key Partners (Phase 2 — เป้า 25 employer partners ใน 3 เดือน)
| กลุ่ม | ตัวอย่าง | ความต้องการหลัก | วิธี approach |
|-------|---------|----------------|--------------|
| **โรงงาน** | นิคมฯ ลาดกระบัง, บางปู, บางชัน | แรงงานสายพาน/แพ็ก จำนวนมาก ทุกวัน | Direct call HR, เสนอ cost/worker ต่ำกว่า agency |
| **โรงแรม** | Airbnb Host, Boutique, Budget Hotel | แม่บ้าน/ต้อนรับ/ครัว — high season/แทนคนลา | Line OA + Walk-in สุขุมวิท, สีลม, สาทร |
| **ร้านสะดวกซื้อ** | 7-Eleven, FamilyMart, Lotus Express | Part-time กะดึก, fill-in | เจรจาผ่าน CP Franchise head office |
| **ร้านอาหาร** | SME, Chain, Food Court | ครัว/เสิร์ฟ/ล้างจาน — weekends + holidays | FB Group เจ้าของร้าน + Walk-in |
| **ขนส่ง/โลจิสติกส์** | Lazada, Flash, Kerry hub | คัดแยก/โหลดสินค้า — ช่วงเทศกาล | LinkedIn outreach ทีม Ops + Pitch deck |

### Channels
**Online:** Facebook (worker 18–40, reach 10k/เดือน) · Instagram (Gen Z + SME, 1k followers/60วัน) · LINE Official (broadcast งาน + D-1 + support bot, 500 friends/30วัน) · X (HR community, thought leadership)
**Offline:** Walk-in แจก flyer (นิคมฯ / ตลาดแรงงาน / BTS-MRT, 50 sign-up/สัปดาห์) · Direct Call HR (2 employer/สัปดาห์)

### Customer Relationship
- **Worker:** LINE Official Bot 24/7 (หางานใกล้ฉัน / สถานะงาน / ต่อ Work Permit) · SLA admin จริง 2 ชม.
- **Employer:** onboarding call ภายใน 24 ชม. · Priority LINE ถ้า posted > 3 ใบ · monthly report (hires / completion / cost-per-hire) · SLA business hours 1 ชม.

### User Metrics (วัดทุกสัปดาห์)
| Metric | นิยาม | สูตร | Target (M3) |
|--------|-------|------|-------------|
| **DAU** | login/action ใน 24 ชม. | `COUNT(DISTINCT user_id) WHERE last_active > NOW()-1d` | 200 |
| **Job Completion Rate** | % งานจบ `verified` จากที่เริ่ม `working` | `verified / (working+completed+verified+disputed)` | ≥ 85% |
| **Worker Retention** | % worker กลับมาสมัครใน 30 วัน | `2nd application within 30d / 1st application` | ≥ 40% |
| **Time to Hire** | โพสต์ → `hired` ครั้งแรก | `AVG(decided_at - created_at) WHERE status='hired'` | ≤ 4 ชม. |

**Secondary:** No-show `no_show/hired` < 10% · Dispute `disputed/completed` < 5% · KYC Approval `approved/submitted` > 90%

---

## ✅ Production — Live แล้ว

### 🔧 Infrastructure
- [x] Supabase PostgreSQL + PostGIS · FastAPI + asyncpg pool (PgBouncer transaction mode)
- [x] JWT Auth middleware (HS256 — token ของเราเอง) · bcrypt password hashing (cost=12)
- [x] Google OAuth via Supabase — verify ด้วย JWKS + ES256
- [x] CORS config (env var + hardcode allowlist) · Health check endpoint
- [x] Deploy: Railway → **Render** (backend) + Cloudflare Workers (frontend)
- [x] GitHub Actions auto-deploy — push → Cloudflare อัตโนมัติ
- [x] Worker rename → `wearehiredmvp.vi-nutthaphat.workers.dev` · Production URL Change Checklist (8 ขั้นใน CLAUDE.md)
- [x] GitHub repo ย้ายบัญชี + Railway/Render source reconnect · backend URL อัปเดตครบ

### 🔐 Auth
- [x] POST /auth/register (worker/employer) · POST /auth/login · GET /auth/me
- [x] GET /auth/google/url + POST /auth/google/callback · Consent Screen Published

### 👷 Worker
- [x] GET/POST/PATCH /workers/profile/me (nationality_type, work_permit_url, work_permit_expiry)
- [x] GET /workers/applications (maps_link + contact เมื่อ hired) · ปุ่ม 🗺️ นำทาง · ปุ่ม 📞 ดูเบอร์/email (เฉพาะ hired)
- [x] Work Permit Enforcement — block apply ถ้า foreign worker ไม่มี/หมดอายุ (403)

### 🏭 Employer
- [x] GET/POST/PATCH /employers/profile/me · ปุ่ม 📞 ดูเบอร์ worker (เฉพาะ hired)

### 💼 Jobs
- [x] POST /jobs · GET /jobs/mine · PATCH /jobs/{id}/status (open/closed)
- [x] Job categories cascade dropdown · GET /zones (50 เขต กทม. + ปริมณฑล)

### 🎯 Matching Engine
- [x] GET /jobs/nearby — PostGIS ST_DWithin (1–30km) · skill filter รองรับ worker ไม่มี skills (cardinality fix)
- [x] POST /jobs/{id}/apply — score: skills 60% / distance 25% / rate 15%
- [x] GET /jobs/{id}/candidates (ranked) · PATCH /applications/{id}/decide (hired/rejected/shortlisted)
- [x] Auto Google Maps navigation link เมื่อ hired
- [x] **Auto-Withdraw Overlap** — hire แล้ว auto-withdraw applications อื่นที่วันซ้อน (batch O(1) + notify employer)

### 🔒 Contact Reveal
- [x] GET /applications/{id}/contact — เปิดเผยเบอร์/email ตลอด `hired → verified` (Contact Lock)

### 📋 Job Lifecycle
- [x] hired → checked_in → working → completed → verified / disputed
- [x] POST /applications/{id}/checkin (GPS ≤ 150m) · /start (±30 นาที) · /complete · /verify
- [x] Auto-verify cron ทุก 30 นาที (≥ 90% → verified, < 90% → disputed)
- [x] **Job Auto-Close** — `auto_close_at` (start_date-48h หรือ NOW()+7d) · cron 30 นาที (no_applicants / no_hire) + notify

### 👻 Anti-Ghosting System (ครบ 100%)
- [x] status `no_show` · GET /jobs/{id}/backup-workers (top 10 ranked) · POST send-backup / accept-backup · PATCH mark-noshow
- [x] Cron 5 นาที: alert +10 นาที, auto no_show +30 นาที หลัง work_start (fallback 08:00 ถ้าไม่มี work_start)
- [x] Cron 18:00 ทุกวัน: D-1 reminder → hired workers ที่มีงานพรุ่งนี้
- [x] Backup wage lock (pro-rata) · distance-based cascade (ST_Distance) · auto-confirm 5 นาที · backup worker เห็นค่าจ้างก่อนรับ

### ⭐ Review System
- [x] Blind review (ซ่อนจนทั้งคู่ส่ง/ครบ 7 วัน) · 1–5 ดาว + tag buttons
- [x] GET /review-tags · POST /reviews · GET /reviews/me · GET /reviews/pending

### 🧮 Behavioral Score
- [x] `jobs_hired +1` เมื่อ checkin (fair กับ worker) · `jobs_noshow +1` เมื่อ auto no-show · `jobs_completed +1` เมื่อ verified
- [x] `reliability_score` recompute อัตโนมัติทุก trigger (0.00–10.00)

### 💰 Earnings Page
- [x] Sidebar 💰 รายได้ · summary card (รายได้รวม + จำนวนงาน) · transaction list (ชื่องาน/บริษัท/วันที่/฿/backup badge)
- ⚠️ **Known Debt:** ตัวเลข = "ประมาณการณ์" ไม่ใช่ "รับจริง" — ดู CLAUDE.md Vibe Code Debt

### 🛡️ Trust & Safety
- [x] POST /reports · POST /blocks · ปุ่ม 🚩 Report ใน frontend

### 🔐 Security (Audited 26 พ.ค. — Sonnet 4.6: 4 CRITICAL / 7 WARNING / 6 INFO ผ่านหมด)
- [x] XSS: `esc()` ทุก user-input ใน innerHTML · auto-ban ลบออก (แทนด้วย logger.warning + admin review)
- [x] `/docs` ปิดใน production · CORS URL เก่าลบออก · email ไม่รั่วใน /users/blocked
- [x] Review ส่งได้หลัง verified/disputed (fix `status='hired'` → `IN ('hired','verified','disputed')`)
- [x] worker.js security headers (CSP, X-Frame-Options: DENY, X-Content-Type-Options, Referrer-Policy, Permissions-Policy)
- [x] worker_service.py column allowlist + validation ก่อน dynamic SET (กัน SQL injection)

### 🔔 Notifications
- [x] Badge unread count (poll 30 วิ) · cache no-store fix · list + filter (ทั้งหมด/ยังไม่อ่าน)
- [x] Smart date labels · type badges + icon · อ่านทีละอัน + อ่านทั้งหมด
- [x] Deep-link navigation (hired/rejected/shortlisted → ใบสมัคร · new_applicant → งานของฉัน · review_pending → รีวิว) + auto-mark read

### 🌐 Frontend UX & i18n
- [x] Multi-language UI TH/EN ครอบคลุมทุกหน้า (sidebar/dashboard/nearby/myapps/myjobs/candidates/notifications/profile)
- [x] Lang preference ใน localStorage (`wh_lang`) · toggle text-only TH/EN
- [x] Work Permit section บน worker profile (badge, link, เตือน < 30 วัน, error ถ้าหมด) · nationality selector

### 📱 Mobile Responsive
- [x] Hamburger ☰ + sidebar slide + overlay (< 768px) · `.main` 100% · font/padding/grid ลดลง
- [x] (07-08) การ์ดจัดการงานไม่หด · ช่องวันที่ชิดซ้าย · sidebar ปิดสนิท · กัน iOS zoom (input 16px) · noti title ไม่ตัด

### 🛡️ Admin Dashboard
- [x] `require_admin` JWT dependency (role='admin')
- [x] GET /admin/stats (15 metrics single query) · GET /admin/users (paginated) · PATCH users/{id}/status
- [x] GET /admin/kyc/pending (signed URLs) · PATCH kyc/{id}/review (verified/failed + notify)
- [x] GET /admin/disputes · PATCH disputes/{id}/resolve · GET /admin/jobs · PATCH jobs/{id}/status
- [x] GET /public/stats (no-auth, landing page) · POST /admin/cron/trigger (auto_verify + check_expired_jobs)
- [x] Frontend: admin nav (ซ่อนถ้าไม่ใช่ admin) + 5 หน้า (stats/users/kyc/disputes/jobs) · admin user ใน DB

### 🪪 KYC Photo Upload
- [x] POST /workers/kyc/upload — multipart face + id_card → Supabase Storage (JPG/PNG/WebP ≤ 5MB)
- [x] Path `kyc/{worker_id}/face.jpg` · UPDATE urls + `background_check_status='pending'`
- [x] Admin KYC: thumbnails คลิกดูใหญ่ + signed URLs (expire 1h) · requirements: supabase==2.10.0, python-multipart==0.0.9

### 🏠 Landing Page
- [x] Full-scroll 5 sections: Hero → Stats bar (live `/public/stats`) → How it works (worker/employer 3 steps) → Key features (6 cards) → Market context + Footer CTA
- [x] (07-08) How-to-use guide (7 ขั้น worker + 4 ขั้น employer, สองภาษา) · onboarding popup หลังสมัคร (เด้งซ้ำจนกว่าจะทำ)
- [x] เบอร์โทร: บังคับกรอก + validate 10 หลักขึ้นต้น 0 (FE + BE `re.fullmatch`)

---

## 🗄️ Database Migrations

| ไฟล์ | สถานะ | ไฟล์ | สถานะ |
|------|-------|------|-------|
| supabase_setup_full.sql | ✅ | 013_job_expiry.sql | ✅ |
| 003_review_system.sql | ✅ | 014_kyc_photos.sql | ✅ |
| 004_review_star_rating.sql | ✅ | 015_auto_confirm.sql | ✅ |
| 005_job_categories.sql | ✅ | 016_backup_wage.sql | ✅ |
| 006_trust_safety.sql | ✅ | 017_behavioral_score.sql | ✅ |
| 007_work_hours.sql | ✅ | 018_job_categories_v2.sql | ✅ |
| 008_job_lifecycle.sql | ✅ | 019_policy_consent.sql | ✅ |
| 009_disputed_status.sql | ✅ | 020_job_fields.sql | ✅ |
| 010_kyc.sql | ✅ | 021_payment_proof.sql | ⏳ รอ run (in-flight) |
| 011_job_categories_expanded.sql | ✅ | | |
| 012_anti_ghosting.sql | ✅ | | |

---

## 🔧 ต้องทำต่อ

### Manual / Quick wins
- [ ] **Review summary** — ดาวเฉลี่ย + top tags แสดงบน profile card
- [ ] **Contact button reload** — ปุ่ม 📞 โผล่ทันทีหลัง hired โดยไม่ต้อง refresh
- [ ] **claude-bridge MCP** — ลบ `run_command` + เพิ่ม auth token + reconnect

### Security Hardening (ก่อน Scale / หลัง Pitch)
- [x] **Rate limiting** (slowapi) — `/auth/login` 10/min, `/apply` 20/min ✅ 07-22
- [x] **CORS `null` origin ตัดออก** + **admin secret timing-safe** (`secrets.compare_digest`) ✅ 07-22 (audit รอบ 2)
- [ ] Rate-limit `/auth/register` + upload endpoints (KYC/slip) — 🟡 ต่ำ ไม่ block pilot
- [ ] Generic error message — เลิกเผย raw exception ใน `detail`
- [ ] **JWT expire ลดเป็น 120 นาที** — ลดหน้าต่าง token theft
- [ ] **`is_active` check ใน `get_current_user`** — banned user ใช้ token เก่าไม่ได้ทันที
- [ ] Revoke GitHub token เก่า `ghp_9Qiy…` (founder)

---

## 🗂️ ไฟล์ปัจจุบัน

| ไฟล์ | คำอธิบาย | สถานะ |
|------|----------|--------|
| main.py | FastAPI backend — 47+ endpoints | ✅ live |
| index.html | Single-file frontend (Vanilla JS) | ✅ live |
| worker.js | Cloudflare Worker entry (serve HTML) | ✅ |
| wrangler.toml | Cloudflare Workers config | ✅ |
| .github/workflows/deploy-frontend.yml | GitHub Actions auto-deploy | ✅ live |
| WeHired_DarkFlyer.html / LightFlyer.html | ใบปลิว GTM (FB/LINE + พิมพ์ A4) | ✅ |
| requirements.txt / Procfile | Python deps / start command | ✅ |
| .env | Env vars (ไม่ commit) | ✅ |

---

## 📋 Roadmap

### Phase 2A — KYC Level 1 (Free) 🪪
> ยืนยันตัวตนด้วยบัตร ปชช. / Passport + Selfie — admin verify มือ, ฟรี 100%

**ทำแล้ว ✅:** migration 010_kyc · Work Permit enforcement + profile section · Multi-language TH/EN · POST /workers/kyc/upload · GET/PATCH admin kyc review · admin KYC page + thumbnails

**ยังต้องทำ:**
- [ ] Badge **✓ KYC Verified** บน profile card + candidate list หลัง approve
- [ ] Cron รายวัน: Work Permit expiry alert + auto-reject ถ้า expired
- [ ] รูปโปรไฟล์ worker · Employer verification flow
- [ ] Supabase bucket `kyc-documents` + `SUPABASE_SERVICE_KEY` (✅ ตั้งแล้ว 06-01)

### Phase 2B — Behavioral Score System 🧮
> วัดความน่าเชื่อถือจากพฤติกรรมจริง (core engine ✅ live แล้ว — ดู Production)

```
reliability_score = (completion_rate × 5.0) + ((1 - noshow_rate) × 3.0) + (review_avg × 2.0)   [0.00–10.00]
```
| Badge | Score |
|-------|-------|
| 🌟 Top Worker | ≥ 9.0 |
| ✅ Reliable | ≥ 7.0 |
| ⚠️ (admin only) | < 5.0 |

- [ ] Frontend: แสดง "ความน่าเชื่อถือ ⭐⭐⭐⭐☆" บน worker profile card
- [ ] Employer: filter ผู้สมัครตาม reliability_score ขั้นต่ำ

### Phase 3 — Wallet & Escrow 💰 + Mobile App 📱
> moat หลัก — ถ้าเงินอยู่ในแอพ ไม่มีใครอยากโทรตรง
- [ ] Wallet schema (wallets, escrow_locks, wallet_transactions) · employer deposit → lock เมื่อ hired
- [ ] Release อัตโนมัติเมื่อ verified · pro-rata payout เมื่อ disputed · worker withdrawal
- [ ] PromptPay / Omise / 2C2P integration · Dispute button + POST /applications/{id}/dispute
- [ ] **Mobile App (React Native / Expo)** — Auth, Nearby, GPS Checkin, KYC camera, Notifications, Wallet

### Phase 3.5 — NDID Integration 🏛️
> ยืนยันระดับรัฐผ่านแอพธนาคาร — ดึงประวัติจริงจากราชการ
- [ ] เชื่อม NDID API (ธปท.) · worker ยืนยันผ่านธนาคาร (กสิกร/SCB/กรุงไทย) · ดึงประวัติอาชญากรรมอัตโนมัติ
- [ ] Badge **🏛️ NDID Verified** · Worker Tier: Unverified → KYC → NDID

### Phase 4 — AI Integration 🤖
> Haiku filter ก่อน → ซับซ้อนค่อยส่ง Sonnet
| Use Case | Model |
|----------|-------|
| Support Bot / KYC pre-filter / Behavioral classify | Haiku |
| Dispute resolution / Matching v2 / Fraud detection | Sonnet |

- [ ] เชื่อม Anthropic API · POST /support/chat (LINE OA) · POST /admin/kyc/precheck · POST /admin/disputes/{id}/ai-suggest
- [ ] Matching v2 free-text job desc · cost guardrail (Haiku 1k / Sonnet 2k tokens)

### Phase 4B — Voice-First Onboarding 🎙️
> แก้ pain: worker อ่านไม่คล่อง / ไม่ถนัด smartphone · ต้นทุน ~$0.02–0.05/user
- Flow: กด Live Chat → AI ถามทีละขั้น + TTS → worker ตอบด้วยเสียง/พิมพ์ → AI กรอก form ให้ + เสนอ action เชิงรุก
- OCR บัตร ปชช.: Haiku vision → auto-fill (~$0.002/ครั้ง) · STT/TTS: Web Speech API (ฟรี) + Whisper fallback
- ⚠️ Risk: Web Speech API รองรับสำเนียงไทยต่างจังหวัด/ต่างด้าวแค่ไหน → ถ้าต่ำ fallback text + AI guide
- [ ] Prototype chat widget · OCR auto-fill · voice input · TTS · proactive suggestion · ทดสอบ STT (อีสาน/เหนือ/ใต้ + เมียนมา/ลาว)

### Phase 4C — Full-Time Job Board 📋
> ขยาย "หางานวันนี้" → "หางานประจำ" ในแอพเดียว · ใช้ฐาน employer เดิม (ไม่ต้อง CAC ใหม่)
- Worker เห็น 2 tab (งานรายวัน | งานประจำ) · employer เลือก type = `full_time` · flat fee ฿500–1,500/โพสต์ (ไม่ต้องใบอนุญาต)
```sql
ALTER TABLE job_postings ADD COLUMN IF NOT EXISTS job_type VARCHAR(20) DEFAULT 'daily'
  CHECK (job_type IN ('daily', 'full_time', 'part_time'));
```
- [ ] job_type + migration · tab switch · employer form (salary range, desc, benefits) · worker resume (expected_salary, experience)
- [ ] Matching งานประจำ (skills + salary, ไม่มี GPS) · flat posting fee flow · admin approve ก่อน publish

### Phase 4D — Smart Calendar 📅
> Two-sided: worker เห็นงานใกล้ตัว, employer วางแผน + โพสต์ได้เลย
- **Worker:** weekly view → top 5 งานใกล้/วัน (sort distance) → 1-tap apply · วัน hired = block เขียว
- **Employer:** timeline งานที่โพสต์ · ครบ=เขียว / ขาด=ส้ม+จำนวน / ว่าง=เทา → กดวันว่าง = quick post
- **GeoPosting:** กดวันว่าง → เห็น available workers บนแผนที่รัศมี X km (ST_DWithin กลับทิศ) → กด pin → invite
```sql
CREATE INDEX IF NOT EXISTS idx_jobs_start_date_status ON job_postings(start_date, status) WHERE status = 'open';
```

### Phase 5 — AI Headhunter Mode 🎯
> WeHire รู้จัก worker จริงกว่า HH ทั่วไป (พฤติกรรมจริง ไม่ใช่แค่ resume)
- Data ที่มีแล้ว: reliability_score, job history, behavioral pattern, skill match history
- Flow: employer โพสต์ตำแหน่งสูง → AI recommend top 3–5 + reasoning → จ่าย HH fee เมื่อ hire (15–20% เดือนแรก)
- **ต้องมีก่อน:** ใบอนุญาตจัดหางาน (5,000 บาท/2 ปี) · track record + trust · Phase 2B live
- [ ] AI scoring model (Sonnet) · HH request flow + fee · recommendation engine + reasoning · HH fee escrow

### Phase 6 — Notifications & Scale
- [ ] Push (LINE Notify / FCM) · in-app chat (หลัง hired) · email backup
- [ ] Rate limiting · logging/monitoring (Sentry/Grafana) · pg_cron · custom domain + HTTPS · Dockerize

### Phase 7 — Growth
- [ ] Landing/marketing site · ML recommendation engine · availability calendar · multi-zone · referral · ขยายนอก BKK

---

## 📅 Session Log

> เรียงตามวันที่ (เก่า → ใหม่)

### Day 6 · 30 พ.ค. — Business Strategy + Job Expiry
- **Job Auto-Close (013_job_expiry):** `auto_close_at`/`auto_closed_reason` + partial index · POST /jobs คำนวณอัตโนมัติ · cron 30 นาที (no_applicants / no_hire) + notify · frontend hint + countdown badge
- **Revenue Streams** บันทึกใน CLAUDE.md (Work Permit 10k margin ~7.5k · White Collar Phase 3 · HH Phase 5 · rotation market insight · work permit = lock-in) → สรุป → Business & GTM section
- **Manual done:** Mobile Responsive · run 013 + 014 · Supabase bucket `kyc-documents` (06-01) · เปลี่ยน admin password (06-01) · SUPABASE_SERVICE_KEY (06-01)

### Day 7 · 1 มิ.ย. — MCP Setup
- MCP wehire-fs — ติดตั้ง `@modelcontextprotocol/server-filesystem` ผ่าน Claude Desktop config
- Claude Desktop เชื่อม filesystem ได้ (read/write/list ที่ `C:\Users\User\Downloads\Hire`)

### Day 8 · 2 มิ.ย. — Pre-Pitch Polish + Bug Fixes
- **W1 KYC Badge + Profile Photo:** `profile_photo_url` ใน candidates query + schemas + worker_service SELECT ครบ · frontend avatar จริง + ✓ KYC badge (ซ่อนถ้า verified)
- **W2 Admin Dashboard Redesign:** /admin/stats +6 metrics · /public/stats endpoint ใหม่ · 3-row layout + color coding
- **W3 Security Hardening:** worker.js security headers · worker_service column allowlist (กัน SQL injection)
- **Landing + Dashboard Redesign:** full-scroll 5 sections + live stats · worker/employer dashboard (greeting + stats จริง + active jobs + nudge) · employer verification badge
- **UI Redesign ทุกหน้า:** Find Job / Applications / Notifications / Reviews / Worker Profile / Candidate card
- **Bug fixes:** check_expired_jobs `NameError: total_hired` (auto-close พังทั้งหมด) · noshow cron ปรับเวลา +10/+30 + `start_date <= today` + fallback 08:00 + auto backup + per-row try/except · JS escape quote · index.html truncation (restore git) · requirements.txt bust cache
- **Pitch Deck (Canva):** เชื่อม MCP · แก้ 5 content issues · tagline "The Right Worker. Right Now. Right Here."

### Day 9 · 15 มิ.ย. — Repo Hygiene + Map Pin Fix
- **Repo:** regenerate GitHub PAT + update remote · `git rm --cached .env` · ลบ __pycache__ ค้าง · push doc updates `ee4365d`
- **Map pin fix (index.html):** ลากหมุดไม่ได้ → เพิ่ม `draggable: true` + `dragend`/`click` listener → reverse geocode อัปเดต lat/lng · เปลี่ยน icon เป็นเข็มหมุดแดง · ใช้ร่วม 3 จุด (post job / search / worker profile) · push `d2f0a46`
- ⚠️ reverse geocode เรียก Google Geocoding API ทุกครั้งที่ลาก/คลิก — cost เล็กน้อย อยู่ใน free tier

### Day 10 · 19 มิ.ย. — Bilingual i18n (TH/EN)
- **i18n architecture:** LANG object (`th`/`en`) + `t('key')` + `data-i18n` + `setLang()` re-render
- ครอบคลุม: landing, notifications, find jobs, my applications, reviews, worker profile, post job, my jobs, employer dashboard + create form, candidates
- `_notifTranslateTitle()` map 24 Thai titles → EN (frontend-only) · review summary widget · category/zone/title dropdowns ใช้ `name_en`
- **ยังเหลือ (ดู I18N_HANDOFF.md):** post job validation/success · button state text · worker profile create form · session timeout · report modal · work permit status · GPS/map status · admin UI (low priority)

### Session · 20 มิ.ย. — Anti-Ghosting Complete + Behavioral Score
- **Anti-Ghosting Loop (100%):** backup wage lock (pro-rata) · distance cascade (ST_Distance) · auto-confirm 5 นาที · backup worker เห็นค่าจ้างก่อนรับ · accept backup UI (`doAcceptBackup()`)
- **Behavioral Score (017):** jobs_hired +1 เมื่อ checkin · jobs_noshow +1 เมื่อ auto no-show · jobs_completed +1 เมื่อ verified · reliability_score recompute อัตโนมัติ
- **Earnings Page:** sidebar 💰 · summary card · transaction list
- ⚠️ **Known Debt:** Earnings = "ประมาณการณ์" ไม่ใช่ "รับจริง" (ดู CLAUDE.md Vibe Code Debt)

### Session · 8 ก.ค. — วันแรกกลับมาหลังพัก 7-8 วัน
- **Ship ขึ้น live (FE + BE):** landing how-to guide (7 ขั้น worker + 4 ขั้น employer สองภาษา) · onboarding popup (worker→ตั้งอาชีพ, employer→โพสต์งาน เด้งซ้ำจนกว่าจะทำ) · เบอร์โทรบังคับ + validate 10 หลักขึ้นต้น 0 (FE + BE) · mobile UI fixes · commits 2c22cf4, f92d86f, cc26e05, ad0bff8
- **⏳ In-flight:** payment-proof flow (task packet ใน bridge/inbox) — employer แจ้งจ่าย (cash/transfer+slip) → worker ยืนยันได้รับ = pair สำเร็จ · migration 021_payment_proof.sql
- **บทเรียน:** เจอ torn-read (mount อ่าน index.html ขาด 267 บรรทัด → commit ไฟล์ขาด) กู้ทันจาก git · **ล็อกกฎ: ไฟล์ใหญ่แก้ผ่าน bridge เท่านั้น**
- **ทิศทาง (สำคัญ):** scoreboard = **pair (งานจบจ่ายจริง)** เป้า 5-10/เดือน must=1 · beachhead = **โรงแรม belt กลางเมืองผ่าน connection พ่อ** · focus worker supply demand-led · Angel ต้องการ traction จริง · รายละเอียด → GTM_traction_plan.md, HANDOFF.md

### Session · 16 ก.ค. — Auth Overhaul + Double-Hire Fix + Worker Profile Redesign
> เริ่มจาก "แก้ปุ่ม mockup" → กลายเป็นปิดรู backend + ยกเครื่อง auth + รื้อโปรไฟล์ทั้งหน้า · deploy + เทสจริงบน prod ครบ
- **🔴 Double-hire ปิดครบ (เทส prod 6/6):** migration `023_job_time_range.sql` = `job_occupied_range()` → tsrange (วันเดียว / ข้ามคืน +1วัน / หลายวัน=เต็มสแปน) · `decide`: advisory lock + guard กัน hire ทับเวลา + auto-withdraw เปลี่ยนวันล้วน→วัน+เวลา · `accept_backup_offer`: guard เดียวกัน (อุดรูรั่ว backup path) · `_cascade_backup_offer`+`get_backup_workers`: กรอง `is_available` + overlap · commits `2fe2fc0`,`2974d06` · `test_double_hire.py`
- **🔑 Auth overhaul (เทส 8/8):** phone login (เบอร์-หรือ-อีเมล + password) · remember me **30 วัน** · timing-enum fix (dummy bcrypt constant-time) · phone capture ฝั่ง **Google user** (ช่องเบอร์ในฟอร์ม profile + endpoint `PATCH /auth/phone` + gate apply/post ถ้าไม่มีเบอร์) · PDPA consent บันทึกตอน Google signup · commit `8af365f` · `test_auth.py`
- **🎨 Worker profile redesign (index.html — ยก Gemini/viewcard ลง prod, เก็บ id/logic เดิมครบ):** ช่องเบอร์ create/edit + pre-fill จาก `/auth/me` · hero card (avatar gradient 76px, badge, stat card, ปุ่มแก้ไข) · create/edit form การ์ด · KYC upload card + PDPA boxed · **inline SVG icons** (Phosphor CDN ไม่ render ใน prod — เดา CSP/font → เลิกใช้ ใช้ SVG เอง) · `_noIco()` strip emoji ซ้ำจาก i18n · KYC selfie `capture="user"` (บังคับกล้องหน้า), บัตร = chooser (กล้อง+คลัง) · commits `38d2728`→`3c3c915`
- **⚠️ Debt/roadmap ที่จดไว้:** JWT revoke ก่อน escrow (`token_version`) · rate-limit lockout ต่อบัญชี · OTP login (Firebase/SMS) · **in-app camera + liveness** (แทน `capture` — คู่กับ selfie check-in) · เบอร์ recycle
- **🧭 ทิศทาง (สำคัญ):** hotel HR **2-3 เจ้า "อยากได้ตัวเต็ม" แต่ยังไม่ใช้** → pull ฝั่ง employer = seed ที่ถูก (employer-first: งานดึง worker) · แผนพี่: **ขัด UI จบ → ไม่แตะ feature ใหม่ → traction เต็มระบบ** · **employer mockup มี 8 หน้า** (post-job/profile/live-roster ยังหยาบ) · **critical path จ้างจริง = post-job + view-applicants** (backend มีครบแล้ว แค่ยก UI + wire แบบเดียวกับ worker profile) · ⚠️ กับดัก: "ทำให้ดีกว่านี้ก่อน" จาก prospect มักเป็น polite stall → ควรผลัก **pilot จ้างจริง 1 กะ** แทนขัดไปเรื่อย
- รายละเอียดเต็ม + next steps → **`HANDOFF_2026-07-16.md`**

### Session · 19–24 ก.ค. — Cron Postmortem + Onboarding UX + Security Audit + RN Prep
> Session ยาวข้ามหลายวัน — infra debugging จริงจัง + UX fix จาก user testing จริง + security audit รอบ 2 + ทดสอบ bridge sub-agent pattern
- **🐛 Cron postmortem (แก้ misdiagnosis เดิม):** เดิมเข้าใจผิดว่า "Render หลับ → cron ตาย" — หลักฐานจริงคือ logger ไม่มี handler (info ถูกทิ้งเงียบ) + `/health` ไม่รับ HEAD (UptimeRobot false-Down) + misfire_grace_time default 1 วิ · แก้ครบ 3 จุด + ยืนยันด้วย log จริง 171 รอบต่อเนื่อง 14.2 ชม. ไม่มีรอบขาด → **ไม่ต้องจ่าย Render Starter** commits `eb497d2`,`378af40`,`106ca48`,`05aea2d`
- **🎯 Onboarding UX (จาก feedback ผู้ทดสอบจริง 2 คน):** soft-gate checklist worker+employer dashboard · apply-gate modal แทน error ดิบ · `_pendingApplyJobId` ย้าย sessionStorage (รอด F5) · แก้บั๊ก multi-skill overwrite (ตอนนี้ accumulate สูงสุด 3 + chip UI) · ลบฟอร์มสร้าง employer profile ซ้ำที่ไม่มาตรฐาน · ปุ่ม verify employer กลับมาทำงาน
- **🔒 Security Audit รอบ 2:** ตรวจ auth/SQL injection(217 query)/IDOR(18 endpoint)/XSS(64 จุด)/upload — ไม่มี Critical · แก้แล้ว CORS null origin + admin secret timing-safe · เหลือ rate-limit register/upload (🟡 ต่ำ) → `security_audit_2026-07-22.md`
- **🧭 PDPA:** `POLICY_VERSION` refactor เป็น constant เดียว · design consent modal ใหม่ (เปิด+tickbox อิสระ แทน forced-scroll) เคาะแล้ว ยังไม่ implement
- **🤖 ทดสอบ bridge sub-agent (read-only):** ให้ Claude Code วิเคราะห์ `index.html` เตรียม React Native (Phase 3) → `RN_MIGRATION_MAP.md` (logic reuse ได้ vs DOM ต้องเขียนใหม่ vs 62 endpoints vs state redesign) · verify แล้วไม่แตะโค้ดจริง — พิสูจน์ pattern "Opus คุมสโคป → Sonnet/bridge ทำ read-only → review" ใช้ได้จริง
- **📄 เอกสารใหม่:** `PARKED_gate2.md` (ของที่ตั้งใจ park ทุกข้อมี "เปิดเมื่อ") · `DECISION_availability_gps.md` · `tools/gen_map.py`+`INDEX_MAP.md`+`COUPLING_MAP.md` (navigation tooling กัน Claude อ่านไฟล์ใหญ่มั่ว) · `launch/07_HR_CALL_CHECKLIST.md` · `launch/08_USER_TEST_SHEET.html`
- **⚠️ ค้าง:** revoke GitHub token (founder) · โทร HR โรงแรม · ให้ผู้ทดสอบเทสจริง (ปลดล็อก guided-tour/grid-vs-map decision) · earnings-screen routing bug (1 บรรทัด เจอจาก RN map แต่ยังไม่แก้)
- รายละเอียดเต็ม → **`HANDOFF_2026-07-24.md`**
