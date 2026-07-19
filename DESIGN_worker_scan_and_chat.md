# DESIGN NOTE — Worker Scan (Job Alert) + Chat + Location

> สถานะ: **แนวคิด (concept) ยังไม่ build** · จดกันลืม · build อยู่หลัง "employer ตัวแรกจ้างจ่ายจริง" เสมอ
> เขียน: 2026-07-08 (session ถกกับ Claude)

---

## 0. หลักที่คุมทุกอย่างในโน้ตนี้
- ทุกฟีเจอร์ในนี้ **มีค่าก็ต่อเมื่อมี hire จริงเกิดขึ้น** → build หลัง employer ตัวแรก
- อย่ากระโดดสร้างระบบก่อนมีของจะส่ง/มีงานจะจับ (completion instinct = กับดักตอนไม่มี demand)

---

## 1. Job / Scan — "standing availability" แบบ FIFO one-at-a-time
- Worker กด **"หางาน / เปิดรับ"** → scan **ค้างไว้** (standing query: skills + โซน + rate)
- งานใหม่ที่ตรงโผล่ → ยิง noti หา (ดู §4)
- **พอ `hired` → scan ดับทันที** (ไม่โดนยิงงานอื่นตอนมีงานแล้ว)
- เสร็จ (`verified`) → worker **กด "หาใหม่" เอง** ถึง scan อีกครั้ง — ไม่ auto-ต่อเนื่อง
- เหตุผล: แรงงานรายวันทำทีละกะ · กัน double-book + noti รก
- Data: worker_profiles มี skills[]/location/rate แล้ว → เพิ่มแค่ flag **`is_looking`**
- ⚠️ Park: hired ล่วงหน้า (ทำอีก 3 วัน) → scan ดับ = รับงานแทรกไม่ได้ · MVP ปล่อยก่อน

---

## 2. Location / ที่ตั้งงาน (per-job)
**หลัก: `location` อยู่บน `job_postings` ต่อโพสต์ ไม่ใช่บน employer → 1 โพสต์ = 1 ที่ตั้ง = 1 จุด check-in**
- Fixed (F&B/ร้าน/โรงงาน) = ติ๊ก checkbox **"ใช้ที่ตั้งเดิม"** (**มีแล้ว ไม่ต้อง build**)
- Moving/ad-hoc (วันนี้สาทร พรุ่งนี้เมืองทอง / ก่อสร้าง) = **ไม่ติ๊ก ใส่ที่ใหม่ต่อโพสต์** → **ระบบรองรับแล้ว ไม่ใช่ช่องโหว่**
- GPS check-in 150m + distance matching ผูกจุดเดียว → โมเดล 1-งาน-1-ที่ ทำให้ยังถูก

**Park:**
- multi-site ใน hire เดียว → โพสต์แยกต่อไซต์ (อย่า model หลายที่ใน hire เดียว)
- ไซต์ใหญ่ → radius ปรับได้ต่องาน/category
- saved multiple locations → เฉพาะ employer หลายไซต์ประจำ
- ขยับจุดนิดหน่อย ("มาประตู 7") → คุยผ่าน contact/chat

**devil:** moving-site = ปัญหา segment ก่อสร้าง · beachhead = **F&B ที่ตั้งคงที่ 100%** → ไม่เกี่ยวตลาดแรก · อย่าออกแบบเผื่อก่อสร้างก่อนชนะ F&B · **ตอนนี้ handled พอแล้ว**
**UX polish (ทีหลัง):** อาจอัป checkbox → auto-prefill ถ้า employer จริงมองไม่เห็น — ดู employer ตัวแรกก่อน

---

## 3. Chat Lifecycle
```
locked → active (hired) → read-only (จบงาน) → [dispute: admin เปิดห้องกลับมา active] → resolved → archived
```
- **เปิดตอน `hired` เท่านั้น** (ล้อ Contact Lock — ก่อนจ้างไม่มีแชท)
- จบงาน → read-only ทันที
- retention ผูกกับ dispute window · **ห้าม hard-delete ตราบ dispute เปิด** · resolve แล้วค่อย archive/ลบ (PDPA)
- **Admin re-activate:** dispute → admin เปิดห้อง + ยิง noti ทั้งคู่ "เปิดเพื่อตรวจสอบ" (โปร่งใส) + log ต่อ
- สิทธิ์: เฉพาะ 2 คนในคู่ (+admin ตอน dispute) · เช็ค server-side ทุก read/send · เคารพ user_blocks

---

## 4. Notification Delivery (คอขวดจริงของ Job Alert)
**ปัญหา:** noti ตอนนี้ต้องเปิดแอปเองถึงเห็น → ไปไม่ถึงตอนแอปปิด = ไม่ใช่ alert

**ทิศ: LINE (คนไทยอยู่ใน LINE) — manual-first:**
1. เปิด LINE OA → worker แอด · เก็บ LINE ตอน onboarding
2. งานแรกมา → **LINE หา worker เองด้วยมือ** → วัดว่าเด้งกลับมาสมัครไหม
3. ตอบสนอง + เริ่มบ่อยจนขี้เกียจทำมือ = **automate** (Messaging API ยิงจาก post_job)

- ช่องอื่น: Web Push (PWA ฟรี Android-first) · SMS (ชัวร์ จ่ายรายข้อความ) · FCM (Phase 3 RN)
- ⚠️ LINE Notify กำลังปิด → ใช้ OA + Messaging API (เช็ค terms อีกที)
- **matching = event-driven** (ยิงตอน post_job → reverse-match ST_DWithin+skills) เบากว่า cron · throttle (dedupe/max N วัน/เลี่ยงกลางดึก) ใส่ตอนมี spam

---

## 5. Dispute + Escrow
- ไม่มี escrow → dispute จบยาก (ไม่มีเงินให้ตัดสิน) · มี escrow → admin เคาะ ratio → จ่าย
- **chat-เป็นหลักฐาน + escrow = ระบบ dispute ตัวจริง** = Phase 3 (สูตร pro-rata ใน CLAUDE.md)

---

## Build order (กัน over-engineer)
1. **employer ตัวแรก จ้างจ่ายจริง** ← gate ทุกอย่าง
2. LINE manual notify (แทบ 0 build)
3. `is_looking` flag + scan on/off + event-driven reverse-match
4. LINE automate เมื่อ manual ไม่ไหว
5. Chat (§3)
6. Escrow + dispute (Phase 3)

> Location per-job = **ทำได้แล้ว ไม่ต้อง build** · form = "ครบแต่ไว: ฆ่าแรงต่อช่อง ไม่ตัดช่อง"
