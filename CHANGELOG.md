# We're Hired — Development Changelog
> จากไอเดียสู่ Production ใน 3 วัน

---

## Day 1 — 22 พฤษภาคม 2568 · วันปล่อย MVP

### 09:36 · 🚀 Initial Commit — MVP ทั้งหมดในคราวเดียว
ครั้งแรกที่ push ขึ้น GitHub ไม่ใช่แค่ skeleton — เป็น product ที่ทำงานได้จริง

**สิ่งที่อยู่ใน commit แรก:**
- FastAPI backend + asyncpg + Supabase PostgreSQL + PostGIS
- JWT auth (register / login / middleware)
- Worker & Employer profile
- Job posting + nearby search (PostGIS ST_DWithin)
- Matching engine (skills 60% / distance 25% / rate 15%)
- Review system (blind review, tags, 5 ดาว)
- Notification system
- Single-file frontend (Vanilla JS, ~2,000+ lines)
- Deploy ready: Railway (backend) + Cloudflare Workers (frontend)

### 09:55–11:01 · ⚙️ Deploy Setup
- แยก `.env` ออกจาก git
- แก้ Railway URL ที่เปลี่ยนหลัง deploy
- ปัญหา: Cloudflare Workers พยายาม install `requirements.txt` → แก้โดย rename ไฟล์ชั่วคราว
- เพิ่ม `.cfignore` กัน Cloudflare อ่านไฟล์ Python

### 13:48–14:01 · 🔐 Google OAuth Round 1
- แก้ redirect URL หลัง Supabase callback
- ลอง verify token ด้วย RS256 → ล้มเหลว (Supabase ไม่ใช้ RS256)

### 14:43 · 🔥 Critical Bug #1 — PgBouncer
```
DuplicatePreparedStatementError — ทั้งระบบพัง
```
Root cause: asyncpg + Supabase PgBouncer transaction mode ไม่ compatible กับ prepared statements  
Fix: `statement_cache_size=0` — บรรทัดเดียวกู้ชีวิตทั้ง production

### 14:55 · 🐛 Bug #2 — Decimal vs Float
```python
TypeError: unsupported operand type(s) for /: 'decimal.Decimal' and 'float'
```
เกิดใน matching engine ตอนคำนวณ rate score  
Fix: `float(worker_rate) / float(job_rate)` — ต้อง explicit cast เสมอกับ asyncpg

### 21:30–22:43 · 🔐 Google OAuth Round 2–4
ใช้เวลานานสุดในวันแรก — debug OAuth ไปหลายรอบ:

| รอบ | ลอง | ผล |
|-----|-----|-----|
| 1 | RS256 | ❌ Supabase ไม่ใช้ |
| 2 | JWKS verification | ❌ signature ไม่ตรง |
| 3 | HS256 (legacy secret) | ❌ algorithm mismatch |
| 4 | google-auth library | ❌ wrong token type |

ยังไม่ได้ solution ในวันนี้ — ต้อง debug ต่อคืน

### 22:35 · 🔔 Notifications UI
- Filter tabs: ทั้งหมด / ยังไม่อ่าน
- Smart date labels (วันนี้ / เมื่อวาน / full date)
- Type badges สีต่างกัน (hired, rejected, ผู้สมัครใหม่...)
- Unread count badge ใน sidebar

### 21:58 · 📄 Add CLAUDE.md
เขียน context file ให้ Claude Code เพื่อสร้าง shared knowledge base ข้ามเซสชัน

---

## Day 2 — 23 พฤษภาคม 2568 · วัน Feature Sprint

### 00:54–01:26 · 🔐 Google OAuth — Final Fix
หลังจาก debug ข้ามคืน ค้นพบว่า Supabase ใช้ **ES256 + JWKS** เท่านั้น

```python
# ✅ วิธีที่ถูกต้อง — ต้อง match kid จาก JWKS
header = jwt.get_unverified_header(access_token)
for key in jwks["keys"]:
    if key["kid"] == header["kid"]:
        public_key = ECAlgorithm.from_jwk(key)
payload = jwt.decode(access_token, public_key, algorithms=["ES256"])
```

บทเรียน: Supabase เปลี่ยนจาก HS256 → ES256 โดยไม่ประกาศชัด — ต้องอ่าน JWKS เสมอ

### 01:36 · 🗺️ Zones API
- Zones dropdown โหลดจาก `GET /zones` แทน hardcode
- รองรับ 50+ เขตกรุงเทพ + ปริมณฑล

### 03:44 · 🌐 Landing Page + Admin
- Landing page อธิบาย product สำหรับ demo
- Admin endpoints: verify employer, KYC management
- Review summary แสดงบน employer profile

### 10:13 · ⏰ Work Hours
- เพิ่ม `work_start`, `work_end` (TIME) + `ot_rate` ต่อ job posting
- Max 8 ชม./วัน enforce ทั้ง frontend + backend
- Bug พบทีหลัง: asyncpg ต้องการ `datetime.time` ไม่ใช่ string — ต้อง `fromisoformat()` ก่อน INSERT

### 10:36–11:17 · 📋 Job Lifecycle (Feature ใหญ่สุดของวัน)
สร้าง full workflow จาก hired จนถึงจ่ายเงิน:

```
hired → checked_in → working → completed → verified
                                         ↘ disputed (< 90%)
```

Endpoints เพิ่มใน sprint นี้:
- `POST /applications/{id}/checkin` — GPS ≤ 150m (PostGIS)
- `POST /applications/{id}/start` — ±30 นาที จาก work_start
- `POST /applications/{id}/complete` — Worker กดเสร็จ
- `POST /applications/{id}/verify` — Employer ยืนยัน
- Auto-verify cron ทุก 30 นาที (APScheduler)
- Migration: 007_work_hours, 008_job_lifecycle, 009_disputed_status

### 13:15 · 🐛 Bug #3 — asyncpg datetime.time
```python
# ❌ asyncpg ไม่รับ string
"work_start": "09:00"

# ✅ ต้อง convert ก่อน
from datetime import time as time_type
work_start = time_type.fromisoformat(data.work_start)
```

### 15:16 · 🎨 Rebrand WeHire → We're Hired
เปลี่ยนชื่อทั้ง codebase — ทั้ง frontend, backend, docs

### 18:27 · 🔐 Google OAuth — Production Fix
- เพิ่ม PKCE support (code_verifier / code_challenge)
- Fix URL encoding ใน redirect
- Fix landing page flash ก่อน token check

### 20:48 · 🐛 Bug #4 — Notifications Empty (Browser Cache)
```
อาการ: badge แสดง "2" แต่เปิดหน้า notifications ว่างเปล่า
```
Root cause: Browser cache `GET /notifications` → `[]` จากครั้งแรกที่ user ไม่มี notifications  
Fix: เพิ่ม `cache: 'no-store'` ใน fetch() ทุก request

### 22:31 · 🐛 Bug #5 — Nearby Jobs ไม่ filter ระยะ
```
อาการ: radius=1km แต่เห็นงานระยะ 31km
```
สาเหตุที่แท้จริง: ST_DWithin ทำงานปกติ — bug อยู่ที่ edge cases
- asyncpg type inference ผิดกับ empty array `[]`
- `jp.required_skills && $4::text[]` ต้องใช้ `cardinality($4::text[]) = 0` ด้วย

Fix:
```sql
AND (
  cardinality($4::text[]) = 0
  OR jp.required_skills = '{}'
  OR jp.required_skills && $4::text[]
)
```

### 23:40–23:48 · 🚀 CI/CD Setup
- `wrangler.toml` — config Cloudflare Workers
- `worker.js` — serve index.html
- `.github/workflows/deploy-frontend.yml` — auto-deploy เมื่อ push

---

## Day 3 — 24 พฤษภาคม 2568 · วัน Polish & Docs

### 00:01 · 🔔 Notifications Deep-Link
- กดการ์ดแล้ว navigate ไปหน้าที่เกี่ยวข้องทันที
- Auto-mark as read เมื่อนำทาง
- "ดูรายละเอียด →" hint บนการ์ดที่ actionable
- Dashboard stats: 7 เขต → 50+, 15km → 30km

### 00:01 · 📄 Docs Consolidation
- รวม PROGRESS.md + PROGRESS2.md เป็นไฟล์เดียว
- CHANGELOG.md ไฟล์นี้

### · 🚀 CI/CD Live
- อัปเดต GitHub PAT ให้มี `workflow` scope
- เพิ่ม GitHub Secrets: `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID`
- Push → GitHub Actions รัน → Cloudflare deploy อัตโนมัติ ✅
- ตั้งแต่นี้ไปแก้ `index.html` แล้ว push ขึ้น production ใน ~30 วินาที

### · 📋 Roadmap KYC + NDID
- เพิ่ม Phase 2 — KYC Level 1 (Free): รูปโปรไฟล์ + บัตรประชาชน + Selfie + admin verify
- เพิ่ม Phase 3.5 — NDID Integration: ยืนยันผ่านแอพธนาคาร + ประวัติอาชญากรรมจากราชการ
- Worker Tier System: Unverified / KYC / NDID

### · 🐛 Bug #6 — Notifications HTML Structure (3 รอบ)
```
อาการ: content จมลงไปข้างล่างมาก เกือบไม่เห็น
```

รอบที่ 1 — วินิจฉัยผิด: เห็น `<div style="padding:32px">` ซ้อนใน `.page{padding:32px}` คิดว่า double padding → ลบ wrapper ออก  
รอบที่ 2 — ยังไม่หาย: พบว่า `#page-notifications` อยู่นอก `.main` container ทั้งหมด → ย้ายเข้ามาแต่วาง closing div ผิดที่  
รอบที่ 3 — root cause จริง: การวางผิดทำให้ `#page-notifications` ถูก nest ใน `#page-myjobs` และ `#page-myreviews` หลุดออกนอก `.app` ด้วย → แก้ structure ทั้งหมดในครั้งเดียว

บทเรียน: HTML structure bug ที่ซ้อนกันหลายชั้น ต้อง trace closing div ทุกตัวก่อนแก้

---

## Day 4 — 25 พฤษภาคม 2568 · วัน Trust & Safety Sprint

### · 🪪 KYC Phase 2A — รองรับแรงงานทุกสัญชาติ
Migration `010_kyc.sql` เพิ่ม 12 columns ใน `worker_profiles`:

| กลุ่ม | Columns |
|-------|---------|
| ทุกคน | `nationality_type`, `profile_photo_url`, `selfie_url` |
| คนไทย | `id_card_front_url`, `id_card_back_url` |
| ต่างด้าว | `passport_url`, `work_permit_url`, `work_permit_expiry` |
| Admin tracking | `kyc_submitted_at`, `kyc_reviewed_at`, `kyc_reviewed_by`, `kyc_note` |

- `background_check_status` ที่มีอยู่แล้ว (none/pending/approved/rejected) ใช้ต่อได้เลย
- Index `idx_worker_kyc_status` บน `background_check_status = 'pending'` เร่ง Admin dashboard

### · 🗂️ Job Categories Expanded (011)
เพิ่ม 4 categories ใหม่ + 24 job titles:

| Category | Icon | หมายเหตุ |
|----------|------|----------|
| โรงงานและการผลิต | 🏭 | 6 titles |
| งาน Event และ Seasonal | 🎪 | 5 titles |
| ล่ามภาษา | 🗣️ | 4 titles (TH↔MY/LA/KH/EN) |
| งานดูแลบุคคล | ⚠️ | 3 titles — `is_special=true` (NDID required Phase 3.5) |

รวม DB: 8 categories · 32+ job titles

### · 👻 Active Anti-Ghosting System (Feature ใหญ่สุดของวัน)
ปัญหา: worker ได้รับงาน hired แล้วหายตัวไป ไม่มาทำงาน ทำให้ employer เสียเวลา

**Schema (012_anti_ghosting.sql):**
- `noshow_marked_at`, `noshow_alerted_at` — track no-show state
- `backup_priority`, `backup_offered_at`, `backup_accepted_at` — backup workflow
- Status `no_show` เพิ่มใน CHECK constraint
- 2 indexes สำหรับ cron performance

**4 Endpoints ใหม่:**

| Endpoint | ใคร | Logic |
|----------|-----|-------|
| `GET /jobs/{id}/backup-workers` | Employer | top 10 applied/shortlisted ranked by match_score |
| `POST /applications/{id}/send-backup` | Employer | ส่ง offer ด่วน + แจ้ง worker ทันที |
| `POST /applications/{id}/accept-backup` | Worker | รับงาน → `hired` + slot filled + Maps link |
| `PATCH /applications/{id}/mark-noshow` | Employer | `no_show` + slot freed + แจ้ง worker |

**2 Cron Jobs:**

```
Cron ทุก 5 นาที (check_noshow_workers):
  work_start + 30 นาที ผ่านไป → alert employer (ครั้งเดียว)
  work_start + 60 นาที ผ่านไป → auto no_show + free slot + notify ทั้งคู่

Cron 18:00 ทุกวัน / 11:00 UTC (send_d1_reminders):
  ค้นหา status='hired' + start_date = พรุ่งนี้
  → push notification ไปทุก hired worker ที่มีงานพรุ่งนี้
```

### · 🛂 Work Permit Enforcement — แรงงานต่างด้าวต้องมีเอกสารก่อนสมัคร

**Backend (main.py):**
```python
# POST /jobs/{id}/apply — ตรวจก่อน insert application
if worker["nationality_type"] == "foreign":
    if not worker["work_permit_url"]:
        raise HTTPException(403, "กรุณา upload Work Permit ก่อนสมัครงาน")
    if worker["work_permit_expiry"] < date.today():
        raise HTTPException(403, "Work Permit หมดอายุแล้ว กรุณาอัปเดตเอกสาร")
```

- `GET /workers/profile/me` คืน `nationality_type`, `work_permit_url`, `work_permit_expiry` ด้วย
- `PATCH /workers/profile` รับ `nationality_type` (thai / foreign)

**Frontend (index.html):**
- Work Permit card ใน worker profile — เห็นเฉพาะ foreign workers
  - Badge: ✅ Verified / ⏳ รอ Admin / ⚠️ ยังไม่ได้ upload
  - Link ดูเอกสาร (เปิด Supabase Storage URL)
  - คำเตือนสีส้ม ถ้าเหลือ < 30 วัน
  - Error สีแดง ถ้าหมดอายุแล้ว
- Nationality selector (ไทย / ต่างด้าว) ใน edit profile form
- Terms disclaimer ใน register page

### · 🌐 Multi-language UI — รองรับแรงงาน 3 ภาษา

Worker-facing UI รองรับ **🇹🇭 ไทย / 🇲🇲 မြန်မာ / 🇬🇧 English** — switch ได้ทันทีโดยไม่ต้อง reload

**สถาปัตยกรรม:**
```javascript
const LANG = { th: {...}, my: {...}, en: {...} }; // 30+ keys ต่อภาษา
let _lang = localStorage.getItem('wh_lang') || 'th';
function t(key) { return (LANG[_lang] || LANG.th)[key] || key; }
function setLang(lang) { ... } // update data-i18n elements + active class
```

**ครอบคลุมทุก touch point:**
- Login / Register page — tabs, labels, buttons, role selector
- หน้าหางานใกล้บ้าน — ปุ่มค้นหา, ปุ่มสมัคร
- ประวัติใบสมัคร — status badges ทุกสถานะ, ปุ่ม checkin/complete/nav/contact, wait messages
- Lang toggle บน auth page (TH/MM/EN flag buttons)
- Lang toggle compact ใน sidebar (เห็นตอน login แล้ว)
- Persistence ใน `localStorage` key `wh_lang`

---

## Day 5 — 26 พฤษภาคม 2568 · วัน Infra & Docs

### · 🔗 Rename Cloudflare Worker → wearehiredmvp
เปลี่ยนชื่อ Worker จาก `divine-bar-29c7` → `wearehiredmvp`

- `wrangler.toml`: `name = "wearehiredmvp"`
- Frontend URL ใหม่: `https://wearehiredmvp.vi-nutthaphat.workers.dev`
- CLAUDE.md: อัปเดต URL table ทุกจุด

### · 🌐 CORS & OAuth Redirect Fix
หลังเปลี่ยน URL ต้องแก้หลายจุดพร้อมกัน:

- `main.py`: ลบ hardcode `127.0.0.1:5500` fallback ออกจาก OAuth callback → ใช้ `settings.frontend_url` เปล่าๆ
- `main.py`: hardcode URL ใหม่ใน CORS allowlist (bypass env var timing issue)
- CORS verify ด้วย `curl -I -X OPTIONS` — ยืนยัน `Access-Control-Allow-Origin` header

### · 📋 Production URL Change Checklist (CLAUDE.md)
เพิ่ม section ใหม่ใน CLAUDE.md — 7 ขั้นตอน ทุกครั้งที่เปลี่ยน URL:

| ขั้นตอน | จุดที่แก้ |
|---------|----------|
| 1 | Cloudflare Dashboard — rename worker |
| 2 | wrangler.toml — name = ใหม่ |
| 3 | Google Cloud Console — redirect URIs (รอ 5-30 นาที) |
| **4** | **Supabase — Site URL + Redirect URLs ← มักลืม!** |
| 5 | Railway env vars — FRONTEND_URL + CORS_ORIGINS |
| 6 | main.py — ไม่มี URL hardcode |
| 7 | Verify ด้วย curl |

**Bug ที่เจอ:** Supabase Site URL คือตัวการทำให้ redirect URL กลับไปเป็น URL เก่า  
**Lesson:** ทุกครั้งที่เปลี่ยน URL ต้องแก้ครบ checklist ทั้ง 7 ขั้น — ลืมขั้นไหนขั้นหนึ่ง OAuth พัง

### · 🌐 Multi-language UI ทุกหน้า (TH/EN)
ขยาย i18n จาก auth page เดียว → ครอบคลุมทุกหน้าใน dashboard

**หน้าที่อัปเดต:**
- Sidebar — nav items, section labels (GENERAL/WORKER/EMPLOYER), ปุ่ม Logout
- Dashboard — greeting, quick-action cards, stat labels
- Notifications — type badges, date labels, empty states, mark-read button
- My Applications (worker) — status badges, action buttons (checkin/complete/nav/contact)
- My Jobs (employer) — empty state, slot info, view/close/reopen buttons
- Candidates — back button, hire/reject/verify/dispute buttons, status badges
- Worker Profile — field labels, edit/save/cancel buttons, nationality selector

**ถอด Myanmar ออก:** ภาษาพม่า (MM) ไม่เหมาะกับ pitch deck BKK MVP  
เหลือ 2 ภาษา: 🇹🇭 ไทย / 🇬🇧 English

### · 📍 Language Toggle — ย้าย position + เปลี่ยน style
- ย้ายออกจากใน `.token-box` → อยู่ระหว่าง nav items กับ token box
- เปลี่ยนจาก flag emoji (🇬🇧) → text-only `TH` / `EN`
- Active = `var(--accent)` สีเขียว, Inactive = `var(--muted)` สีเทา
- `setLang()` อัปเดต inline `color` ทันทีทุกครั้ง toggle

### · 🔐 Security Audit + Fixes
Security audit ครอบคลุมทุกจุด — `main.py` (2,580 บรรทัด) + `index.html` (2,301 บรรทัด)  
ผล: **4 CRITICAL / 7 WARNING / 6 INFO** — ข่าวดี: ไม่มี SQL Injection, JWT verify ถูกต้อง, RBAC ครบ

**Fixes ที่ implement ในวันนี้:**

| # | ระดับ | งาน | ไฟล์ |
|---|-------|-----|------|
| C1 | 🔴 | XSS: เพิ่ม `esc()` + ใช้ทุก user-input ใน innerHTML | index.html |
| C3 | 🔴 | ลบ auto-ban 3 reports → `logger.warning` สำหรับ admin review | main.py |
| C4 | 🔴 | Contact endpoint: `hired` เดียว → `hired/checked_in/working/completed/verified` | main.py |
| W2 | 🟡 | ปิด `/docs` + `/redoc` เมื่อ `RAILWAY_ENVIRONMENT` set | main.py |
| W3 | 🟡 | ลบ `u.email` ออกจาก `GET /users/blocked` response | main.py |
| W4 | 🟡 | Review: `status = 'hired'` → `IN ('hired','verified','disputed')` | main.py |
| W6 | 🟡 | ลบ URL เก่า `divine-bar-29c7` ออกจาก CORS hardcode | main.py |

**XSS ที่แก้ครอบคลุม:** job title, location_name, skills array, employer_note, full_name, background_check_status, notification title/body, contact name/phone/email, employer company_name — ทุกจุดที่มาจาก API

**คงเหลือ (ก่อน scale):**  
W1 rate limiting · C2 JWT expire 120 นาที · W7 `is_active` ใน `get_current_user` · I1 security headers · W5 column allowlist

### · 🐛 Bug #9 — Job posting โผล่หลังงานเสร็จ
```
อาการ: งานที่ slots เต็มแล้ว (ทุก worker verified) ยังแสดงใน Nearby + My Jobs
```

Root cause: ไม่มีโค้ดที่ mark `job_postings.status = 'filled'` หลัง verify — status ยังเป็น `open` ตลอด

**Fix:**
```python
# หลัง UPDATE job_applications SET status='verified'
UPDATE job_postings SET status='filled'
WHERE  id=$1 AND status='open'
  AND  slots_filled >= slots_available
```

แก้ 3 จุดใน `main.py`:
- `POST /applications/{id}/verify` — employer กด verify เอง
- Auto-verify cron — cron ยืนยันให้อัตโนมัติหลัง 2 ชม.
- `_get_app_for_employer` — เพิ่ม `jp.id AS job_id` เพื่อให้ทั้งสอง endpoint เข้าถึง job_id ได้
- `GET /jobs/mine` — เพิ่ม `AND status = 'open'` filter (Nearby มีอยู่แล้ว)

---

## Stats

| | จำนวน |
|--|--|
| วันที่ใช้สร้าง | **5 วัน** |
| Commits | **75+** |
| Endpoints | **47+** |
| Database migrations | **12 ไฟล์** |
| Bugs ที่เจอและแก้ | **9 critical** |
| Security findings fixed | **7 (4 CRITICAL + 3 WARNING)** |
| Lines of code (approx) | **~7,000+** |
| ภาษา UI รองรับ | **2 (TH/EN)** |

---

## Bugs Hall of Fame

| # | Bug | เวลาที่เสีย | วิธีแก้ |
|---|-----|------------|---------|
| 1 | PgBouncer `DuplicatePreparedStatementError` | ~1 ชม. | `statement_cache_size=0` |
| 2 | `decimal.Decimal / float` TypeError | ~30 นาที | `float()` explicit cast |
| 3 | Google OAuth ES256 vs HS256 vs RS256 | **~8 ชม.** | JWKS + `kid` matching |
| 4 | Browser cache notifications `[]` | ~2 ชม. | `cache: 'no-store'` |
| 5 | asyncpg `datetime.time` ไม่รับ string | ~30 นาที | `fromisoformat()` before INSERT |
| 6 | Notifications HTML nest + อยู่นอก `.main` | ~1 ชม. (3 รอบ) | trace closing div ทุกตัว |
| 9 | Job posting โผล่หลังงานเสร็จ (slots เต็มแต่ status ยัง `open`) | — | mark `status='filled'` ใน verify + cron |

> Bug #3 (Google OAuth) กินเวลาข้ามคืน — debug ตั้งแต่บ่ายวันที่ 22 จนถึงตี 1 วันที่ 23
