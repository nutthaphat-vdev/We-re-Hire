# COUPLING_MAP — สิ่งที่อ่านจากโค้ดไม่เห็น

> ✍️ **ไฟล์นี้เขียนด้วยมือ · `gen_map.py` ไม่แตะ** — ถ้าเจอกับดักใหม่ให้เพิ่มลงที่นี่
> คู่กับ `INDEX_MAP.md` (auto-generated) — อันนั้นบอก "อะไรอยู่ตรงไหน" · อันนี้บอก **"แก้ตรงนี้แล้วอะไรพัง"**
>
> อัปเดตล่าสุด: 2026-07-19 (รอบ 5 — employer profile) · อ้างอิง `index.html` 6,415 บรรทัด sha `f7c9dbabe590`
> ⚠️ เลขบรรทัดในไฟล์นี้จะเลื่อนเมื่อแก้โค้ด — ถ้าไม่ตรง ให้ค้นด้วย**ชื่อ function** แทน

---

## 🔴 1. มี router **สองตัว** ที่ต้อง sync กัน

| ตัวที่ | อยู่ที่ | ทำงานเมื่อ |
|---|---|---|
| `showPage(name)` | ~2636 | ผู้ใช้กด nav |
| `setLang(lang)` ท่อนล่าง | ~2342–2352 | ผู้ใช้สลับภาษา → re-render หน้าที่เปิดอยู่ |

ทั้งคู่มี `if (... === 'xxx') loadXxx()` **คนละชุดกัน** และ**ไม่ครบเท่ากัน**

**กฎ:** เพิ่มหน้าใหม่ → ต้องแตะ **4 จุด**
1. `<div class="page" id="page-xxx">` (markup ~1458–1866)
2. `<div class="nav-item" onclick="showPage('xxx')" id="nav-xxx">` (~1351–1435)
3. `initApp()` ~2616–2621 — ใส่ `nav-xxx` ใน array ของ role ที่ควรเห็น (**ลืมข้อนี้ = nav ไม่โผล่ แต่หน้าทำงานปกติ** ดีบักหลง)
4. `showPage()` — เพิ่มบรรทัด loader
5. `setLang()` — เพิ่มบรรทัด re-render (ถ้าหน้านั้นมีข้อความจาก JS)

> 🐞 **บั๊กที่มีอยู่ตอนนี้:** `page-earnings` ทำข้อ 5 แต่**ไม่ได้ทำข้อ 4** —
> `loadEarnings()` ถูกเรียกจาก `setLang()` **ที่เดียวเท่านั้น** (ยืนยันแล้ว: grep เจอ 2 จุด = ตัวประกาศ + setLang)
> ⇒ กด nav "รายได้" ครั้งแรกจะเห็นแค่หัวข้อ `#earningsContent` ว่างเปล่า · จะขึ้นก็ต่อเมื่อสลับภาษา
> **แก้:** เพิ่ม `if (name === 'earnings') loadEarnings();` ใน `showPage()` (1 บรรทัด)

---

## 🔴 2. `saveSession` / `doLogout` ถูก **เขียนทับ** ท้ายไฟล์

```
function saveSession()  ประกาศที่ 2573  →  ถูกทับที่ 5852
function doLogout()     ประกาศที่ 2583  →  ถูกทับที่ 5858
```

ท้ายไฟล์ทำแบบนี้ (SESSION TIMEOUT section):
```js
const _origDoLogout = doLogout;
doLogout = function() { ...เคลียร์ timer...; _origDoLogout(); ...; };
```

**ผลกับการแก้โค้ด:** แก้ที่ `function doLogout()` บรรทัด 2583 → wrapper ที่ 5858 ยังครอบอยู่
ถ้าอยากเปลี่ยนพฤติกรรม logout จริงๆ **ต้องอ่านทั้งสองที่**

> ⚠️ และเพราะ wrapper ใช้ `_origDoLogout` ที่จับค่าไว้ตอน parse — ถ้าย้ายตำแหน่งประกาศ order จะพัง

---

## 🔴 3. Timer / Polling — ตัวไหนหยุด ตัวไหนไม่หยุด

`showPage()` เรียก `stopRosterPolling()` + `stopActiveShiftTimer()` **ทุกครั้งที่เปลี่ยนหน้า**
⇒ ถ้าเพิ่ม timer ใหม่ให้หน้าไหน **ต้องเพิ่ม stop ใน `showPage()` ด้วย** ไม่งั้นวิ่งค้างข้ามหน้า

| handle | ตั้งที่ | หยุดที่ | สถานะ |
|---|---|---|---|
| `_rosterPoll` (30s → `loadRoster`) | 4267 | 4195 ← `stopRosterPolling` | ✅ |
| `_rosterTick` (1s → นาฬิกาเดิน) | 4268 | 4196 | ✅ |
| `_asTick` (Active Shift) | 4398 | 4364 | ✅ |
| `_notifTimer` (30s → `refreshNotifBadge`) | 5399 | — | ⚠️ **ไม่มีใครเคลียร์** |
| `_sessionTimer` / `_sessionWarnTimer` / `_countdownTimer` | 5817–5828 | 5811–5815, 5859–5861 | ✅ (เคลียร์ใน logout wrapper) |

> `_notifTimer` วิ่งต่อหลัง logout → ยิง `GET /notifications/unread-count` ทุก 30 วิ ด้วย token เก่า → 401 ทุกครั้ง
> **ไม่ใช่เรื่องด่วน** (ไม่มีผลกับผู้ใช้) แต่ถ้าแตะ session logic เมื่อไหร่ ให้เก็บไปพร้อมกัน

---

## 🟠 4. Google Maps — state ค้างข้ามหน้า

```
_nearbyMap · _nearbyCircle · _nearbyMarker · _jobMarkers[]   (ประกาศ ~3642–3646)
autocompletes{}                                              (~4765)
```

- เป็น global · **ไม่ถูกทำลายเมื่อออกจากหน้า** (ต่างจาก timer ที่ `showPage` เคลียร์ให้)
- `initAllAutocompletes()` **เรียกตัวเองตอน parse ไฟล์** (~4953) และ retry ทุก 500ms จนกว่า `window.google` จะมา
- `showMapPreview()` marker ต้องมี `draggable:true` + `dragend` listener — **เคยพังมาแล้ว** (commit `d2f0a46`, อยู่ในตาราง Pitfalls ของ `CLAUDE.md`)

**กฎ:** อย่าใช้ `innerHTML = ...` ทับ container ที่มี map instance อยู่ — object จะลอยไม่มีใครอ้างถึงแต่ยัง listen event อยู่
นี่คือเหตุผลหนึ่งที่ **SPA แบบ `innerHTML` swap ทั้งหน้า (แผน Modularize ของ Gemini) จะพัง** ที่หน้า nearby

---

## 🟠 5. `_categoriesCache` — ทำไมเพิ่มหมวดใหม่แล้วไม่ขึ้น

```js
let _categoriesCache = null;              // ~5580
async function loadCategories() {
  if (_categoriesCache) return _categoriesCache;   // ← cache ตลอด session
  _categoriesCache = await api('GET', '/job-categories');
}
```

**ตรงกับที่เจอจริงตอน migration 026 (หมวดโรงแรม)** — INSERT ลง DB แล้วแต่ dropdown ไม่ขึ้น
เพราะ cache อยู่ใน memory ทั้ง session · **ต้อง hard-refresh** ถึงเห็น
⇒ ไม่ใช่บั๊ก ไม่ต้องไปไล่แก้ backend

---

## 🟠 6. `initCategoryDropdowns()` — ต้องเรียกซ้ำหลัง render form

ถูกเรียก **3 จุด** และทุกจุดจำเป็น:

| บรรทัด | ทำไม |
|---|---|
| 2630 | ตอน `initApp()` — ครั้งแรก |
| ~3508 | หลัง `loadWorkerProfile()` render form เสร็จ |
| ~3573 | หลัง render "ฟอร์มสร้างโปรไฟล์" (เคส 404 ไม่มีโปรไฟล์) |

**เหตุผล:** ฟอร์มพวกนี้ถูกสร้างด้วย `innerHTML` *หลัง* `initApp()` ⇒ `<select>` ยังไม่มีตอนเรียกครั้งแรก
นี่คือ pitfall ที่จดไว้ใน `CLAUDE.md` ("Dropdown ว่าง") — **ลบบรรทัดไหนออกก็พังทันที และไม่มี error ให้เห็น**

> 🔎 pattern ทั่วไป: **ทุกครั้งที่ render form ด้วย `innerHTML` แล้วในฟอร์มมี dropdown ที่ต้องเติมจาก API → ต้อง re-init**

---

## 🟠 7. Auth state — `var` ไม่ใช่ `const`

```js
var token    = localStorage.getItem('wh_token') || '';    // 2374
var userRole = localStorage.getItem('wh_role')  || '';    // 2375
var userId   = localStorage.getItem('wh_uid')   || '';    // 2376
```

- ถูกเขียนใหม่ที่ `saveSession()` (2573) และ `doLogout()` (2583) · เคลียร์ที่ START block (~5873) ถ้า session หมดอายุ
- `headers()` (2405) อ่าน `token` ทุกครั้งที่ยิง API ⇒ เปลี่ยนค่าแล้วมีผลทันทีทั้งระบบ
- **`userRole` คุมทั้ง nav visibility (`initApp`) และ logic ในหลาย loader** — เปลี่ยน role ต้อง `initApp()` ใหม่ ไม่ใช่แค่ `showPage()`

---

## 🟡 8. จุดเข้าโปรแกรม (entry point) อยู่ **ท้ายไฟล์**

`// ─── START ───` ~5869 — ไม่ใช่ `DOMContentLoaded` แต่รันตอน parse ถึงบรรทัดนั้นเลย

```
มี token+role?  → เช็ค wh_last_active เกิน 8 ชม.ไหม
                   เกิน  → localStorage.clear() + โชว์ authPage
                   ไม่เกิน → initApp() + _resetSessionTimers()
ไม่มี token     → handleGoogleCallback() → ถ้าไม่ใช่ callback ก็โชว์ authPage
```

**ผลกับการแก้โค้ด:** โค้ดที่วางไว้ *ใต้* บรรทัด 5869 จะรัน**หลัง**แอป init แล้ว
`SESSION TIMEOUT` section (5799–5868) จงใจอยู่ *เหนือ* START เพราะ START เรียก `_resetSessionTimers()`

---

## 🟡 9. `esc()` — XSS guard ที่ต้องไม่ลืม

`esc(str)` ที่ 2446 · ใช้อยู่ **99 จุด** ทั้งไฟล์
ทุกครั้งที่ render ข้อมูลจากผู้ใช้ (ชื่อ worker, ชื่อบริษัท, ข้อความรีวิว, ชื่องาน) ลง `innerHTML` **ต้องผ่าน `esc()`**

> เขียน card ใหม่แล้วลืม `esc()` = ช่องโหว่ XSS · ไม่มี lint จับให้ ต้องดูเอง
> เช็คเร็ว: `grep -n 'innerHTML' index.html` แล้วดูว่า template ข้างในมี `${esc(` ครบไหม

---

## 🟡 10. `<style>` ซ่อนอยู่ใน JS string

CSS ไม่ได้อยู่แค่ 3 ก้อนบนหัวไฟล์ (11–627, 630–667, 671–907)
มีอีก **5 ก้อนฝังใน template literal ของ JS** — ดูตาราง Layout ใน `INDEX_MAP.md` (แถวที่ mark ว่าอยู่ใน JS)

⇒ แก้สีปุ่มใน modal แล้วไม่เปลี่ยน? ลองหาใน string ก่อนโทษ cache

---

## 🟠 11. `_pendingApplyJobId` — state ค้างข้ามหน้า (เพิ่ม 2026-07-19)

```js
const _PENDING_KEY = 'wh_pending_apply';        // sessionStorage
let _pendingApplyJobId = /* อ่านจาก sessionStorage ตอน parse */;
function setPendingApply(v) { ... }            // ← ทางเข้าออกทางเดียว
```

ใช้จำ "งานที่ worker กดสมัครแต่โปรไฟล์ไม่ครบ" เพื่อพากลับมาหลังกรอกเสร็จ

> 🔴 **ห้ามเขียน `_pendingApplyJobId = ...` ตรงๆ — ต้องผ่าน `setPendingApply()` เสมอ**
> ไม่งั้น memory กับ sessionStorage จะไม่ตรงกัน แล้ว flow จะขาดหลัง refresh
> (เก็บใน sessionStorage เพราะเทสจริงพบว่าผู้ใช้ refresh ระหว่างกรอกโปรไฟล์แล้ว state หาย)

**เส้นทางของมัน — ต้องเคลียร์ครบทุกทางออก ไม่งั้นจะเด้งไปหน้า nearby มั่ว:**

| จุด | เกิดอะไร |
|---|---|
| `applyJob()` | **ตั้งค่า** เมื่อ `canApplyNow()` = false |
| `applyJob()` | **เคลียร์** เมื่อสมัครสำเร็จ |
| ปุ่ม "ไว้ทีหลัง" ใน gate modal | **เคลียร์** (inline `onclick="setPendingApply(null)"`) |
| `returnToPendingApply()` | **เคลียร์** ก่อนพากลับไปหน้า nearby |
| `doLogout()` | **`sessionStorage.clear()`** — กันค้างข้ามบัญชีในเบราว์เซอร์เดียวกัน |

⚠️ **ไม่ถูกเคลียร์ตอน logout** — แต่ไม่เป็นไรเพราะ `doLogout()` ทำ `localStorage.clear()` และหน้าถูก reset · ถ้าอนาคตเปลี่ยน logout ให้เป็น SPA แบบไม่ reload **ต้องมาเคลียร์ตัวนี้ด้วย**

**`returnToPendingApply()` ถูกเรียกใน `doCreateProfile()` + `doUpdateProfile()`**
คืน `true` = พาไปแล้ว → caller **ต้อง `return`** ไม่ให้ `loadWorkerProfile()` รันทับ (เพราะจะดึงหน้าเดิมกลับมา)

---

## 🟡 12. Gate โปรไฟล์ก่อนสมัครงาน — frontend ต้องตรงกับ backend

`workerChecklist()` (~3710) มี `required:true` = สิ่งที่ **backend บล็อกจริง** ที่ `POST /jobs/{id}/apply` (main.py ~1833):

| checklist item | backend เช็ค |
|---|---|
| `profile` | 404 `"สร้าง Worker Profile ก่อน"` |
| `phone` | 400 `"กรุณาเพิ่มเบอร์โทร..."` |
| `permit` (ต่างด้าวเท่านั้น) | 403 work permit ไม่มี/หมดอายุ |

`skills` / `location` เป็น `required:false` — **ไม่บล็อก** แต่ทำให้ `W_SKILLS 0.60` + `W_DISTANCE 0.25` เป็นศูนย์

> 🔴 **ถ้าแก้เงื่อนไขฝั่ง backend ต้องมาแก้ `workerChecklist()` ด้วย** ไม่งั้น frontend จะปล่อยผ่านแล้วไปตายที่ API เหมือนเดิม
> `applyJob()` ยังมี `try/catch` เดิมไว้เป็น safety net — แต่มันคือ UX ที่เราเพิ่งแก้ทิ้งไป อย่าให้ตกไปถึงตรงนั้น

---

## 🔴 13. ที่อยู่ในโปรไฟล์ **ไม่ใช่** พิกัดจับคู่งาน — เจตนาออกแบบ

> เพิ่ม 2026-07-19 หลังเทสจริง · **อ่านก่อนจะ "แก้" ให้โปรไฟล์มี lat/lng**

`POST/PATCH /workers/profile` ฝั่ง backend **รับ `lat`/`lng` ได้** (main.py ~1046, ~1057)
แต่ฟอร์มโปรไฟล์ฝั่งหน้าเว็บ **จงใจไม่ส่ง** — ส่งแค่ `address_text` · `province` · `postal_code` · `location_name`

**เหตุผล (การตัดสินใจของ founder):** งานรายวันคนงานย้ายที่ทั้งวัน · พิกัดบ้านที่ตั้งไว้ตายตัวจะทำให้ระยะทางผิด
⇒ **ระยะทางคิดจาก GPS ปัจจุบันตอนเปิดหน้าหางานเท่านั้น** · ที่อยู่ในโปรไฟล์ = ข้อมูลติดต่อ ไม่ใช่พิกัด

> 🚧 **ห้าม geocode ที่อยู่แล้วยัดลง `worker_profiles.location`** เพื่อ "แก้ให้ครบ" — จะทับ design เดิม
> และห้ามเพิ่มข้อ "ตั้งที่อยู่" กลับเข้า `workerChecklist()`

**ผลข้างเคียงที่ยังค้างอยู่ (ยังไม่แก้):**
`_cascade_backup_offer()` (main.py ~2934) กรอง `AND wp.location IS NOT NULL`
เมื่อไม่มีอะไรเขียน `wp.location` เลย ⇒ **worker ที่สมัครผ่าน UI ถูกตัดออกจากระบบ backup ทั้งหมด**
รวมกับ cron ที่ไม่รัน = anti-ghosting พังสองชั้น

**ทางแก้ที่ตกลงกันไว้ (ยังไม่ทำ):** ผูกพิกัดกับปุ่ม **"รับงาน"** — เปิด = ส่ง GPS ปัจจุบันไปกับ `PATCH /workers/profile { is_available, lat, lng }` · ปิด = หลุดจากการถูกเลือก
ต้องทำ consent ตาม `policies/02_PRIVACY_POLICY_PDPA.md` **ข้อ 2.1 + 9.1** ก่อนเปิดใช้

---

## 🟡 14. `FIELD_LABEL` ต้อง sync กับ Pydantic model ใน `main.py`

> เพิ่ม 2026-07-19 · หลังเจอ error ดิบหลุดถึงผู้ใช้ตอนเทส

`api()` (~2411) แปลง **422 validation error** ของ FastAPI เป็นภาษาคน ผ่าน `humanizeValidationError()`
โดยอ่านชื่อฟิลด์จาก `detail[].loc` แล้วเปิดตาราง `FIELD_LABEL`

**พฤติกรรม:**

| `detail` เป็น | ผลลัพธ์ |
|---|---|
| string (backend เขียนเอง เช่น `"งานนี้ปิดรับสมัครแล้ว"`) | ใช้ตามเดิม ไม่แตะ |
| array (Pydantic 422) | แปลงเป็น `"กรุณากรอกชื่อ-นามสกุล"` ฯลฯ |
| array แต่ฟิลด์ไม่มีใน `FIELD_LABEL` | fallback เป็นชื่อฟิลด์ดิบ + `" ไม่ถูกต้อง"` — **ไม่พัง แต่ผู้ใช้เห็นชื่อฟิลด์อังกฤษ** |

> 🔴 **เพิ่มฟิลด์ใหม่ใน Pydantic model → ต้องมาเติม `FIELD_LABEL` ด้วย**
> ไม่งั้นผู้ใช้จะเห็นเช่น `work_permit_expiry ไม่ถูกต้อง`

ของดิบยังถูกส่งเข้า `log('err', ...)` เหมือนเดิม ⇒ เปิด debug panel ยังดีบักได้ครบ

---

## 🔴 15. `syncSkillCode()` มี **2 โหมด** — ดูจำนวน argument

> เพิ่ม 2026-07-19 · ตอนทำ multi-skill เกือบทำฟอร์มโพสต์งานฝั่งนายจ้างพัง

```js
syncSkillCode(selectId, hiddenId)              // โหมดเดิม — เลือกได้ตัวเดียว (ทับค่า)
syncSkillCode(selectId, hiddenId, containerId) // โหมดใหม่ — สะสมเป็น chip สูงสุด 3
```

| ผู้เรียก | โหมด | ทำไม |
|---|---|---|
| `jobSkillSelect` (โพสต์งาน — employer) | **เดิม** 2 args | งานหนึ่งใบระบุตำแหน่งเดียว |
| `createSkillSelect` / `editSkillSelect` (โปรไฟล์ worker) | **ใหม่** 3 args | คนงานรายวันเป็น generalist ทำได้หลายอย่าง |

> 🔴 **ห้ามลบ branch `if (!containerId) { hidden.value = sel.value; return; }`**
> ถ้าลบ ฟอร์มโพสต์งานจะรีเซ็ต dropdown ตัวเองโดยไม่มี chip มารับ = ตัวเลือกหายต่อหน้าผู้ใช้

**คู่ id ที่ต้องมาครบ 3 ตัวเสมอในโหมดใหม่:** `xxxSkills` (hidden) · `xxxSkillChips` (container) · `xxxSkillSelect` (dropdown)
และต้องเรียก `renderSkillChips()` **หลัง form render** ทุกครั้ง (เหตุผลเดียวกับข้อ 6 — form สร้างด้วย `innerHTML` ทีหลัง)

`_titleLabels` เก็บ code → ชื่อไทย เติมตอน `loadJobTitles()` · ถ้ายังไม่เคยโหลดหมวดนั้น chip จะโชว์ **code ดิบ** (เช่น `laundry_attendant`) — ยอมรับได้ ไม่ใช่บั๊ก

---

## 🔴 16. โปรไฟล์บริษัท — สร้างได้ **ทางเดียว** เท่านั้น

> เพิ่ม 2026-07-19 · เดิมมีฟอร์มสร้าง 2 ตัว ตัวหนึ่งเก็บข้อมูลไม่ครบ

**ทางเดียวที่ถูก:** หน้า `page-employerprofile` → `loadEmployerProfile()` → `.ep-form` (`isNew = true`)
เก็บครบ: ชื่อบริษัท · ประเภท · ผู้ติดต่อ · **เบอร์โทร** · **พิกัดหน้างาน (lat/lng)** · รูปสถานที่

**ที่ลบทิ้งแล้ว:** ฟอร์มย่อ 3 ช่องใน `checkEmployerProfile()` + `doCreateEmployerProfile()`
เก็บแค่ company/biz/contact ⇒ นายจ้างที่สร้างทางนั้น **ไม่มีพิกัดและไม่มีเบอร์**
- `applyProfileLocationToPostJob()` ขึ้นเตือน "ยังไม่ได้ตั้งที่อยู่" → ต้องกรอกที่อยู่ใหม่ทุกครั้งที่โพสต์งาน
- ไม่มีเบอร์ → กระทบ contact-lock ตอนจ้าง

> 🚧 **ห้ามใส่ฟอร์มสร้างโปรไฟล์บริษัทกลับเข้าไปในหน้าโพสต์งาน** — ให้ส่งไปหน้าโปรไฟล์เสมอ
> ถ้าเพิ่มฟิลด์ใหม่ให้ employer ต้องเพิ่มที่ `.ep-form` ที่เดียว ไม่มีที่สองให้ลืม

**`wh_pending_postjob` (sessionStorage)** — `goCreateEmployerProfile()` ตั้งไว้ก่อนพาไปหน้าโปรไฟล์
`doSaveEmployerProfile()` อ่านค่านี้ **เฉพาะตอน `isNew`** → พากลับหน้าโพสต์งาน แล้วลบทิ้ง
ถ้าเข้าหน้าโปรไฟล์เองตรงๆ ค่านี้ไม่ถูกตั้ง ⇒ บันทึกแล้วอยู่หน้าเดิมตามปกติ
(`doLogout()` ทำ `sessionStorage.clear()` อยู่แล้ว — ไม่ค้างข้ามบัญชี)

---

## 🟡 17. Checklist ตั้งค่าบัญชี — มี **2 ชุด** คนละ role

| ฝั่ง | ฟังก์ชัน | ข้อ | ตัวบล็อก |
|---|---|---|---|
| worker | `workerChecklist()` | โปรไฟล์ · เบอร์โทร · (ต่างด้าว) work permit · **อาชีพ (แนะนำ)** | ไม่มีโปรไฟล์/เบอร์ = สมัครงานไม่ได้ |
| employer | `eChk` (inline ใน `loadDashboard`) | โปรไฟล์บริษัท · **ยืนยันตัวตน (แนะนำ)** · **โพสต์งานแรก (แนะนำ)** | ไม่มีโปรไฟล์ = โพสต์งานไม่ได้ |

**ฝั่ง employer กินหน้าที่ `verifyNudge` เดิมไปแล้ว** — ตัวเก่าเช็ค `empProfile ? ... : ''` ⇒ นายจ้างใหม่ที่ยังไม่มีโปรไฟล์**ไม่เห็นอะไรเลย** ซึ่งเป็นเคสที่ต้องการคำแนะนำมากที่สุด

> 🔴 `verifyNudge` ถูกลบทั้งตัวแปรและจุด render แล้ว — **ถ้าจะเอา nudge กลับมา ให้เพิ่มเป็นข้อใน `eChk` ไม่ใช่สร้าง banner ใหม่** ไม่งั้นจะมี UI 2 ตัวพูดเรื่องเดียวกัน
> ตอนลบ ผมลืมเอา `${verifyNudge}` ออกจากเทมเพลตรอบแรก → **ReferenceError ทำ dashboard นายจ้างพังทั้งหน้า** · จับได้ตอน grep · เตือนไว้ว่าลบตัวแปรต้องไล่ลบจุด render ด้วยเสมอ

**Welcome modal** — คุมด้วย localStorage คนละคีย์: `wh_onboarded_worker` / `wh_onboarded_employer`
`doLogout()` ทำ `localStorage.clear()` ⇒ ออกแล้วเข้าใหม่จะเห็น modal อีกครั้ง (ยอมรับได้)

---

## 📌 Checklist ก่อน commit แก้ index.html

- [ ] เพิ่ม/ลบหน้า → ครบ 5 จุดตามข้อ 1 แล้วยัง (markup / nav / initApp role array / showPage / setLang)
- [ ] เพิ่ม timer → ใส่ stop ใน `showPage()` แล้วยัง
- [ ] แตะ `doLogout` / `saveSession` → อ่าน wrapper ท้ายไฟล์ด้วยแล้วยัง
- [ ] render form ด้วย `innerHTML` ที่มี dropdown → re-init dropdown แล้วยัง
- [ ] render ข้อมูลผู้ใช้ → ผ่าน `esc()` ครบแล้วยัง
- [ ] รัน `python tools/gen_map.py` refresh แผนที่แล้วยัง
