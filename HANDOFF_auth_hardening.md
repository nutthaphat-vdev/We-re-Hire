# HANDOFF — Auth Hardening + Double-Hire Session

> โยนไฟล์นี้เข้า session ใหม่ได้เลย · วันที่: 2026-07-16 · โปรเจกต์: We're Hired (WeHire)
> บริบท: เริ่มจากงาน mockup (settings/nav) แล้ว pivot มาอุด bug backend หลังมี worker จริงใช้งาน
> feedback จาก worker จริงเป็นตัวจุดเรื่อง phone login

---

## ✅ DONE — deploy prod + เทสผ่านแล้ว (`test_double_hire.py` 6/6 บน prod)

**Double-hire cluster ปิดครบ:**
- `023_job_time_range.sql` → function `job_occupied_range(start_date, duration, work_start, work_end)` → tsrange
  - วันเดียวปกติ / ข้ามเที่ยงคืน (+1 วัน) / หลายวัน (บล็อกทั้งสแปน) · **อยู่บน Supabase แล้ว**
- **`decide`** (commit `2fe2fc0`): advisory lock (worker_id) + guard กัน hire ทับเวลา + auto-withdraw เปลี่ยนจากวันล้วน → วัน+เวลา
- **backup** (commit `2974d06`): `_cascade_backup_offer` + `get_backup_workers` กรอง `is_available=TRUE` + ตัด worker ที่ติดงานทับเวลา · `accept_backup_offer` เพิ่ม lock+guard+withdraw (อุด double-hire ทาง backup)
- ทั้ง 2 commit **push + live แล้ว**

---

## ✅ COMMITTED — auth cluster (commit `8af365f`, main.py) — **รอพี่ push**

> **ไม่มี migration ใหม่** (ใช้คอลัมน์เดิม: users.phone, terms_accepted_at, policy_version) → push ได้เลยปลอดภัย
> backward-compatible: email login เดิมทำงาน · profile-create ไม่มี phone ก็ผ่าน (soft)

- **phone login**: `LoginRequest` รับ `identifier` (เบอร์/อีเมล) + `email` legacy + `remember` · `login` แยก email/phone lookup · `create_token(remember)` → token 30 วัน
- **timing fix**: `_DUMMY_BCRYPT_HASH` รัน bcrypt หลอกเมื่อไม่เจอ user (constant-time กัน enumeration)
- **phone capture (Google)**: `WorkerProfileCreate`/`EmployerProfileCreate` รับ `phone` → set `users.phone` (soft, ไม่ hard-require) · endpoint ใหม่ **`PATCH /auth/phone`** (สำหรับ Google user เก่าที่สร้าง profile ไปแล้ว) · helper `_set_user_phone` (validate `0XXXXXXXXX` + unique)
- **gate (hard enforcement)**: `apply` + `post-job` reject ถ้า `users.phone` ว่าง → "กรุณาเพิ่มเบอร์โทร..."
- **PDPA**: `google_callback` บันทึก `terms_accepted_at=NOW()` + `policy_version='1.0'` (implicit consent ผ่าน notice หน้า login)

**⚠️ พฤติกรรมหลัง deploy ที่ต้องรู้:** Google user เก่าที่ยังไม่มีเบอร์ จะ **apply/post ไม่ได้** จนกว่าจะเพิ่มเบอร์ (ตั้งใจ — contact-lock ต้องใช้) → frontend ต้องมี prompt "เพิ่มเบอร์" (เรียก `PATCH /auth/phone`)

**Frontend follow-ups (ยังไม่แตะ — prod index.html + mockup login.html):**
1. หน้า login: ช่องรับเบอร์ + checkbox "จำฉันไว้" (`remember`)
2. ฟอร์ม profile: ช่อง Tel. (pre-fill จาก `/auth/me` ถ้ามี · Google user ว่าง)
3. prompt "เพิ่มเบอร์" เมื่อโดน gate (apply/post 400) → เรียก `PATCH /auth/phone`
4. notice T&C ใกล้ปุ่ม Google login (รองรับ implicit consent)

---

## 📌 NOTED — ยังไม่ด่วน (จดกันลืม)

- **Token revoke ก่อน escrow** — JWT stateless revoke ไม่ได้ · token 30 วันถูกขโมย = ใช้ได้ 30 วัน (ban ยังตัดได้เพราะ `get_current_user` เช็ก is_active ทุก request) · ก่อนมีเงิน: เพิ่ม `token_version` ใน users bump ตอน logout-all/เปลี่ยนรหัส
- **Rate-limit lockout ต่อบัญชี** — ตอนนี้ login 10/min ต่อ IP เท่านั้น
- **เบอร์ recycle / OTP verify** — ผูกกับ KYC · OTP login เป็น upgrade ตอนมีงบ (Firebase / Supabase phone / SMS gateway ไทย)
- **Selfie check-in** (roadmap) = ตัวจับจริงเรื่องยืมบัญชีสวมรอย (ไม่ใช่แก้ที่ login)

---

## ⏸️ PAUSED — mockup (GeminiDesign/)

- `settings-worker.html` เสร็จ: ใส่ sidebar + bottom-nav 5 แท็บไทย + wire ปุ่มเกียร์ → settings ทั้ง 9 หน้า worker
- เหลือ: sync nav หน้า worker ที่เหลือ · ทำ `profile.html` เป็น hub · comment-stub หน้าอื่น · สร้าง `settings-employer.html`

---

## 🔑 Decisions ที่ล็อกแล้ว (อ้างอิงเวลาทำต่อ)

| เรื่อง | สรุป |
|-------|------|
| นิยาม overlap | time-based (`tsrange &&`) · วันเดียว=เวลาทับ · หลายวัน=บล็อกทั้งสแปน · ข้ามคืน=+1วัน |
| apply | อิสระ ไม่บล็อก — ป้องกันที่ hire อย่างเดียว |
| is_available | toggle มือ (เก็บ) · busy/idle = derive เอา (ไม่เก็บ status ใหม่) |
| remember me | 30 วัน |
| phone login | เบอร์-หรือ-อีเมล + password (OTP เฟสหลัง) |
| เบอร์ Google user | เก็บผ่านฟอร์ม Profile → UPDATE `users.phone` |
| settings IA | desktop = ปุ่มเกียร์ footer · mobile = แท็บบัญชี → hub → settings |

---

## 📁 ไฟล์ที่แตะ session นี้

- `main.py` — double-hire (decide) + backup + phone-login (phone-login ยังไม่ push)
- `023_job_time_range.sql` (ใหม่, run แล้ว) · `test_double_hire.py` (ใหม่)
- `GeminiDesign/`: `settings-worker.html`, `theme-toggle.js`, + 9 worker pages (wire ปุ่มเกียร์)

## 🛠️ Tool notes
- แก้ไฟล์ → `Edit` · git/py_compile บน Windows → `mcp__shell__run_command` (⚠️ mount Linux sync ช้า — เชื่อ Read/shell Windows เป็นหลัก)
- **git push สงวนให้พี่ทำเอง** (hook `block_git_write.py` — agent commit ได้ push ไม่ได้)
- migration ต้อง run บน Supabase **ก่อน** push โค้ดที่เรียก function ใหม่
