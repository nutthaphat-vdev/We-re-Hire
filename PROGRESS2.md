# WeHire — Progress & Roadmap
อัปเดต: 22 พฤษภาคม 2568

---

## ✅ สิ่งที่ทำเสร็จแล้ววันนี้

### 🔧 Infrastructure
- [x] Supabase PostgreSQL + PostGIS setup
- [x] FastAPI + asyncpg connection pool
- [x] JWT Auth middleware
- [x] bcrypt password hashing (cost=12)
- [x] CORS configuration
- [x] Health check endpoint

### 🔐 Auth
- [x] POST /auth/register (email + password)
- [x] POST /auth/login
- [x] GET /auth/me
- [x] Google OAuth via Supabase (login + register)

### 👷 Worker
- [x] GET/POST/PATCH /workers/profile/me
- [x] GET /workers/applications
- [x] ปุ่ม 🗺️ นำทางไปงาน (เฉพาะ hired)
- [x] ปุ่ม 📞 ดูเบอร์ติดต่อ employer (เฉพาะ hired)

### 🏭 Employer
- [x] GET/POST/PATCH /employers/profile/me
- [x] ปุ่ม 📞 ดูเบอร์ worker (เฉพาะ hired)

### 💼 Jobs
- [x] POST /jobs
- [x] GET /jobs/mine
- [x] PATCH /jobs/{id}/status
- [x] Job categories cascade dropdown (4 หมวด, 16 ตำแหน่ง)

### 🎯 Matching Engine
- [x] GET /jobs/nearby (PostGIS radius + skill filter)
- [x] POST /jobs/{id}/apply (score: skills 60% / distance 25% / rate 15%)
- [x] GET /jobs/{id}/candidates (ranked)
- [x] PATCH /applications/{id}/decide
- [x] Auto Google Maps navigation link เมื่อ hired
- [x] Notification system

### 🔒 Contact Reveal
- [x] GET /applications/{id}/contact
- [x] เปิดเผยเบอร์โทร + email เฉพาะคู่ที่ hired เท่านั้น
- [x] กด tel: link โทรได้เลยจากแอพ

### ⭐ Review System
- [x] Blind review (ซ่อนจนทั้งคู่ส่ง หรือครบ 7 วัน)
- [x] 1-5 ดาว + tag buttons (ไม่มี free text)
- [x] Auto-reveal เมื่อทั้งคู่ส่ง
- [x] หน้า "รีวิวของฉัน" ใน sidebar

### 🗄️ Database Migrations (run แล้วทั้งหมด)
- [x] supabase_setup_full.sql
- [x] 003_review_system.sql
- [x] 004_review_star_rating.sql
- [x] 005_job_categories.sql

---

## 🔧 ต้องทำต่อ (ก่อน Present)

- [ ] Notification badge ใน sidebar
- [ ] หน้า Notifications list
- [ ] Review summary (ดาวเฉลี่ย + top tags) บน profile card
- [ ] ปุ่ม 📞 โผล่ทันทีหลังกด hired โดยไม่ต้อง reload
- [ ] Google Maps API Key — restrict domain ใน Google Console
- [ ] ngrok สำหรับ demo บน iPad

---

## 📋 Roadmap อนาคต

### Phase 1 — Polish MVP
- [ ] Notification badge + list
- [ ] Review summary บน profile
- [ ] Landing page อธิบาย product

### Phase 2 — Trust & Safety
- [ ] Background check flow
- [ ] Employer verification
- [ ] Report/block user

### Phase 3 — Wallet & Payment 💰
- [ ] Wallet + Escrow system
- [ ] Employer deposit → release เมื่องานเสร็จ
- [ ] Worker withdrawal
- [ ] PromptPay / Omise integration
- [ ] *** ตัวนี้แหละที่ทำให้ไม่มีใครโทรตรง เพราะเงินอยู่ในแอพ ***

### Phase 4 — Production Deploy
- [ ] Dockerize + Railway/Render
- [ ] Custom domain + HTTPS
- [ ] pg_cron, Rate limiting, Logging

### Phase 5 — Growth
- [ ] Push notifications (LINE / FCM)
- [ ] Worker ↔ Employer chat (หลัง hired เท่านั้น)
- [ ] Job recommendation engine
- [ ] ขยายนอก BKK
- [ ] Mobile App (React Native)

---

## 💡 Key Insight

> "ถ้า employer ดู profile worker ได้ เขาโทรตรงเลย ไม่ผ่านแอพ"
>
> แก้ด้วย: ล็อคเบอร์ไว้จนกว่าจะ hired ผ่านแอพ
> ปิดสนิทด้วย: Phase 3 Wallet — เงินอยู่ในแอพ ใครก็ไม่อยากออกนอกระบบ

---

*พักได้เลยพี่ 🙏 วันนี้ทำได้เยอะมากๆ!*
