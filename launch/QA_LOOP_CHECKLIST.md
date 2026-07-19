# QA Loop Checklist — ต้องผ่านก่อนปล่อย user จริง
> ทดสอบบน **มือถือจริง** + **production (we-re-hire.onrender.com)** ด้วย 2 บัญชีทดสอบ (employer 1 + worker 1)
> เจอพังตรงไหน = แก้ก่อน อย่าปล่อยให้ first user เจอ (เสียไปตลอด)

## 0. Pre-flight (reliability)
- [ ] ตั้ง **keep-alive ping** กัน Render หลับแล้ว (ดู REVISED_PLAN — UptimeRobot)
- [ ] เปิด `we-re-hire.onrender.com/health` → ตอบ ok + build ล่าสุด
- [ ] เปิดแอปบนมือถือ → โหลดหน้าได้ ไม่ค้าง

## 1. Auth
- [ ] สมัคร employer ใหม่ (email/password) → สำเร็จ
- [ ] สมัคร worker ใหม่ → สำเร็จ
- [ ] login/logout ทั้งสอง → ใช้ได้
- [ ] (ถ้ามี) Google OAuth → login ได้

## 2. Worker setup
- [ ] กรอกโปรไฟล์ worker (ทักษะ, ตำแหน่ง/พิกัด, ค่าจ้างคาดหวัง) → บันทึกได้
- [ ] อัปโหลด KYC (รูปบัตร/selfie) → upload ขึ้น Supabase Storage ได้
- [ ] dropdown หมวด/อาชีพ → ขึ้นครบ ไม่ว่าง

## 3. Employer post job
- [ ] โพสต์งาน (กรอกครบ + ปักหมุดแผนที่) → **ขึ้นใน"งานของฉัน"** (เช็คบั๊กที่เพิ่งเจอ)
- [ ] dropdown หมวด/อาชีพ ในฟอร์มโพสต์ → ขึ้นครบ
- [ ] งานโผล่ใน worker "หางานใกล้ฉัน" (nearby) → match ถูกโซน

## 4. Matching → Hire → Lifecycle
- [ ] worker apply งาน → employer เห็น candidate
- [ ] employer hire → status = hired + เบอร์โทรเปิด (contact lock ปลดเมื่อ hired)
- [ ] worker checkin (GPS ≤150m) → ผ่าน / นอกระยะ → แจ้ง distance
- [ ] employer start → working
- [ ] worker complete → completed
- [ ] employer verify → verified → trigger review

## 5. Trust & edge
- [ ] รีวิว blind (ซ่อนจนครบทั้งคู่/7วัน) → ทำงาน
- [ ] report ผู้ใช้ → admin เห็น
- [ ] no-show flow (ไม่ checkin) → cron alert/auto no_show (รอเวลา หรือ trigger manual ผ่าน /debug)

## 6. สิ่งที่ "ยังไม่มี" — ต้องสื่อสารชัด
- [ ] **ไม่มีระบบจ่ายเงินในแอป** → จ่ายกันเอง (มีข้อความบอก user ตาม wage policy)
- [ ] หน้า/ลิงก์ policy (ToS/Privacy) เข้าถึงได้

## จุดเสี่ยงที่เคยพัง (เช็คเป็นพิเศษ)
- CORS / Render cold-start (request แรกหลังหลับ fail)
- dropdown ว่าง (init ก่อน form render)
- ลากหมุดแผนที่ / reverse geocode
- Decimal vs float ใน matching/earnings
