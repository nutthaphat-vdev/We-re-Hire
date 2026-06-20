# We're Hired — Progress & Roadmap
> **"ทำงานวันนี้ เสร็จงานได้เงินทันที"**

อัปเดต: 31 พฤษภาคม 2568

---

## 🧭 Strategy — ภาพรวมที่ต้องจำไว้เสมอ

> บันทึก 18 มิถุนายน 2568

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

## ✅ Production — Live แล้ว

### 🔧 Infrastructure
- [x] Supabase PostgreSQL + PostGIS setup
- [x] FastAPI + asyncpg connection pool (PgBouncer transaction mode)
- [x] JWT Auth middleware (HS256 — token ของเราเอง)
- [x] Google OAuth via Supabase — verify ด้วย JWKS + ES256
- [x] bcrypt password hashing (cost=12)
- [x] CORS configuration (อ่านจาก env var + hardcode allowlist)
- [x] Health check endpoint
- [x] Deploy: Railway (backend) + Cloudflare Workers (frontend)
- [x] GitHub Actions auto-deploy — push → Cloudflare อัตโนมัติ ✅ live
- [x] **Rename Worker** → `wearehiredmvp` — URL ใหม่: `wearehiredmvp.vi-nutthaphat.workers.dev`
- [x] **Production URL Change Checklist** — บันทึกใน CLAUDE.md ครบ 8 ขั้นตอน (เพิ่ม Railway Source Repo)
- [x] **Railway service migration** — ย้ายจาก `web-production-03c5a` → `web-production-1db39` (หลังย้าย GitHub account)
- [x] **GitHub repo ย้ายบัญชี** → `nutthaphat-vdev/We-re-Hire` (PAT revoke + reconnect Railway Source)
- [x] **Backend URL อัปเดตครบ** — index.html, CLAUDE.md ชี้ไป `web-production-1db39` แล้ว

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
- [x] เปิดเผยเบอร์โทร + email ตลอด lifecycle `hired → verified` (Contact Lock)

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

### 🔐 Security (Audited 26 พ.ค. 2568 — Claude Sonnet 4.6)
- [x] **Security Audit ผ่าน** — 4 CRITICAL / 7 WARNING / 6 INFO ทุกจุด
- [x] **XSS Protection** — `esc()` ทุก user-input ใน innerHTML (job title, name, skills, notif body, contact info)
- [x] **Auto-ban ลบออก** — `logger.warning` แทน + admin review
- [x] **Contact reveal ใช้ได้ตลอด lifecycle** — `hired → checked_in → working → completed → verified`
- [x] **`/docs` ปิดใน Railway production** — enumerate admin endpoints ไม่ได้
- [x] **CORS URL เก่าลบออก** — `divine-bar-29c7` subdomain ไม่อยู่ใน allowlist แล้ว
- [x] **Email ไม่รั่ว** — ลบ `u.email` ออกจาก `GET /users/blocked` response
- [x] **Review ส่งได้หลัง verified/disputed** — แก้ logic bug `status = 'hired'` → `IN ('hired','verified','disputed')`

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
- [x] **Multi-language UI (TH/EN)** — ไทย / English (MM ถอดออก ไม่เหมาะ pitch)
- [x] **i18n ครอบคลุมทุกหน้า** — sidebar, dashboard, nearby, myapps, myjobs, candidates, notifications, profile
- [x] Language preference เก็บใน localStorage (`wh_lang`)
- [x] **Language toggle** — ย้ายออกนอก token box, อยู่ด้านล่าง nav items, text-only TH/EN (ไม่มี flag)
- [x] **Work Permit section** บน worker profile — badge, link เอกสาร, คำเตือนใกล้หมดอายุ (< 30 วัน), error ถ้าหมดแล้ว
- [x] Nationality selector ใน edit profile form — ไทย / ต่างด้าว

### 🔒 Auto-Withdraw Overlap
- [x] `PATCH /applications/{id}/decide` — เมื่อ hire แล้ว auto-withdraw applications อื่นของ worker คนเดียวกันที่วันซ้อนทับ
- [x] Batch UPDATE + RETURNING + Batch INSERT notifications — O(1) queries ไม่ว่าจะมี overlap กี่ใบ
- [x] Notify employer ที่ได้รับผลกระทบทันที

### 📱 Mobile Responsive
- [x] Hamburger ☰ button บนมุมบนซ้ายเมื่อ screen < 768px
- [x] Sidebar slide in จากซ้าย (position:fixed) + overlay สีดำ semi-transparent
- [x] `.main` width 100% บน mobile
- [x] Font-size, card padding, stat grid, form-row ลดลงบน mobile

### 🛡️ Admin Dashboard
- [x] `require_admin` JWT dependency — role='admin' check
- [x] `GET /admin/stats` — 9 platform metrics ใน single query
- [x] `GET /admin/users?role=&status=&page=` — paginated user list
- [x] `PATCH /admin/users/{id}/status` — active/suspended/banned
- [x] `GET /admin/kyc/pending` — list workers รอ KYC review + signed URLs
- [x] `PATCH /admin/kyc/{id}/review` — verified/failed + notify worker
- [x] `GET /admin/disputes` — list disputed applications
- [x] `PATCH /admin/disputes/{id}/resolve` — worker_win/employer_win + notify ทั้งคู่
- [x] `GET /admin/jobs?status=&page=` — list all jobs
- [x] `PATCH /admin/jobs/{id}/status` — close/reopen/expire
- [x] Frontend: Admin nav section (ซ่อนถ้าไม่ใช่ admin)
- [x] Frontend: 5 หน้า admin (stats/users/kyc/disputes/jobs)
- [x] Admin user สร้างแล้วใน DB (`admin@wehire.th`)

### 🪪 KYC Photo Upload
- [x] `POST /workers/kyc/upload` — multipart face_photo + id_card_photo → Supabase Storage
- [x] Validate: JPG/PNG/WebP เท่านั้น, ขนาดไม่เกิน 5MB ต่อไฟล์
- [x] Path: `kyc/{worker_id}/face.jpg` / `kyc/{worker_id}/id_card.jpg`
- [x] UPDATE `face_photo_url`, `id_card_photo_url`, `kyc_submitted_at`, `background_check_status='pending'`
- [x] `GET /admin/kyc/pending` — signed URLs (expire 1h) สำหรับแต่ละรูป
- [x] Frontend worker profile: upload form (status='pending') + file preview
- [x] Frontend admin KYC: thumbnails คลิกดูขนาดใหญ่ได้
- [x] Migration 014_kyc_photos.sql: `face_photo_url`, `id_card_photo_url`
- [x] requirements.txt: `supabase==2.10.0`, `python-multipart==0.0.9`

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
| 013_job_expiry.sql | ✅ |
| 014_kyc_photos.sql | ✅ |

---

## 🔧 ต้องทำต่อ (งาน Manual)

- [x] **GitHub Secrets** — `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID` ✅ 2026-05-24
- [x] **GitHub PAT** — scope `workflow` เพิ่มแล้ว, CI pipeline active ✅ 2026-05-24
- [ ] **Review summary** — ดาวเฉลี่ย + top tags แสดงบน profile card
- [ ] **Contact button reload** — ปุ่ม 📞 โผล่ทันทีหลังกด hired โดยไม่ต้อง refresh

### 🔐 Security Hardening (ก่อน Scale / หลัง Pitch)
- [ ] **Rate limiting** (slowapi) — W1: brute force `/auth/login`, spam `/apply`
- [ ] **JWT expire ลดเป็น 120 นาที** — C2: ลดหน้าต่าง token theft
- [ ] **`is_active` check ใน `get_current_user`** — W7: banned user ใช้ token เก่าไม่ได้ทันที
- [ ] **Security headers ใน worker.js** — I1: CSP, X-Frame-Options, X-Content-Type-Options
- [ ] **Column allowlist ใน dynamic SQL** — W5: explicit whitelist ป้องกัน dev ใหม่ inject field

---

## 📋 Roadmap

### Phase 2A — KYC Level 1 (Free) 🪪
> ยืนยันตัวตนด้วยบัตรประชาชน / Passport + Selfie — admin verify มือ, ฟรี 100%

**ทำแล้ว ✅**
- [x] Migration: 010_kyc.sql — 12 columns (nationality_type, kyc docs, review tracking)
- [x] Work Permit enforcement — block apply ถ้า foreign worker ไม่มีหรือหมดอายุ (403)
- [x] Work Permit section บน worker profile card + expiry warning < 30 วัน
- [x] Multi-language UI 🌐 TH/EN — ครอบคลุมทุกหน้า (MM ถอดออก ไม่เหมาะ pitch)
- [x] `POST /workers/kyc/upload` — face_photo + id_card_photo → Supabase Storage
- [x] `GET /admin/kyc/pending` + `PATCH /admin/kyc/{id}/review` (verified/failed + note)
- [x] Admin KYC page พร้อม photo thumbnails + signed URLs

**ยังต้องทำ**
- [ ] Badge **✓ KYC Verified** แสดงบน profile card + candidate list หลัง admin approve
- [ ] Cron รายวัน: Work Permit expiry alert + auto-reject ถ้า expired
- [ ] รูปโปรไฟล์ worker (Supabase Storage)
- [ ] Employer verification flow
- [ ] **Supabase bucket `kyc-documents`** ต้องสร้างด้วยมือ + ตั้ง `SUPABASE_SERVICE_KEY` ใน Railway

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

### Phase 4B — Voice-First Onboarding 🎙️
> แก้ pain point หลักของ daily wage worker — อ่านหนังสือไม่คล่อง / ไม่ถนัด smartphone
> ต้นทุน API ต่ำมาก (~$0.02–0.05/user ตลอด onboarding) เพราะ conversation สั้น

**Core Flow:**
```
Worker กรอกไม่ถูก / สับสน
→ กด Live Chat (floating button)
→ AI ถามทีละขั้น + พูดออกเสียงให้ฟัง (TTS)
→ Worker ตอบด้วยเสียง (STT) หรือพิมพ์ก็ได้
→ AI interpret → กรอก form ให้อัตโนมัติ
→ เสนอ action เชิงรุก เช่น "พรุ่งนี้ว่าง → ทำตารางสมัครงานเลยไหม?"
```

**OCR บัตรประชาชน:**
```
Worker ถ่ายบัตรประชาชน → Haiku vision → extract ชื่อ/นามสกุล/เลขบัตร/วันเกิด
→ กรอก profile form ให้อัตโนมัติ — worker แค่กด confirm
ต้นทุน: ~$0.002/ครั้ง (ทำครั้งเดียวตอน onboard)
```

**STT/TTS Stack:**
| ฟีเจอร์ | วิธีทำ | Cost |
|---------|--------|------|
| Speech-to-Text | Web Speech API (browser native) | ฟรี |
| Text-to-Speech | Web Speech Synthesis API (browser native) | ฟรี |
| AI interpret + respond | Haiku | ~$0.001–0.003/message |
| Fallback STT (ถ้า browser ไม่รองรับ) | Whisper API | ~$0.006/นาที |

**⚠️ Risk ที่ต้องทดสอบ:**
- Web Speech API รองรับภาษาไทยสำเนียงต่างจังหวัด / สำเนียงต่างด้าวได้แค่ไหน
- ถ้า STT accuracy ต่ำ → fallback เป็น text input พร้อม AI guide แทน

**Tasks:**
- [ ] Prototype live chat widget (floating button → chat drawer)
- [ ] OCR บัตรประชาชน: Haiku vision → auto-fill profile fields
- [ ] Voice input: Web Speech API → Haiku → interpret intent → action
- [ ] TTS: AI ถาม/ตอบออกเสียง ให้ worker ฟังแทนอ่าน
- [ ] Proactive suggestion: เช่น detect "ว่าง" → เสนอ "สมัครงานเลยไหม?"
- [ ] ทดสอบ STT กับสำเนียงไทย (อีสาน/เหนือ/ใต้) + ภาษาเมียนมา/ลาว

### Phase 4C — Full-Time Job Board 📋
> ขยาย platform จาก "หางานวันนี้" → "หางานประจำ" ในแอพเดียวกัน
> ใช้ฐาน employer เดิมที่มีอยู่แล้ว — upsell โดยไม่ต้อง CAC ใหม่

**Product Vision:**
- Worker เห็น 2 tab: **"งานรายวัน"** | **"งานประจำ"**
- Employer โพสต์งานประจำได้ในหน้าเดิม — เลือก type = `full_time`
- Platform ดูแข็งแกร่งขึ้น — ไม่ใช่แค่ gig economy แต่เป็น full employment platform

**Revenue Model:**
- Flat fee โพสต์งานประจำ (ไม่มี % transaction)
- เป้า: ฿500–1,500/โพสต์ (SME/โรงงาน จ่ายง่าย vs headhunter ที่แพงกว่า 10x)
- ไม่ต้องการใบอนุญาตพิเศษ (ต่างจาก Phase 5 HH)

**Difference จากงานรายวัน:**
| | งานรายวัน | งานประจำ |
|--|----------|----------|
| ระยะสัญญา | 1 วัน – 1 เดือน | 3 เดือนขึ้นไป |
| ค่าจ้าง | รายวัน (฿/วัน) | รายเดือน (฿/เดือน) |
| Matching | AI score + GPS | Resume/profile match |
| Employer จ่าย | % per hire | Flat posting fee |
| Checkin/GPS | ✅ required | ❌ ไม่มี |
| Escrow | ✅ Phase 3 | ❌ ไม่มี (จ่ายตรง) |

**DB Changes:**
```sql
ALTER TABLE job_postings
  ADD COLUMN IF NOT EXISTS job_type VARCHAR(20) DEFAULT 'daily'
    CHECK (job_type IN ('daily', 'full_time', 'part_time'));
-- full_time: salary_min/salary_max แทน daily_rate
-- แสดงผลแยก tab ใน frontend
```

**Tasks:**
- [ ] `job_type` column + migration
- [ ] Frontend: tab switch "งานรายวัน / งานประจำ" บนหน้า Find Job
- [ ] Employer: form ใหม่สำหรับโพสต์งานประจำ (salary range, job description, benefits)
- [ ] Worker: resume/skills profile เพิ่ม expected_salary, work_experience
- [ ] Matching สำหรับงานประจำ (skills + salary range — ไม่มี GPS requirement)
- [ ] Payment: flat posting fee flow (Phase 3 wallet หรือ PromptPay direct)
- [ ] Admin: approve งานประจำก่อน publish (quality control)

### Phase 4D — Smart Calendar 📅
> Two-sided calendar — Worker เห็นงานใกล้ตัว, Employer วางแผนธุรกิจ + โพสต์งานได้เลย

**Worker View — "งานใกล้ฉัน วันนี้/พรุ่งนี้":**
```
เปิด Calendar → เห็น 2–3 วันข้างหน้า
→ แต่ละวันแสดง top 5 งานใกล้ที่สุด (sort: distance ASC)
→ ถ้ามีงานรอ 10 อัน → แสดง 5 ก่อน + "ดูเพิ่มเติม"
→ กดการ์ดงาน → apply ได้เลยใน 1 tap
→ วันที่ worker มีงาน hired แล้ว → block สีเขียว (ไม่แสดงงานอื่น)
```

**Employer View — "วางแผนธุรกิจ":**
```
เปิด Calendar → เห็น timeline งานที่โพสต์แล้วทั้งหมด
→ วันที่มีคนครบ → สีเขียว ✅
→ วันที่ยังขาดคน → สีส้ม ⚠️ + แสดงจำนวนที่ขาด
→ วันที่ยังไม่ได้โพสต์งานเลย → สีเทา (ว่าง)
→ กดวันที่ว่าง/ขาดคน → เปิด quick job post form ทันที
```

**Key Insight:**
- Worker: ไม่ต้องค้นหาเอง — งานมาหา ตามวันที่ว่าง
- Employer: เห็น gap ในธุรกิจชัดเจน → โพสต์งานเร็วขึ้น → fill rate สูงขึ้น
- Platform: เพิ่ม job posting frequency โดยธรรมชาติ

**DB Changes:**
```sql
-- ไม่ต้องเพิ่ม table ใหม่ — ใช้ job_postings.start_date + slot_filled ที่มีอยู่
-- เพิ่ม index สำหรับ calendar query:
CREATE INDEX IF NOT EXISTS idx_jobs_start_date_status
  ON job_postings(start_date, status)
  WHERE status = 'open';
```

**Tasks:**
- [ ] Worker calendar: weekly view + top 5 nearby jobs per day (sort distance)
- [ ] Worker: 1-tap apply จาก calendar card
- [ ] Worker: วันที่ hired แล้ว → block + แสดง job ที่ confirm ไว้
- [ ] Employer calendar: monthly/weekly view + color coding (ครบ/ขาด/ว่าง)
- [ ] Employer: quick post form เมื่อกดวันที่ว่าง
- [ ] Employer: "ขาดอีก N คน" badge บนแต่ละวัน
- [ ] Sync: worker accept → employer calendar อัปเดต slot ทันที
- [ ] **GeoPosting**: employer กดวันว่างใน calendar → เห็น available workers บนแผนที่รัศมี X km
  - ใช้ PostGIS `ST_DWithin` เดิม — query กลับทิศ (workers → job location แทน)
  - แสดง worker pins บนแผนที่ พร้อม match score + KYC badge
  - กด pin → ดู profile → invite / โพสต์งานเจาะจงรัศมีนั้น

### Phase 5 — AI Headhunter Mode 🎯
> ใช้ data ที่สะสมมาจาก daily wage + งานประจำ + behavioral score
> WeHire รู้จัก worker จริงกว่า headhunter ทั่วไปที่ดูแค่ resume

**Insight หลัก:**
- Headhunter ทั่วไป: รู้จาก CV + interview → เดา
- WeHire: รู้จากพฤติกรรมจริง — มาตรงเวลา, ทำงานครบ, employer review, no-show rate → วัดได้จริง

**Data ที่มีอยู่แล้ว (ไม่ต้องเก็บใหม่):**
```
reliability_score  — completion rate, no-show, review avg
job history        — ทำงานประเภทไหน, กี่ครั้ง, กับ employer ไหน
behavioral pattern — checkin ตรงเวลา, OT รับได้ไหม, ระยะทางยอมเดินทางไกลแค่ไหน
skill match history — skill ไหน match แล้วงานสำเร็จจริง
```

**AI Headhunter Flow:**
```
Employer โพสต์ตำแหน่งระดับสูง (ผ่าน Full-time Job Board)
→ WeHire AI วิเคราะห์ data ทั้งหมด → recommend top 3–5 candidates
→ พร้อม reasoning: "คนนี้ทำงานกับ logistics 47 ครั้ง, completion 98%, ไม่เคย no-show"
→ Employer จ่าย HH fee เมื่อ hire สำเร็จ (15–20% เงินเดือนเดือนแรก)
```

**ต้องมีก่อน implement:**
- [ ] ใบอนุญาตจัดหางานในประเทศ (5,000 บาท/2 ปี — กรมการจัดหางาน ดินแดง)
- [ ] Track record พอ + employer trust สูงพอ
- [ ] Data สะสมครบ (Phase 2B behavioral score ต้อง live ก่อน)

**Tasks:**
- [ ] AI scoring model สำหรับ headhunter tier (Sonnet)
- [ ] Employer HH request flow + fee model
- [ ] Candidate recommendation engine พร้อม reasoning
- [ ] HH fee payment + escrow

### Phase 6 — Notifications & Communication
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
| WeHired_DarkFlyer.html | ใบปลิว GTM — Dark theme (Facebook/LINE) | ✅ |
| WeHired_LightFlyer.html | ใบปลิว GTM — Light theme (พิมพ์แจก A4) | ✅ |
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

## ✅ Day 6 — 30 พฤษภาคม 2568 · วัน Business Strategy + Job Expiry

### 💼 Job Auto-Close System (Migration 013)
- [x] Migration: `013_job_expiry.sql` — ADD COLUMN `auto_close_at`, `auto_closed_reason` + partial index
- [x] `POST /jobs` — คำนวณ `auto_close_at` อัตโนมัติ: start_date - 48h หรือ NOW() + 7d
- [x] Cron `check_expired_jobs` รันทุก 30 นาที:
  - ไม่มีผู้สมัครเลย → reason = `no_applicants`
  - มีผู้สมัครแต่ไม่ hire → reason = `no_hire`
  - auto-close + notify employer พร้อมเหตุผล + TODO refund hook (Phase 3)
- [x] `GET /jobs/mine` — เพิ่ม `auto_close_at`, `auto_closed_reason` + return ทุก status
- [x] `POST /admin/cron/trigger` — trigger ทั้ง `auto_verify` + `check_expired_jobs` ใน call เดียว
- [x] Frontend: hint "⏰ งานจะปิดอัตโนมัติ..." เมื่อเลือก start_date
- [x] Frontend: countdown badge ⏳ สีส้ม + reason badge สีเทาหลัง auto-close

### 💰 Revenue Streams & Business Roadmap (บันทึกใน CLAUDE.md)
- [x] Work Permit Service — ราคาขาย 10,000 บาท, margin ~7,500 บาท/คน (verified กรมการจัดหางาน)
- [x] White Collar Job Board — Phase 3, upsell ฐาน employer เดิม
- [x] Headhunter (HH) — Phase 5, ใบอนุญาตจัดหางาน 5,000 บาท/2 ปี
- [x] Key insight: Rotation market = employer ต้องกลับมาใช้ platform เสมอ
- [x] Key insight: Work permit = Lock-in mechanism ที่แข็งแกร่งที่สุด

### 🔧 ต้องทำต่อ (เพิ่มเติม)
- [x] **Mobile Responsive** ✅ — hamburger + sidebar slide + smaller content < 768px
- [x] **Run 013_job_expiry.sql** ✅ run แล้ว
- [x] **Run 014_kyc_photos.sql** ✅ run แล้ว
- [x] **Supabase bucket `kyc-documents`** ✅ 2026-06-01
- [x] **เปลี่ยน admin password** ✅ 2026-06-01
- [x] **SUPABASE_SERVICE_KEY** ตั้งใน Railway ✅ 2026-06-01
- [ ] **claude-bridge MCP** — ลบ `run_command` + เพิ่ม auth token + reconnect

## ✅ Day 7 — 1 มิถุนายน 2568 · วัน MCP Setup

- [x] **MCP wehire-fs** — ติดตั้ง `@modelcontextprotocol/server-filesystem` ผ่าน Claude Desktop config ✅
- [x] **Claude Desktop เชื่อมต่อ filesystem ได้แล้ว** — read_file, write_file, list_directory ทำงานได้ที่ `C:\Users\User\Downloads\Hire`

## ✅ Day 8 — 2 มิถุนายน 2568 · วัน Pre-Pitch Polish + Bug Fixes

### 🎯 W1 — KYC Badge + Profile Photo
- [x] **Backend**: เพิ่ม `profile_photo_url` ใน candidates query (JOIN `worker_review_summary`)
- [x] **Backend**: `WorkerOut` / `WorkerPublicOut` schemas เพิ่ม `profile_photo_url`
- [x] **Backend**: `worker_service.py` SELECT ครบทุก query (get_my_profile, get_worker_public, create, update)
- [x] **Frontend**: Candidate card — avatar แสดงรูปจริง + ✓ KYC badge สีเขียวติดชื่อ
- [x] **Frontend**: Worker profile page — avatar แสดงรูปจริง
- [x] **Frontend**: Badge ซ่อนถ้า verified แล้ว (ไม่แสดง status text ซ้ำ)

### 📊 W2 — Admin Dashboard Redesign
- [x] **Backend**: `/admin/stats` เพิ่ม 6 metrics ใหม่: `total_completed`, `total_hired_alltime`, `completion_rate_pct`, `avg_time_to_hire_hours`, `new_users_today`, `jobs_posted_today`
- [x] **Backend**: `/public/stats` endpoint ใหม่ (ไม่ต้อง auth) สำหรับ landing page
- [x] **Frontend**: Admin dashboard redesign — 3 rows: KPI stats → performance metrics (completion rate / time-to-hire / jobs) → action required (KYC + disputes) พร้อม color coding

### 🛡️ W3 — Security Hardening
- [x] **worker.js**: Security headers ครบ — CSP, X-Frame-Options: DENY, X-Content-Type-Options: nosniff, Referrer-Policy, Permissions-Policy
- [x] **worker_service.py**: Column allowlist + validation ก่อนสร้าง dynamic SET clause ป้องกัน SQL injection

### 🏠 Landing Page Redesign
- [x] Landing page เป็น full-scroll (5 sections): Hero → Stats bar → How it works → Key features → Market context + Footer CTA
- [x] Stats bar ดึง live data จาก `/public/stats` API
- [x] How it works: Worker flow vs Employer flow คู่กัน 3 steps each
- [x] Key features: 6 cards (Anti-ghosting, GPS, Blind review, KYC, AI Match Score, D-1 Reminder)
- [x] Market context: 5M+ workers / ฿400/วัน / 90% ยังไม่ใช้ platform

### 🎨 Dashboard Redesign (Worker + Employer)
- [x] **Worker**: Greeting ชื่อจริง + 3 stats จริง (รอผล / ได้รับ / สำเร็จ) + active jobs widget + KYC nudge + 4 quick actions
- [x] **Employer**: Greeting ชื่อบริษัท + 3 stats + active jobs list กด direct เข้า candidates + verify nudge
- [x] **Employer verification badge**: ✅ Verified / ⏳ รอ Admin / ⚠️ ยังไม่ verified พร้อมปุ่ม

### 🎨 UI Redesign — ทุกหน้า
- [x] **Find Job**: job card ใหม่ — match score ตัวเลขใหญ่สีตาม threshold, meta เป็น chip, apply full-width
- [x] **Applications**: แยก active vs history, left border สีตาม status, match score circle, disputed orange box
- [x] **Notifications**: icon circle สีตาม type, unread มี accent left border + tint
- [x] **Reviews**: stars 32px, received reviews แสดงดาว + tags chip, would_rehire badge
- [x] **Worker Profile**: header gradient, stats 3-col grid, skills chip, edit button ย้ายขึ้น header
- [x] **Candidate card**: review stars ⭐ + avg score + รีวิว count + % รับอีก (จาก `worker_review_summary`)

### 🐛 Bug Fixes
- [x] **check_expired_jobs cron**: `NameError: total_hired` — ทำให้ auto-close ไม่ทำงานเลย ✅ fixed
- [x] **check_noshow_workers cron**: ปรับ alert +10 นาที (เดิม +30), auto no-show +30 นาที (เดิม +60)
- [x] **check_noshow_workers cron**: `start_date = today` → `start_date <= today` — จับงานค้างจากวันก่อน
- [x] **check_noshow_workers cron**: งานไม่มี `work_start` → fallback 08:00 Thai time
- [x] **check_noshow_workers cron**: Auto backup offer อัตโนมัติหลัง no-show (top match_score candidate)
- [x] **check_noshow_workers cron**: per-row try/except ป้องกัน 1 job crash หยุด cron ทั้งหมด
- [x] **JS syntax error**: `onclick="showContact('' + a.id...)"` → escape quote ถูกต้อง
- [x] **index.html truncation**: ไฟล์ขาด `</html>` หลาย episode — restore จาก git + Python patch
- [x] **requirements.txt**: bust Railway pip cache (เปลี่ยน comment วันที่)

### 🎤 Pitch Deck (Canva)
- [x] เชื่อมต่อ Canva MCP connector
- [x] แก้ 5 content issues: Roadmap Phase 5→4, Traction ⬜→🔜/🗺️, on-chain proof→fully logged, Team duplicate, SOM formula +12 เดือน
- [x] คิด tagline ใหม่: **"The Right Worker. Right Now. Right Here."**

---

## ✅ Day 9 — 15 มิถุนายน 2568 · Repo Hygiene + Map Pin Fix

### 🔐 Repo Hygiene
- [x] **GitHub PAT** "we re hire" ใกล้หมดอายุ → regenerate token + อัปเดต git remote URL
- [x] **`.env` ถูก track ใน git** → `git rm --cached .env` + commit (repo เป็น Private อยู่แล้ว, ความเสี่ยงต่ำ)
- [x] ลบ `__pycache__/main.cpython-312.pyc` ที่ค้างอยู่
- [x] Commit doc updates ค้าง (CHANGELOG.md, CLAUDE.md, PROGRESS.md) → push `ee4365d`

### 📍 Map Location Pinning Fix (index.html)
- [x] **Bug**: หน้า post job — พิมหาที่อยู่ได้ (Places Autocomplete ทำงาน) แต่ **ลากหมุดปรับตำแหน่งไม่ได้**
- [x] **Fix**: `showMapPreview()` — เพิ่ม `draggable: true` ให้ marker
- [x] เพิ่ม `dragend` listener — ลากหมุดแล้ว reverse geocode อัปเดต lat/lng + ที่อยู่ที่แสดง
- [x] เพิ่ม `click` listener บนแผนที่ — คลิกจุดไหนหมุดย้ายไปจุดนั้นทันที
- [x] เปลี่ยน marker icon จากวงกลมเขียว → เข็มหมุดสีแดง (teardrop pin)
- [x] ใช้ร่วมกันทั้ง 3 จุด: post job, search location, create worker profile
- [x] Push `d2f0a46` → Cloudflare auto-deploy → ทดสอบแล้วใช้งานได้ ✅

⚠️ **Note**: reverse geocode เรียก Google Geocoding API ทุกครั้งที่ลาก/คลิกหมุด — cost เล็กน้อย อยู่ใน free tier ปกติ

---

## ✅ Day 10 — 19 มิถุนายน 2568 · Bilingual i18n

### 🌐 Full Bilingual Support (TH/EN)
- [x] **i18n architecture**: LANG object (`th`/`en`) + `t('key')` function + `data-i18n` on static HTML + `setLang()` re-renders dynamic pages
- [x] **Lang toggle**: Flag images (🇹🇭 🇺🇸) via flagcdn.com — absolute top-right on landing page, no border/box
- [x] **Landing page** — ทุก section (hero, stats bar, how-it-works worker/employer flows, key features, market context, footer CTA)
- [x] **Notifications page** — title, badges, buttons, read state
- [x] **Find Jobs page** — title, radius, search button, map labels
- [x] **My Applications page** — title, section headers, status labels
- [x] **My Reviews page** — pending/received headers, star form, rehire buttons, empty state
- [x] **Worker Profile page** — title, stats grid, KYC section, edit form labels
- [x] **Post Job page** — title + all 16 form labels
- [x] **My Jobs page** — title, status badges, auto-close reason labels
- [x] **Employer Dashboard** — stats, open jobs list, verify nudge banner
- [x] **Employer create profile form** — labels + biz type dropdown options
- [x] **Candidates page** — all action buttons (hire/reject/checkin/verify/dispute/contact)
- [x] **Notification titles** — `_notifTranslateTitle()` map 24 Thai titles → English (frontend-only, no backend change)
- [x] **Review summary widget** — stars, count, rehire %
- [x] **Category / zone / title dropdowns** — dynamic, uses `name_en` when available
- [x] **`_autoCloseReasonLabel`** — changed const object → function (evaluates `t()` at call time)

### 🟡 i18n ยังเหลือ (ดู I18N_HANDOFF.md)
- [ ] Post job validation errors + success message
- [ ] Button state text (doCheckin, doComplete, doStart, doVerify, doDispute)
- [ ] Worker profile create form
- [ ] Session timeout buttons + login loading state
- [ ] Report modal
- [ ] Work permit status text
- [ ] Review validation + success message
- [ ] GPS / map status text
- [ ] Admin UI (low priority)

---

## Session 2026-06-20 — Anti-Ghosting Complete + Behavioral Score

### ✅ Anti-Ghosting Loop (ครบ 100%)
- [x] **Backup wage lock** — คำนวณ pro-rata เมื่อ no-show → employer confirm ก่อน cascade
- [x] **Distance-based cascade** — หา backup worker ที่ใกล้สุด ณ ขณะนั้น (ST_Distance)
- [x] **Auto-confirm 5 min** — employer ไม่กดใน 5 นาที → cascade อัตโนมัติ
- [x] **Backup worker เห็นค่าจ้าง** — `backup_confirmed_wage` lock ก่อนกด รับงาน
- [x] **Accept backup UI** — frontend banner + `doAcceptBackup()` function

### ✅ Behavioral Score System (017_behavioral_score.sql)
- [x] `jobs_hired + 1` เมื่อ **checkin** (ไม่ใช่ตอน employer กด hired — fair กับ worker)
- [x] `jobs_noshow + 1` เมื่อ cron auto no-show
- [x] `jobs_completed + 1` เมื่อ verified (backup worker ได้ด้วยแม้ทำแค่ 7 ชม.)
- [x] `reliability_score` recompute อัตโนมัติทุก trigger (0.00–10.00)

### ✅ Earnings Page
- [x] Sidebar worker: เมนู 💰 รายได้
- [x] Summary card: รายได้รวม + จำนวนงาน
- [x] Transaction list: ชื่องาน, บริษัท, วันที่, ฿ amount, backup badge

### ⚠️ Known Debt (Vibe Code)
- Earnings ตัวเลขคือ "ประมาณการณ์" ไม่ใช่ "รับจริง" — ดู CLAUDE.md Vibe Code Debt section
