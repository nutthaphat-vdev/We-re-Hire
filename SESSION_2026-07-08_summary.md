# WeHire — สรุป Session 2026-07-08

## ✅ Ship ขึ้น live วันนี้ (frontend + backend)
- **Landing "How-to-use"** — 7 ขั้น worker + 4 ขั้น employer, สองภาษา, CTA "เริ่มเลย"
- **Onboarding popup** หลังสมัคร — worker→ชวนตั้งอาชีพ, employer→ชวนโพสต์งาน · เด้งซ้ำจนกว่าจะทำแล้วหายเอง
- **เบอร์โทรบังคับ + validate** 10 หลักขึ้นต้น 0 (frontend กันพิมพ์ผิด + backend กัน bypass)
- **Mobile UI** — การ์ด "จัดการงาน" ไม่หดตัดทีละคำ, ช่องวันที่ชิดซ้าย, dashboard/noti หายใจ, sidebar ปิดสนิท, กัน iOS zoom, noti title ไม่ตัดทีละตัวอักษร
- commits: `2c22cf4` `f92d86f` `cc26e05` `ad0bff8` → push + Cloudflare auto · main.py (phone) = Render Manual Deploy

## ⚠️ เหตุการณ์ + บทเรียน
- เจอ **torn-read**: sandbox/wehire-fs อ่าน index.html ขาด 267 บรรทัด → commit ไฟล์ขาดไป · จับได้จาก "274 deletions" → กู้จาก git object สำเร็จ (diff เหลือ +7/-2 ตามจริง)
- 🔒 **กฎที่ล็อก: ไฟล์ใหญ่ (index.html/main.py) แก้ผ่าน bridge (CC บนเครื่องจริง) เท่านั้น — ห้ามแตะ sandbox/wehire-fs**
- sandbox เขียน `.git` ไม่ได้ → git amend/push ทำบนเครื่องเองเสมอ

## 🎯 Reckoning (devil) — ตัววัดที่แท้จริง
- **Scoreboard เดียว = employer ตัวแรก จ้างจ่ายเงินจริง (organic-match ไม่ pair เอง)**
- สถานะจริง: worker cold **3 คน** / employer **0** / งานจบครบวง **0**
- worker เป็นฝั่งง่าย (คนอยากได้เงินมีล้น) · **employer = ฝั่งยาก + ฝั่งจ่าย** (matching fee 6% มาจากตรงนี้ล้วน)
- งานวันนี้ = **product readiness** (ดี, มาจาก feedback คนนอกจริง) — แต่ **ไม่ใช่ traction** · ฝั่งที่ตัดสินว่าเป็นธุรกิจไหมยังไม่ถูกแตะ
- ⚠️ worker 3 คนที่ไม่มีงานให้กด = **churn ได้ในไม่กี่วัน** (supply เน่าถ้าไม่มี demand)

## 🧠 Design decisions (รายละเอียดใน DESIGN_worker_scan_and_chat.md)
- **Job scan** = standing availability FIFO one-at-a-time (hired→ดับ, เสร็จ→กดใหม่)
- **Location** = per-job (moving-site "วันนี้สาทร พรุ่งนี้เมืองทอง" = โพสต์แยก, ระบบรองรับแล้ว) · reuse = checkbox มีอยู่แล้ว
- **Form** = ครบแต่ไว (ฆ่าแรงต่อช่อง ไม่ตัดช่อง) — ไม่ simplify
- **Chat** = เปิดตอน hired → read-only ตอนจบ → admin re-open ตอน dispute
- **Delivery** = LINE manual-first → automate เมื่อไม่ไหว · matching event-driven (เบากว่า cron)
- **Build gate:** ทุกอย่างหลัง employer ตัวแรก

## ▶️ Next (เรียงลำดับ)
1. **ไปหา employer ตัวแรก** — F&B beachhead โซนเดียว งานประเภทเดียว (ข้อสอบที่ devil เปิดค้าง)
2. **LINE OA + เก็บ LINE worker 3 คน** (แทบ 0 build) = กระสุนปลุก supply ตอน employer โพสต์งานแรก → เขาเห็น app เวิร์ค → self-serve
3. รอ **hire จริง** เกิด → ค่อยเปิด design note ทำตาม build order

## 🚫 อย่าเพิ่งทำ (park)
- LINE automation, Chat, Escrow, job-alert automate, auto-prefill address, radius ปรับได้, multi-site — **ทั้งหมด gate หลัง employer ตัวแรก**
- Chat feature (#13) ยัง pending ตั้งใจ
