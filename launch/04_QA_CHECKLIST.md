# 04 — QA Checklist (เทสก่อนปล่อย user จริง)

> **ไฟล์นี้ใช้ยังไง:** ไล่เทสตามนี้บน **มือถือจริง 2 เครื่อง** (เครื่อง A = employer, เครื่อง B = worker) ก่อนเริ่ม outreach **ห้ามข้าม** — user จริงเจอบั๊กครั้งแรก = ขอ first impression คืนไม่ได้ พี่มีโอกาสครั้งเดียว
> เทสครบ = ติ๊กครบทุกช่อง แล้วค่อยไปไฟล์ 01/02

---

## 🔥 เทสก่อนเพื่อน: ปลุก Backend (Render cold-start)

> ⚠️ Render free/hobby tier **หลับเมื่อไม่มี traffic** คำขอแรกหลังหลับใช้เวลา 30-60 วิ ถ้า user คนแรกเจอหน้าค้าง = คิดว่าแอพพัง

- [ ] เปิด `https://we-re-hire.onrender.com/` ในเบราว์เซอร์ รอจนตอบ (ครั้งแรกอาจช้า)
- [ ] ลองซ้ำอีกครั้ง ต้องเร็ว (<2 วิ) = ตื่นแล้ว
- [ ] **ก่อนนัด onboard employer/worker แต่ละครั้ง → ยิง backend ให้ตื่นก่อน 1 ครั้ง** (เปิดหน้าเว็บทิ้งไว้)
- [ ] (แนะนำ) ตั้ง uptime ping ฟรี (เช่น cron-job.org / UptimeRobot) ยิง `/` ทุก 10-14 นาที กัน cold-start ระหว่างวัน

---

## 🌐 เทส CORS + เชื่อมต่อ Frontend↔Backend
> เคยพังมาแล้ว: URL frontend ไม่อยู่ใน CORS_ORIGINS → ทุก request fail เงียบ

- [ ] เปิด frontend `https://wearehiredmvp.vi-nutthaphat.workers.dev` บนมือถือ
- [ ] เปิด DevTools/Console (หรือเทสบน desktop ก่อน) → **ไม่มี CORS error สีแดง**
- [ ] ลอง register/login จริง → สำเร็จ (ถ้า fail = เช็ค CORS_ORIGINS ใน Render env + `settings.frontend_url`)
- [ ] ทดสอบ Google OAuth login → redirect กลับมาแล้ว login ติด (เช็ค Supabase Redirect URL + Google redirect URI ตรงกับ URL ปัจจุบัน)

---

## 📝 เทส Loop เต็ม (เครื่อง A = Employer, เครื่อง B = Worker)

### Step 1 — Employer โพสต์งาน [เครื่อง A]
- [ ] สมัคร/ล็อกอินเป็น employer
- [ ] **Dropdown หมวดงาน/ตำแหน่งโหลดครบ** (เคยพัง: dropdown ว่างเพราะ init ก่อน form render — ถ้าว่าง ลองรีเฟรช/เข้าใหม่ แล้วจดไว้ว่ายังมีบั๊ก)
- [ ] กรอกงานครบ: ตำแหน่ง, วันที่, เวลา work_start/work_end, ค่าจ้าง, จำนวนคน
- [ ] **ปักหมุดแผนที่ + ลากหมุดได้** (เคยพัง: marker ลากไม่ได้ — ตรวจว่า lat/lng อัปเดตตามหมุด)
- [ ] โพสต์สำเร็จ → งานขึ้นในระบบ

### Step 2 — Worker เจองาน + สมัคร [เครื่อง B]
- [ ] ล็อกอินเป็น worker (โปรไฟล์มี location อยู่ในโซนเดียวกับงาน)
- [ ] **งานที่เพิ่งโพสต์โผล่ในรายการ nearby** (ถ้าไม่โผล่ = เช็ค matching/PostGIS radius + worker location ตั้งไว้ไหม)
- [ ] เปิดดูรายละเอียดงาน → match_score / ระยะทาง แสดงถูก
- [ ] กดสมัคร → สำเร็จ
- [ ] **เบอร์โทร employer ต้องยังไม่โชว์** (contact lock — เปิดเฉพาะหลัง hired)

### Step 3 — Employer จ้าง [เครื่อง A]
- [ ] เห็น worker ที่สมัคร + โปรไฟล์ + รีวิว (ถ้ามี)
- [ ] กด hire → worker ได้ notification
- [ ] หลัง hired → **เบอร์โทรเปิดเผยทั้ง 2 ฝั่ง**

### Step 4 — Worker เช็คอิน GPS [เครื่อง B] ⚠️ จุดเสี่ยงสูง
- [ ] วันงาน worker กดเช็คอิน → **เบราว์เซอร์ขอ permission location → ต้องอนุญาต**
- [ ] ยืนในรัศมี 150m จากจุดงาน → เช็คอินผ่าน
- [ ] ลองเช็คอินไกลเกิน 150m → ขึ้น error บอกระยะจริง (กันคนเช็คอินจากบ้าน)
- [ ] **เทสบนมือถือจริงนอกอาคาร** — GPS ในตึก/ wifi เพี้ยนได้ ต้องรู้ว่า user จะเจออะไร

### Step 5 — งานเดินจนจบ
- [ ] Employer กด start (อยู่ในช่วง ±30 นาทีจาก work_start) [A]
- [ ] Worker กด complete เมื่อจบงาน [B]
- [ ] Employer กด verify [A] → สถานะ verified
- [ ] (ถ้าไม่กด verify) เทส auto-verify cron ทำงาน — หรือ trigger เองผ่าน debug endpoint
- [ ] หลัง verified → **ระบบให้รีวิวทั้ง 2 ฝั่ง** (blind review — รีวิวอีกฝั่งซ่อนจนกว่าจะส่งครบ/ครบ 7 วัน)

### Step 6 — Earnings / เงิน
- [ ] Worker เปิดหน้า earnings → เห็นยอด (จำ: ตอนนี้เป็น "ค่าจ้างโดยประมาณ" ยังไม่ใช่ escrow จริง — มี label เตือนไหม)
- [ ] ตัวเลข fee 6% คำนวณถูก (หักฝั่ง worker ตาม default)

---

## 👻 เทส Edge Cases (อย่างน้อยลองสัก 2-3 อัน)
- [ ] **No-show:** worker hired แต่ไม่เช็คอิน → +30 นาที employer ได้ alert, +60 นาที auto no_show + slot คืน (trigger cron ผ่าน debug endpoint ได้)
- [ ] **Backup worker:** หลัง no-show employer เห็น backup list → ส่ง offer → worker อีกคนรับ → hired
- [ ] **งานเต็ม slot:** จ้างครบจำนวนแล้ว worker ใหม่สมัครไม่ได้/เห็นว่าเต็ม
- [ ] **2 worker แย่ง slot สุดท้าย** พร้อมกัน → ไม่ over-hire เกิน slot

---

## 📱 เทสประสบการณ์มือถือจริง (เพราะ user 99% ใช้มือถือ)
- [ ] หน้าจอไม่ล้น/ปุ่มกดถึงบนจอเล็ก (เทสจอ ~6 นิ้ว)
- [ ] ฟอร์มพิมพ์ภาษาไทยได้ไม่เพี้ยน
- [ ] แผนที่ Google Maps โหลดบนมือถือ (เช็ค API key ไม่ติด domain restriction จนพัง)
- [ ] โหลดครั้งแรกไม่นานเกินรับได้ (เผื่อ cold-start แล้ว)
- [ ] ลองบน **เน็ตมือถือจริง (4G/5G ไม่ใช่ wifi)** — user จริงใช้แบบนี้

---

## 🧹 ก่อนเปิดจริง — ล้างของทดสอบ
- [ ] ลบ account/งาน/รีวิวที่เทสไว้ออก (อย่าให้ user เจอ data ขยะ)
- [ ] เหลือไว้เฉพาะ data ที่อยากโชว์ (ถ้ามี)
- [ ] เตรียม account admin + จำ `X-Admin-Secret` ไว้เผื่อต้องแก้สด

---

## 🚦 สรุปจุดเสี่ยงที่เคยพัง (ดูเร็วๆ)
| จุดเสี่ยง | อาการ | เช็คอะไร |
|----------|-------|---------|
| Render cold-start | คำขอแรกค้าง 30-60 วิ | ปลุก backend ก่อน onboard / ตั้ง uptime ping |
| CORS | request fail เงียบ login ไม่ได้ | URL อยู่ใน CORS_ORIGINS + frontend_url ไหม |
| Dropdown ว่าง | เลือกหมวด/ตำแหน่งไม่ได้ | init dropdown หลัง form render |
| หมุดแผนที่ลากไม่ได้ | ตั้ง location ไม่ได้ | marker draggable + dragend listener |
| GPS เช็คอิน | เช็คอินไม่ผ่าน/เพี้ยน | permission + เทสนอกอาคาร + รัศมี 150m |
| OAuth | login Google แล้วเด้งกลับไม่ติด | Supabase/Google redirect URL ตรง URL ปัจจุบัน |
