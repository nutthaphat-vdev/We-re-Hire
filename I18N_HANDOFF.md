# i18n Handoff — WeHire Frontend
> อัปเดต: 2026-06-19 (Session 2)

---

## Pattern ที่ใช้

- LANG object มี 2 sub-object: `th` (line ~1305) และ `en` (line ~1435)
- `t('key')` — ดึงค่าตาม `_lang` ปัจจุบัน
- Static HTML ใช้ `data-i18n="key"` แล้ว `setLang()` set `textContent`
- JS-generated HTML ใช้ `t('key')` inline ใน template literal
- **แก้ไฟล์ด้วย Python `str.replace()` ผ่าน `mcp__workspace__bash` เท่านั้น — ห้ามใช้ Edit tool (ไฟล์ใหญ่ truncate)**

---

## ✅ เสร็จแล้ว

| หน้า / ส่วน | สถานะ |
|---|---|
| Landing page — hero, stats, how-it-works, features, market, footer | ✅ |
| Lang toggle — flag images (🇹🇭 🇺🇸) absolute top-right, no border | ✅ |
| Auth page subtitle | ✅ |
| Notifications page | ✅ |
| Find Jobs (nearby) page | ✅ |
| My Applications page | ✅ |
| My Reviews page | ✅ |
| Worker Profile page + KYC form | ✅ |
| Post Job page (all form labels) | ✅ |
| My Jobs page (title, status badges, auto-close) | ✅ |
| Employer Dashboard (stats, open jobs, verify banner) | ✅ |
| Employer create profile form + biz type options | ✅ |
| Candidates page (hire/reject/checkin/verify/dispute buttons) | ✅ |
| Notification title translation (`_notifTranslateTitle`) | ✅ |
| Review summary + submit button | ✅ |
| Category / zone / title dropdowns (dynamic — use name_en if available) | ✅ |

---

## 🟡 ยังเหลือ — เรียงตาม priority

### 1. Post Job — validation errors + success ⚠️ employer ใช้ตลอด
```
Lines ~3042–3073
'กรุณาระบุชื่อตำแหน่ง'             → t('err_no_title')
'กรุณาระบุค่าแรงที่ถูกต้อง'         → t('err_no_wage')
'กรุณาระบุจำนวนวันที่ถูกต้อง'       → t('err_no_days')
'กรุณาระบุเวลาเริ่ม-เลิกงานให้ครบ'  → t('err_incomplete_time')
'ช่วงเวลาทำงานต้องไม่เกิน 8 ชั่วโมง' → t('err_overtime')
'✅ โพสต์งานสำเร็จ!'                → t('postjob_success')
work hours summary "X ชม." (lines 3021/3026) → t('hr_unit') = 'ชม.' / 'hr'
```

### 2. Button state text ⚠️ employer + worker ใช้
```
Lines ~3428–3529
showContact: '📞 ดูเบอร์ติดต่อ' / '📞 ดูเบอร์' / '🙈 ซ่อน' / '📞 ข้อมูลติดต่อ'
doCheckin:   '⏳ รอ Employer ยืนยันเริ่มงาน' (→ t('wait_start') มีแล้ว) / 'มาถึงแล้ว 📍'
doComplete:  '⏳ รอ Employer ยืนยันจบงาน' (→ t('wait_verify') มีแล้ว) / '✅ งานเสร็จแล้ว'
doStart:     '▶️ กำลังทำงาน' → t('cand_working') มีแล้ว
doVerify:    '✅ สำเร็จแล้ว' / '✅ ยืนยันจบงาน' → t('cand_success') / t('cand_verify_btn') มีแล้ว
doDispute:   prompt text + '⚠️ ส่งเรื่องให้ admin ตรวจสอบแล้ว' + Phase3 alert
             → t('dispute_prompt') / t('dispute_sent') / t('dispute_phase3')
```

### 3. Worker profile create form 🔵 worker-facing
```
Lines ~2575–2640
'ยังไม่มีโปรไฟล์ — กรุณากรอกข้อมูลด้านล่าง' → t('worker_no_profile_msg')
'สร้างโปรไฟล์' heading                       → t('worker_create_title')
form labels: หมวดงาน, ตำแหน่งงาน, ประสบการณ์, ที่อยู่
'✅ สร้างโปรไฟล์สำเร็จ!'                      → t('profile_create_success')
'✅ อัปเดตสำเร็จ!'                             → t('profile_update_success')
```

### 4. Session / Auth 🔵
```
Lines 799–800:  'ออกเลย' / 'อยู่ต่อ' → t('session_logout_now') / t('session_stay')
Lines 1812/1823: login button loading state → t('logging_in')
```

### 5. Report modal 🔵 (static HTML)
```
Lines 1268–1287
'🚩 รายงานผู้ใช้' / 'เหตุผล' / reason options / 'รายละเอียด (ไม่บังคับ)'
'ยกเลิก' / 'ส่งรายงาน'
→ t('report_title') / t('report_reason_lbl') / t('report_spam') etc.
Line 3582: success '✅ ส่งรายงานแล้ว ทีมงานจะตรวจสอบ' → t('report_success')
```

### 6. Work permit status 🔵 worker profile
```
Lines 2467–2472
'⏳ รอ Admin ตรวจสอบ'                          → t('wp_pending')
'⚠️ ยังไม่ได้ upload'                          → t('wp_not_uploaded')
'📄 ดูเอกสาร'                                  → t('wp_view_doc')
'⚠️ Work permit จะหมดอายุใน X วัน'             → t('wp_expiring_soon') + interpolate
'❌ Work permit หมดอายุแล้ว กรุณาอัปเดตเอกสาร' → t('wp_expired')
```

### 7. Review flow 🔵
```
Line 4051: 'กรุณาให้คะแนนดาวก่อน'                                              → t('rev_no_star_err')
Line 4073: '✅ ส่งรีวิวเรียบร้อย! จะเปิดเผยเมื่ออีกฝ่ายส่งด้วย หรือครบ 7 วัน' → t('rev_success_msg')
Lines 3828/3830: btn 'อ่านทั้งหมด'                                              → t('notif_mark_all_done')
```

### 8. GPS / map text 🟡 ต่ำ
```
Lines 2720/2735/2742: 'กำลังระบุตำแหน่ง GPS...' / 'กรุงเทพมหานคร (ค่าเริ่มต้น)'
Lines 3287/3348/3361: geocoder / GPS status text
Line 3344: 'Browser ไม่รองรับ GPS'
```

### 9. Admin UI 🟡 ต่ำมาก (investor ไม่เห็น)
```
Lines 936/940/944/952: admin nav spans
Lines 1977–2169: admin stats, KYC review, dispute resolution
```

---

## Technical Notes

### เพิ่ม LANG keys
```python
OLD_TH = "    existing_key:'ค่าเก่า',"
NEW_TH = "    existing_key:'ค่าเก่า',\n    new_key:'ค่าใหม่',"
# ทำ EN เหมือนกัน — หา anchor ใน EN object
```

### Apostrophe ใน EN strings
```python
# ✅ ใช้ double quotes ถ้ามี 's หรือ 've
"    key:\"It's ready\","
# ❌ จะ JS syntax error
"    key:'It's ready',"
```

### Elements ที่มี child nodes
```html
<!-- wrap text ใน span เพื่อไม่ให้ setLang() ลบ child nodes -->
<button>
  <span data-i18n="key">ข้อความ</span>
  <svg ...></svg>
</button>
```

### Validate JS ก่อน commit เสมอ
```bash
node -e "
const html = require('fs').readFileSync('index.html','utf8');
const m = html.match(/<script>([\s\S]*?)<\/script>\s*<\/body>/);
new Function(m[1]); console.log('JS OK');"
```

### Git workflow
```powershell
# sandbox ทำ commit ไม่ได้ถ้า lock ติดค้าง
cd C:\Users\User\Downloads\Hire
git restore --staged .   # ถ้า staged มั่วๆ
git add index.html
git commit -m "feat: ..."
git push
```
