# COUPLING_MAP — สิ่งที่อ่านจากโค้ดไม่เห็น

> ✍️ **ไฟล์นี้เขียนด้วยมือ · `gen_map.py` ไม่แตะ** — ถ้าเจอกับดักใหม่ให้เพิ่มลงที่นี่
> คู่กับ `INDEX_MAP.md` (auto-generated) — อันนั้นบอก "อะไรอยู่ตรงไหน" · อันนี้บอก **"แก้ตรงนี้แล้วอะไรพัง"**
>
> อัปเดตล่าสุด: 2026-07-19 · อ้างอิง `index.html` 6,085 บรรทัด sha `3a84f52cf83e`
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

## 📌 Checklist ก่อน commit แก้ index.html

- [ ] เพิ่ม/ลบหน้า → ครบ 5 จุดตามข้อ 1 แล้วยัง (markup / nav / initApp role array / showPage / setLang)
- [ ] เพิ่ม timer → ใส่ stop ใน `showPage()` แล้วยัง
- [ ] แตะ `doLogout` / `saveSession` → อ่าน wrapper ท้ายไฟล์ด้วยแล้วยัง
- [ ] render form ด้วย `innerHTML` ที่มี dropdown → re-init dropdown แล้วยัง
- [ ] render ข้อมูลผู้ใช้ → ผ่าน `esc()` ครบแล้วยัง
- [ ] รัน `python tools/gen_map.py` refresh แผนที่แล้วยัง
