# WeHire — Progress & Roadmap
อัปเดต: 21 พฤษภาคม 2568

---

## ✅ สิ่งที่ทำเสร็จแล้ว

### Infrastructure
- [x] Supabase PostgreSQL + PostGIS setup (supabase_setup_full.sql)
- [x] FastAPI + asyncpg connection pool (lifespan)
- [x] JWT Auth (register / login / middleware)
- [x] bcrypt password hashing (cost=12)
- [x] CORS configuration
- [x] .env management (pydantic-settings)
- [x] Health check endpoint

### Auth
- [x] POST /auth/register (worker / employer)
- [x] POST /auth/login
- [x] GET /auth/me

### Worker
- [x] GET/POST/PATCH /workers/profile/me
- [x] GET /workers/applications (พร้อม maps_link ถ้า hired)

### Employer
- [x] GET/POST/PATCH /employers/profile/me

### Jobs
- [x] POST /jobs
- [x] GET /jobs/mine
- [x] PATCH /jobs/{id}/status (open/closed)

### Matching Engine
- [x] GET /jobs/nearby (PostGIS radius + skill filter + scoring)
- [x] POST /jobs/{id}/apply (match score: skills 60% / distance 25% / rate 15%)
- [x] GET /jobs/{id}/candidates (ranked list)
- [x] PATCH /applications/{id}/decide (hired/rejected/shortlisted)
- [x] Auto-generate Google Maps navigation link เมื่อ hired
- [x] Notification system (insert to notifications table)

### Review System
- [x] DB schema (reviews, review_tags, review_tag_selections, summaries)
- [x] Migration: 004_review_star_rating.sql
- [x] GET /review-tags
- [x] POST /reviews (blind review, auto-reveal เมื่อทั้งคู่ส่ง)
- [x] GET /reviews/me
- [x] GET /reviews/pending

### Frontend (index.html)
- [x] Auth page (login / register)
- [x] Worker flow: หางานใกล้บ้าน, ประวัติสมัคร, โปรไฟล์
- [x] Employer flow: โพสต์งาน, งานของฉัน, ดูผู้สมัคร, จ้าง/ปฏิเสธ
- [x] Google Maps Places autocomplete
- [x] GPS location
- [x] Review UI (⭐ ดาว + tag buttons + blind review)
- [x] Debug console

---

## 🔧 กำลังทำ / แก้ไขต่อไป

### UX Improvements (ตกลงในแชทนี้)
- [ ] Skills input เปลี่ยนเป็น dropdown (skill 1, 2, 3 แยก field)
- [ ] หน้า "หางานใกล้บ้าน" — zone dropdown แทน free text
- [ ] Carrier/ประเภทงาน dropdown

---

## 📋 Roadmap ที่แนะนำ

### Phase 1 — UX Polish (ทำต่อเลย)
- [ ] Skills dropdown (3 slots) แทน free-text input
- [ ] Zone/area dropdown ในหน้าค้นหางาน
- [ ] Job category dropdown (โรงงาน / คลังสินค้า / ร้านค้า / ก่อสร้าง / อื่นๆ)
- [ ] Worker profile — เพิ่มรูปโปรไฟล์ (Supabase Storage)
- [ ] Notification badge ใน sidebar (แสดงจำนวนที่ยังไม่อ่าน)

### Phase 2 — Trust & Safety
- [ ] Background check flow (mock → real integration)
- [ ] Employer verification flow
- [ ] Report/block user system
- [ ] Review summary แสดงบน worker/employer profile card

### Phase 3 — Wallet & Payment
- [ ] Wallet schema (transactions, balances)
- [ ] Escrow flow: employer deposit → release เมื่องานเสร็จ
- [ ] Worker withdrawal request
- [ ] PromptPay integration (หรือ Omise/2C2P)

### Phase 4 — Scale & Production
- [ ] Dockerize (Dockerfile + docker-compose)
- [ ] Deploy to Railway / Render / AWS
- [ ] Custom domain + HTTPS
- [ ] pg_cron: reveal reviews hourly, expire old jobs
- [ ] Rate limiting (per IP / per user)
- [ ] Logging + monitoring (Sentry / Grafana)
- [ ] Push notifications (LINE Notify หรือ Firebase FCM)

### Phase 5 — Growth Features
- [ ] Worker แชทกับ Employer (หลัง hired เท่านั้น)
- [ ] Job recommendation engine (ML-based)
- [ ] Worker availability calendar
- [ ] Multi-zone posting
- [ ] Referral system

---

## 🗂️ ไฟล์ปัจจุบัน

| ไฟล์ | สถานะ |
|------|--------|
| main.py | ✅ production-ready |
| index.html | ✅ MVP complete |
| supabase_setup_full.sql | ✅ run แล้ว |
| 003_review_system.sql | ✅ run แล้ว |
| 004_review_star_rating.sql | ⚠️ ยังไม่ได้ run — ต้อง run ใน Supabase |
| requirements.txt | ✅ |
| .env | ✅ (ไม่ commit ขึ้น git) |

---

## ⚠️ สิ่งที่ต้องระวัง

1. **004_review_star_rating.sql** — ยังไม่ได้ run ใน Supabase → Review system จะยังใช้ไม่ได้
2. **Google Maps API Key** — อยู่ใน index.html แบบ hardcode → ควรย้ายไป backend หรือ restrict domain ใน Google Console
3. **JWT Secret** — ต้องแข็งแรงพอ (32+ chars) และไม่ leak
4. **bcrypt** — ถ้า user เก่า (ก่อน main.py ใหม่) password hash อาจเสีย → ให้ register ใหม่
