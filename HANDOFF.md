# HANDOFF — WeHire

> อ่านไฟล์นี้ก่อนเริ่ม session ใหม่ · อัปเดต 2026-07-08
> รายละเอียดเต็ม → ดู "ไฟล์อ้างอิง" ท้ายเอกสาร

**TL;DR:** Scoreboard เดือนนี้ = **pair (งานจบ + จ่ายเงินจริง)** เป้า 5-10 · must = pair #1 · beachhead = โรงแรม belt กลางเมืองผ่าน connection พ่อ · แรงที่ต้องออก = worker supply

---

## ⏭️ 1. Next actions — session ใหม่เริ่มตรงนี้

1. เช็ค payment-proof bridge task เสร็จยัง → review diff → deploy (**migration → Render → Cloudflare** ห้ามสลับลำดับ)
2. **พี่: เดินสาย employer** — พ่อ → HR โรงแรม anchor → ถามตำแหน่งที่ขาด → recruit worker demand-led โซนนั้น
3. **pair #1-3 = manual log + LINE confirm 2 ฝั่ง (0 build)** — อย่ารอ payment flow เสร็จค่อยขาย
4. LINE OA + เก็บ LINE worker 3 คน (กระสุน seed liquidity)

---

## 🎯 2. ทิศทาง (north star — อ่านก่อนตัดสินใจทุกครั้ง)

- **Scoreboard เดือนนี้ = pair (งานจบ + จ่ายเงินจริง)** ไม่ใช่ code/signup/research · เป้า **5-10 pair**, must = **pair #1**
- **Beachhead = โรงแรม belt กลางเมือง** (Sukhumvit / เพชรบุรีตัดใหม่ / วิทยุ / รัชดา = ก้อนเดียว ทุกโรงห่าง <10 กม.) ผ่าน **connection พ่อ (HR) = unfair advantage**
- **แรงที่ต้องออก = worker supply** (employer = โรงแรม warm จัดการได้) · demand-led ลึกไม่กว้าง
- **ห้าม:** หว่านหลาย segment/โซน · worker marketing กว้าง · pair คู่ให้เอง (seed ได้ ไม่ pair) · ปากต่อปาก = amplifier หลังมี pair สำเร็จ ไม่ใช่ตัวจุดติด
- รายละเอียด → `GTM_traction_plan.md`

---

## 📌 3. สถานะปัจจุบัน

**✅ Live (push + deploy แล้ว):** landing how-to guide · onboarding popup (worker→ตั้งอาชีพ, employer→โพสต์งาน) · เบอร์โทรบังคับ + validate (FE+BE) · mobile UI fixes (การ์ดงาน / วันที่ / dashboard / noti / sidebar / iOS zoom)

**⏳ In-flight — payment-proof flow:**
- task packet: `bridge/inbox/20260708-payment-proof.md` · **รอ watcher หยิบ build** (ถ้ายังไม่รัน → เปิด `bridge/start_watcher.bat`)
- flow: employer แจ้งจ่าย (cash / transfer, โอน = แนบ slip) → worker "ยืนยันได้รับเงิน" → `paid_confirmed` = **pair สำเร็จ**
- เสร็จแล้ว: review diff → run `021_payment_proof.sql` (Supabase) → deploy Render → push Cloudflare **(ห้ามสลับลำดับ)**

**⏸️ Park (ยังไม่ทำ):** Chat #13 (design พร้อมใน DESIGN note) · theme dark/light + zoom (signal ยังไม่ strong) · LINE automation · escrow (Phase 3)

---

## 🔒 4. กฎ / บทเรียนที่ล็อก (ห้ามลืม)

- **ไฟล์ใหญ่ (index.html 4400+, main.py 3500+, CLAUDE.md 900+, PROGRESS.md 800+) = แก้ผ่าน bridge (CC เครื่องจริง) เท่านั้น** · sandbox / wehire-fs / mount อ่าน-เขียน **ขาดได้ (torn read/write)** — 2026-07-08 เกือบเสียโค้ด 267 บรรทัด กู้ทันจาก git
- ไฟล์ .md เล็กก็เคย tear → **write แล้ว verify เสมอ** (line count + tail)
- sandbox เขียน `.git` ไม่ได้ → git commit / amend / push ทำบนเครื่องเอง (พี่)
- **Deploy order:** migration (Supabase SQL Editor) → backend (Render Manual Deploy) → frontend (Cloudflare auto จาก push)
- **Bridge:** watcher = `start_watcher.bat` · task packet **≤6KB** (cmd.exe limit) · GATE2 = CC commit local ไม่ push, พี่ review + push เอง

---

## 🧾 5. CLAUDE.md pending update (ทำผ่าน bridge วันหลัง — อย่าแก้ผ่าน mount)

- migrations: 019 policy consent · 020 job fields (pay_method / contact / dress_code) · 021 payment proof
- phone = required + validate (10 หลักขึ้นต้น 0)
- bridge workflow + torn-read rule

---

## 👤 6. Working style (founder = "พี่")

- burst worker (off สนิท → on เต็ม, บางทีลากยาว) → ใช้ **external checkpoint รายสัปดาห์** วัดที่ pair ไม่ใช่ code
- devil skill = second opinion จริง (ยิงตอนมั่นใจ, เรียกตอนแข็ง ไม่เรียกตอนล้า) · พูดตรง ไม่ประจบ

---

## 📁 7. ไฟล์อ้างอิง (สร้าง / อัปเดต 2026-07-08)

- `SESSION_2026-07-08_summary.md` — สรุปวันนั้น (ship + บทเรียน + reckoning)
- `GTM_traction_plan.md` — แผน traction / beachhead / worker acquisition
- `DESIGN_worker_scan_and_chat.md` — job scan FIFO · location per-job · chat lifecycle · delivery (LINE) · escrow
- `UI_PARKED_notes.md` — theme + zoom (park)
- `PROGRESS.md` — roadmap เต็ม + Session Log
