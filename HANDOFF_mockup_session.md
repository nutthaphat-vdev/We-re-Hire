# HANDOFF — GeminiDesign Mockup Cleanup Session

> โยนไฟล์นี้เข้า session ใหม่ได้เลย เพื่อทำงานต่อโดยไม่ต้องเล่าใหม่
> วันที่: 2026-07-16 | โปรเจกต์: We're Hired (WeHire)

---

## 🎯 บริบทงานที่กำลังทำ

กำลัง**จัดหน้า mockup ในโฟลเดอร์ `C:\Users\User\Downloads\Hire\GeminiDesign\`**
⚠️ **เป็น mockup ล้วนๆ — ยังไม่แตะไฟล์หลัก production** (`index.html`, `worker.js`, `main.py`)
การ wire เข้าแอปจริงจะทำทีหลัง ตอนนี้แค่จัด design ให้ลงตัว

---

## ✅ ตัดสินใจแล้ว (Design Decisions)

1. **Mobile nav = Bottom Tab Bar** (ไม่ใช่ burger)
   เหตุผล: กลุ่มผู้ใช้เป็นแรงงานรายวัน คุ้นกับ LINE/Shopee/Grab (bottom tab หมด) + แอปขายเรื่อง "เร็ว" การซ่อนปุ่มใน burger ลด engagement

2. **Worker bottom nav = 5 แท็บไทย:**
   `หน้าหลัก` · `งานของฉัน` · `หางาน`(กลาง) · `แจ้งเตือน` · `บัญชี`
   - แท็บ 5 "บัญชี" → `profile.html` (ไอคอน `ph-user-circle`)
   - Settings เป็น **list ข้างใน** profile/บัญชี ไม่ใช่แท็บแยก

3. **หลักการ mockup: comment ปุ่มที่ยังไม่มีฟังก์ชันจริงออก** (ใช้ `<!-- -->` เก็บไว้ + TODO note ไม่ลบทิ้ง) เหลือเฉพาะของที่มีจริง — กัน "หลอกตา" ตอนยกไป wire

---

## ✅ ทำเสร็จแล้ว session นี้

### `GeminiDesign/dashboard-worker.html`
- เปลี่ยน bottom nav → 5 แท็บไทย + แท็บ 5 = บัญชี (→ profile.html)
- 🐛 Fix: ปิด `.e-stats </div>` ที่ขาด (div balance 5/5 แล้ว)

### `GeminiDesign/dashboard.css`
- 🐛 Fix: dark theme ใส่ค่าจริงให้ `--border-color / --glass-border / --hover-bg`
  (เดิมเขียน `--border-color: var(--border-color)` = invalid → ขอบหายในโหมดมืด)
- ⚠️ กระทบ **ทุกหน้า mockup** ที่ใช้ dashboard.css (worker + employer) — เป็นผลดี ขอบโผล่ครบขึ้น

### `GeminiDesign/settings-worker.html`
- Comment ปุ่ม stub ที่ยังไม่มีฟังก์ชัน
- ปุ่มที่ **โชว์จริง (5)**: โปรไฟล์ส่วนตัว · ประวัติการทำงาน · โหมดสว่าง/มืด · ออกจากระบบ · ลบบัญชี
- **ลบบัญชี**: เคย comment ผิด → เปิดกลับแล้ว (มีจริง: `main.py:4093 @app.delete("/users/me")` + modal ใน index.html)

---

## 🔜 ทำต่อทันที (Next Session — เริ่มตรงนี้)

### 1. ⭐ เปิดปุ่ม "เปลี่ยนภาษา" กลับใน `settings-worker.html`
พี่ยืนยันว่า **i18n TH/EN มีจริงใน production** (ดู `index.html` — มี `data-i18n` + dict TH/EN ครบ เช่นบรรทัด 1872/2090)
→ ปุ่ม "เปลี่ยนภาษา (Language)" ที่ผม comment ไว้ **ต้องเปิดกลับ** (uncomment)
ตำแหน่ง: กลุ่ม "การแสดงผล" คู่กับ theme toggle

### 2. เช็ก stub ที่เหลือว่ามีจริงไหม (ผมอาจ comment ผิดอีก — verify กับ main.py/index.html ก่อน)
ยัง comment อยู่: `ช่องทางการรับเงิน` · `การแจ้งเตือน(settings)` · `เปลี่ยนภาษา`(→ต้องเปิด) · `ติดต่อแอดมิน` · `ข้อตกลงและเงื่อนไข`
> บทเรียน: อย่าเดาว่าไม่มี — grep main.py + index.html ยืนยันก่อน comment ทุกครั้ง

### 3. ปัญหาค้างใน settings-worker.html (ยังไม่แก้)
- **bottom nav ยังเป็นชุดเก่า** (Home/Active Job/Find Job/Noti/**Setting** อังกฤษ) → ต้อง sync เป็น 5 แท็บใหม่ + ให้แท็บ **บัญชี** active
- **desktop ไม่มี nav เลย** (ไม่มี `<aside class="sidebar">` + bottom nav ซ่อนบน desktop) → เพิ่ม sidebar หรือปุ่ม back
- **wiring เพี้ยน**: "ประวัติการทำงาน" → `earnings-worker.html` (หน้ารายได้) แต่ Work History จริงคือ `applications-worker.html`

### 4. ทำหลักการเดียวกัน (comment stub) กับหน้าอื่น
`profile.html`, `dashboard-worker.html`, employer pages ฯลฯ

---

## 📁 ไฟล์สำคัญ

| ไฟล์ | บทบาท |
|------|-------|
| `GeminiDesign/settings-worker.html` | หน้ากำลังแก้ (settings ใต้แท็บบัญชี) |
| `GeminiDesign/dashboard-worker.html` | worker dashboard (bottom nav ใหม่แล้ว) |
| `GeminiDesign/dashboard.css` | shared CSS ทุกหน้า mockup |
| `GeminiDesign/worker.css` | CSS เฉพาะ worker flow (ใหม่) |
| `GeminiDesign/index.html` | landing (mockup) |
| `index.html` (root) | **production frontend จริง** — reference ตอน verify ฟังก์ชัน |
| `main.py` (root) | **production backend จริง** — reference ตอน verify endpoint |

> ⚠️ worker flow mockup มี CSS 2 ชุด: หน้าใหม่ (dashboard-worker, settings-worker) ใช้ `worker.css`, หน้าเก่า (findjobs, applications, earnings, profile, reviews) ยังใช้ `findjobs-real.css` — ถ้าจะ unify ต้อง migrate

---

## 🛠️ Tool / Working Notes
- แก้ไฟล์ Hire → `Edit` / `mcp__wehire-fs__edit_file`
- git/powershell → `mcp__shell__run_command` (⚠️ wrangler deploy ต้องใช้ **PowerShell** ไม่ใช่ cmd)
- Python/grep → `mcp__workspace__bash` (path: `/sessions/.../mnt/Hire/`)
- skill `wehire-product` มี product knowledge เต็ม

## ⚠️ หมายเหตุ glitch
Session ก่อนเจอ bug "court" รัวๆ เวลาสตรีมข้อความ (ระดับระบบ แก้ไม่ได้จากฝั่ง assistant) — เริ่ม session ใหม่ควรหาย งานในโฟลเดอร์เซฟหมดแล้ว ไม่หาย
