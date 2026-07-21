# INDEX_MAP — แผนที่ `index.html`

> 🤖 **ไฟล์นี้ generate อัตโนมัติ — ห้ามแก้ด้วยมือ**  
> regenerate: `python tools/gen_map.py` · เช็คว่าเก่ายัง: `python tools/gen_map.py --check`  
> ส่วนที่เขียนด้วยมือ (coupling / กับดัก) อยู่ที่ **`COUPLING_MAP.md`** — สคริปต์ไม่แตะไฟล์นั้น

- generated: `2026-07-21 16:15` (BKK)
- source: `index.html` · **6,453 บรรทัด** · sha256 `29dfa85cc663`
- 169 functions · 19 pages · 62 endpoints

---

## 🗺️ Layout ของไฟล์

| ช่วงบรรทัด | คืออะไร |
|---|---|
| 1–7 | HTML markup |
| 8–8 | JS · 0 บรรทัด |
| 9–9 | HTML markup |
| 10–10 | JS `src="https://maps.googleapis.com/maps/api/js?key=AIzaSyD73zN` · 0 บรรทัด |
| 11–631 | CSS · 620 บรรทัด |
| 632–633 | HTML markup |
| 634–671 | CSS · 37 บรรทัด |
| 672–674 | HTML markup |
| 675–911 | CSS · 236 บรรทัด |
| 912–1870 | HTML markup |
| 1871–6260 | **JS (ก้อนหลัก)** · 4,389 บรรทัด |
| 6261–6274 | HTML markup |
| 6275–6355 | JS · 80 บรรทัด |
| 6356–6412 | HTML markup |
| 6413–6449 | JS · 36 บรรทัด |
| 6450–6453 | HTML markup |

## 📑 Section ใน JS

| บรรทัด | Section |
|---|---|
| 1872 | MULTILANG |
| 2359 | THEME (login page) |
| 2376 | CONSTANTS |
| 2384 | DEBUG |
| 2408 | API |
| 2492 | HTML ESCAPE — ใช้ทุกจุดที่ render user input ใน innerHTML |
| 2503 | LANDING |
| 2523 | AUTH |
| 2648 | INIT |
| 2683 | NAV |
| 2714 | EMPLOYER PROFILE (company + workplace location) |
| 2836 | KYC UPLOAD |
| 2876 | ADMIN DASHBOARD |
| 3153 | SIDEBAR TOGGLE (mobile) |
| 3166 | DASHBOARD |
| 3459 | WORKER PROFILE |
| 3805 | PROFILE COMPLETENESS (gate ก่อนสมัครงาน) |
| 3924 | NEARBY MAP INIT |
| 4058 | NEARBY JOBS |
| 4171 | MY APPLICATIONS |
| 4291 | EMPLOYER PROFILE CHECK |
| 4341 | POST JOB |
| 4475 | LIVE ROSTER |
| 4649 | ACTIVE SHIFT (worker — กระจกสะท้อน Roster) |
| 4716 | SETTINGS (role-aware) |
| 4801 | MY JOBS |
| 5051 | GOOGLE MAPS |
| 5174 | POST-JOB: inherit ที่อยู่หน้างานจากโปรไฟล์บริษัท |
| 5272 | JOB LIFECYCLE |
| 5424 | PAYMENT PROOF |
| 5540 | TRUST & SAFETY |
| 5596 | NOTIFICATIONS |
| 5841 | REVIEW SUMMARY |
| 5865 | JOB CATEGORIES CASCADE |
| 5920 | SKILLS แบบหลายตำแหน่ง (สูงสุด 3) |
| 6005 | REVIEWS |
| 6018 | Pending reviews |
| 6067 | Received reviews |
| 6167 | SESSION TIMEOUT |
| 6237 | START |

## 📄 หน้า (page) → ตัวโหลด → mount point

`showPage(key)` คือ router · มันซ่อน `.page` ทุกตัวแล้วโชว์ `#page-<key>` จากนั้นเรียก loader ตามตาราง

| page id | บรรทัด | key ที่ส่งให้ showPage | loader | mount point (JS เขียน innerHTML ลงตรงนี้) |
|---|---|---|---|---|
| `page-dashboard` | 1462–1472 | `dashboard` | — | `#dashContent` `#dashHeader` `#dashStats` |
| `page-nearby` | 1473–1516 | `nearby` | `initNearbyMap()` @3978 | `#nearbyResults` `#searchMapPreview` |
| `page-myapps` | 1517–1525 | `myapps` | `loadMyApps()` @4172 | `#myAppsContent` |
| `page-workerprofile` | 1526–1535 | `workerprofile` | `loadWorkerProfile()` @3460 | `#alertWorkerProfile` `#workerProfileContent` |
| `page-postjob` | 1536–1652 | `postjob` | `checkEmployerProfile()` @4292 | `#alertPostJob` `#employerProfileCheck` `#jobHoursSummary` `#jobProfileMapPreview` |
| `page-myjobs` | 1653–1661 | `myjobs` | `loadMyJobs()` @4811 | `#myJobsContent` |
| `page-roster` | 1662–1670 | `roster` | `loadRoster()` @4519 | `#rosterContent` |
| `page-employerprofile` | 1671–1679 | `employerprofile` | `loadEmployerProfile()` @2715 | `#employerProfileContent` |
| `page-activeshift` | 1680–1686 | `activeshift` | `loadActiveShift()` @4659 | `#activeShiftContent` |
| `page-settings` | 1687–1694 | `settings` | `loadSettings()` @4717 | `#settingsContent` |
| `page-admin-stats` | 1695–1703 | `admin-stats` | `loadAdminStats()` @2877 | `#adminStatsContent` |
| `page-admin-users` | 1704–1717 | `admin-users` | `loadAdminUsers()` @2955 | `#adminUsersContent` |
| `page-admin-kyc` | 1718–1726 | `admin-kyc` | `loadAdminKYC()` @2987 | `#adminKYCContent` |
| `page-admin-disputes` | 1727–1735 | `admin-disputes` | `loadAdminDisputes()` @3033 | `#adminDisputesContent` |
| `page-admin-jobs` | 1736–1749 | `admin-jobs` | `loadAdminJobs()` @3064 | `#adminJobsContent` |
| `page-admin-payments` | 1750–1758 | `admin-payments` | `loadAdminPayments()` @3100 | `#adminPaymentsContent` |
| `page-notifications` | 1759–1777 | `notifications` | `setNotifFilter()` @5710 | `#notificationsContent` |
| `page-earnings` | 1778–1785 | `earnings` | — | `#earningsContent` |
| `page-myreviews` | 1786–1870 | `myreviews` | `loadMyReviews()` @6007 | `#alertPay` `#alertReport` `#debugLogs` `#myReviewsContent` |

## 🔧 Functions

### MULTILANG

| บรรทัด | function |
|---|---|
| 2330–2330 | `t(key)` |
| 2331–2359 | `setLang(lang)` |

### THEME (login page)

| บรรทัด | function |
|---|---|
| 2360–2367 | `renderAuthThemeIcon()` |
| 2368–2384 | `toggleAuthTheme()` |

### DEBUG

| บรรทัด | function |
|---|---|
| 2385–2401 | `log(type, msg)` |
| 2402–2408 | `toggleDebug()` |

### API

| บรรทัด | function |
|---|---|
| 2409–2429 | `headers()` |
| 2430–2454 | `humanizeValidationError(detail)` |
| 2455–2484 | async `api(method, path, body)` |
| 2485–2492 | `showAlert(id, msg, type='error')` |

### HTML ESCAPE — ใช้ทุกจุดที่ render user input ใน innerHTML

| บรรทัด | function |
|---|---|
| 2493–2503 | `esc(str)` |

### LANDING

| บรรทัด | function |
|---|---|
| 2504–2508 | `showAuthFromLanding()` |
| 2509–2523 | async `loadLandingStats()` |

### AUTH

| บรรทัด | function |
|---|---|
| 2524–2530 | `switchAuthTab(tab)` |
| 2531–2539 | `selectRole(role, el)` |
| 2540–2548 | async `doGoogleLogin(role)` |
| 2549–2577 | async `handleGoogleCallback()` |
| 2578–2595 | async `doLogin()` |
| 2596–2619 | async `doRegister()` |
| 2620–2629 | `saveSession(data)` |
| 2630–2638 | `doLogout()` |
| 2639–2648 | `copyToken()` |

### INIT

| บรรทัด | function |
|---|---|
| 2649–2683 | `initApp()` |

### NAV

| บรรทัด | function |
|---|---|
| 2684–2714 | `showPage(name)` |

### EMPLOYER PROFILE (company + workplace location)

| บรรทัด | function |
|---|---|
| 2715–2774 | async `loadEmployerProfile()` |
| 2775–2815 | async `doSaveEmployerProfile(isNew)` |
| 2816–2836 | async `uploadEmpPhoto(input)` |

### KYC UPLOAD

| บรรทัด | function |
|---|---|
| 2837–2844 | `previewKYCImg(input, previewId)` |
| 2845–2876 | async `submitKYC()` |

### ADMIN DASHBOARD

| บรรทัด | function |
|---|---|
| 2877–2954 | async `loadAdminStats()` |
| 2955–2978 | async `loadAdminUsers(role=null, status=null, page=1)` |
| 2979–2986 | async `adminUpdateUserStatus(userId, status)` |
| 2987–3023 | async `loadAdminKYC()` |
| 3024–3032 | async `adminKYCReview(workerId, decision)` |
| 3033–3054 | async `loadAdminDisputes()` |
| 3055–3063 | async `adminResolveDispute(disputeId, decision)` |
| 3064–3092 | async `loadAdminJobs(status=null, page=1)` |
| 3093–3099 | async `adminUpdateJobStatus(jobId, status)` |
| 3100–3143 | async `loadAdminPayments()` |
| 3144–3153 | async `adminResolvePayment(appId)` |

### SIDEBAR TOGGLE (mobile)

| บรรทัด | function |
|---|---|
| 3154–3157 | `openSidebar()` |
| 3158–3161 | `closeSidebar()` |
| 3162–3166 | `toggleSidebar()` |

### DASHBOARD

| บรรทัด | function |
|---|---|
| 3167–3173 | `dashInitials(name)` |
| 3174–3459 | async `loadDashboard()` |

### WORKER PROFILE

| บรรทัด | function |
|---|---|
| 3460–3739 | async `loadWorkerProfile()` |
| 3740–3745 | `showEditProfile()` |
| 3746–3774 | async `doCreateProfile()` |
| 3775–3819 | async `doUpdateProfile()` |

### PROFILE COMPLETENESS (gate ก่อนสมัครงาน)

| บรรทัด | function |
|---|---|
| 3820–3829 | `setPendingApply(v)` |
| 3830–3840 | async `fetchWorkerStatus()` |
| 3841–3869 | `workerChecklist(profile, phone)` |
| 3870–3899 | `showProfileGateModal(items)` |
| 3900–3907 | `goCompleteProfile()` |
| 3908–3932 | async `returnToPendingApply(alertId)` |

### NEARBY MAP INIT

| บรรทัด | function |
|---|---|
| 3933–3940 | `sizeNearby()` |
| 3941–3947 | `_onNearbyResize()` |
| 3948–3956 | `setNearbyScope(scope)` |
| 3957–3977 | `_nbPill(lat, lng, label, active, onClick)` |
| 3978–3982 | `initNearbyMap()` |
| 3983–4029 | `buildMap(lat, lng)` |
| 4030–4043 | `onGeoOk(pos)` |
| 4044–4070 | `onGeoFail()` |

### NEARBY JOBS

| บรรทัด | function |
|---|---|
| 4071–4138 | async `searchNearby()` |
| 4139–4171 | async `applyJob(jobId, lat, lng, btn)` |

### MY APPLICATIONS

| บรรทัด | function |
|---|---|
| 4172–4291 | async `loadMyApps()` |

### EMPLOYER PROFILE CHECK

| บรรทัด | function |
|---|---|
| 4292–4335 | async `checkEmployerProfile()` |
| 4336–4341 | `goCreateEmployerProfile()` |

### POST JOB

| บรรทัด | function |
|---|---|
| 4342–4349 | `calcWorkHours(start, end)` |
| 4350–4369 | `updateHoursSummary()` |
| 4370–4374 | `toggleJobOT()` |
| 4375–4428 | async `doPostJob()` |
| 4429–4477 | `ico(n, sz)` |

### LIVE ROSTER

| บรรทัด | function |
|---|---|
| 4478–4478 | `_elapsedSec(iso)` |
| 4479–4480 | `_hhmmss(s)` |
| 4481–4484 | `stopRosterPolling()` |
| 4485–4489 | `_fmtHM(iso)` |
| 4490–4496 | `_shiftSeconds(ws, we)` |
| 4497–4504 | `_minutesLate(ws)` |
| 4505–4507 | `_rosterRank(kind)` |
| 4508–4518 | `_rosterKind(c)` |
| 4519–4557 | async `loadRoster()` |
| 4558–4623 | `renderRosterRow(r)` |
| 4624–4635 | `tickRosterTimers()` |
| 4636–4642 | async `markNoShow(appId, btn)` |
| 4643–4650 | async `rosterVerifyPay(appId, jobId, jobTitle, amount, btn)` |

### ACTIVE SHIFT (worker — กระจกสะท้อน Roster)

| บรรทัด | function |
|---|---|
| 4651–4651 | `stopActiveShiftTimer()` |
| 4652–4658 | `tickActiveShiftTimers()` |
| 4659–4688 | async `loadActiveShift()` |
| 4689–4716 | `renderShiftCard(a)` |

### SETTINGS (role-aware)

| บรรทัด | function |
|---|---|
| 4717–4767 | async `loadSettings()` |
| 4768–4769 | `toggleLangSetting()` |
| 4770–4778 | `toggleAppTheme()` |
| 4779–4784 | async `dashHire(appId, btn)` |
| 4785–4795 | async `toggleAvailable(elm)` |
| 4796–4801 | async `toggleAvailInput(el)` |

### MY JOBS

| บรรทัด | function |
|---|---|
| 4802–4810 | `autoCloseCountdown(autoCloseAt)` |
| 4811–4861 | async `loadMyJobs()` |
| 4862–4912 | async `loadEarnings()` |
| 4913–4920 | async `closeJob(jobId)` |
| 4921–4927 | async `reopenJob(jobId)` |
| 4928–5016 | async `loadCandidates(jobId, jobTitle, jobWage)` |
| 5017–5053 | async `decide(appId, decision, btn)` |

### GOOGLE MAPS

| บรรทัด | function |
|---|---|
| 5054–5081 | `initPlacesAutocomplete(inputId, latId, lngId, displayId, mapPreviewId)` |
| 5082–5096 | `updatePinLocation(lat, lng, latId, lngId, displayId, inputId)` |
| 5097–5141 | `showMapPreview(containerId, lat, lng, label, latId, lngId, displayId, inputId)` |
| 5142–5172 | `setLocationFromGPS(latId, lngId, displayId, mapPreviewId, inputId)` |
| 5173–5174 | `useMyLocation()` |

### POST-JOB: inherit ที่อยู่หน้างานจากโปรไฟล์บริษัท

| บรรทัด | function |
|---|---|
| 5175–5199 | `applyProfileLocationToPostJob(emp)` |
| 5200–5207 | `toggleProfileLocation(cb)` |
| 5208–5234 | `showStaticMap(containerId, lat, lng, label)` |
| 5235–5241 | `initAllAutocompletes()` |
| 5242–5273 | async `showContact(appId, btn)` |

### JOB LIFECYCLE

| บรรทัด | function |
|---|---|
| 5274–5289 | async `doConfirmBackupWage(jobId, amount, btn)` |
| 5290–5306 | async `doAcceptBackup(appId, btn)` |
| 5307–5328 | async `doCheckin(appId, btn)` |
| 5329–5341 | async `doComplete(appId, btn)` |
| 5342–5354 | async `doStart(appId, btn)` |
| 5355–5367 | async `doVerify(appId, btn)` |
| 5368–5386 | async `showEmployerContact(appId, btn)` |
| 5387–5406 | async `toggleAutoConfirm(appId, btn)` |
| 5407–5425 | async `doDispute(appId, btn)` |

### PAYMENT PROOF

| บรรทัด | function |
|---|---|
| 5426–5430 | `payMethodChanged()` |
| 5431–5460 | `openPayModal(appId, jobId, jobTitle, amount)` |
| 5461–5464 | `closePayModal()` |
| 5465–5509 | async `doPaySubmit()` |
| 5510–5524 | async `doConfirmPayment(appId, btn)` |
| 5525–5541 | async `doReportPayment(appId, btn)` |

### TRUST & SAFETY

| บรรทัด | function |
|---|---|
| 5542–5554 | async `requestBackgroundCheck(btn)` |
| 5555–5567 | async `requestEmployerVerify(btn)` |
| 5568–5574 | `showReportModal(targetUserId)` |
| 5575–5578 | `closeReportModal()` |
| 5579–5613 | async `submitReport()` |

### NOTIFICATIONS

| บรรทัด | function |
|---|---|
| 5614–5641 | `_notifLabelMap(type)` |
| 5642–5672 | `_notifTranslateTitle(title)` |
| 5673–5683 | `_notifDateLabel(dateStr)` |
| 5684–5688 | async `startNotifPolling()` |
| 5689–5709 | async `refreshNotifBadge()` |
| 5710–5723 | `setNotifFilter(filter)` |
| 5724–5786 | async `loadNotifications()` |
| 5787–5802 | async `markNotifRead(notifId, btn)` |
| 5803–5820 | async `notifOpen(notifId, type, cardEl)` |
| 5821–5842 | async `markAllRead()` |

### REVIEW SUMMARY

| บรรทัด | function |
|---|---|
| 5843–5868 | async `loadReviewSummary(userIdForReview, role, containerId)` |

### JOB CATEGORIES CASCADE

| บรรทัด | function |
|---|---|
| 5869–5879 | async `loadCategories()` |
| 5880–5899 | async `initCategoryDropdowns()` |
| 5900–5935 | async `loadJobTitles(categorySelectId, titleSelectId)` |

### SKILLS แบบหลายตำแหน่ง (สูงสุด 3)

| บรรทัด | function |
|---|---|
| 5936–5950 | async `ensureTitleLabels()` |
| 5951–5955 | `getSkillList(hiddenInputId)` |
| 5956–5975 | `renderSkillChips(hiddenInputId, containerId, selectId)` |
| 5976–5995 | `syncSkillCode(titleSelectId, hiddenInputId, containerId)` |
| 5996–6006 | `removeSkill(code, hiddenInputId, containerId, selectId)` |

### REVIEWS

| บรรทัด | function |
|---|---|
| 6007–6103 | async `loadMyReviews()` |

### Received reviews

| บรรทัด | function |
|---|---|
| 6104–6117 | async `loadTagsForReview(appId, targetRole)` |
| 6118–6125 | `setStar(appId, val)` |
| 6126–6129 | `toggleTag(appId, tagKey, el)` |
| 6130–6135 | `setRehire(appId, val, btn)` |
| 6136–6175 | async `submitReview(appId, targetRole)` |

### SESSION TIMEOUT

| บรรทัด | function |
|---|---|
| 6176–6192 | `_resetSessionTimers()` |
| 6193–6205 | `_showSessionWarning()` |
| 6206–6299 | `extendSession()` |

### START

| บรรทัด | function |
|---|---|
| 6300–6303 | `openPolicyModal(tab)` |
| 6304–6306 | `closePolicyModal()` |
| 6307–6314 | `switchPolicyTab(tab)` |
| 6315–6350 | `showOnboardModal(role)` |
| 6351–6413 | `closeOnboardModal()` |
| 6414–6419 | `openDeleteAccountModal()` |
| 6420–6427 | `closeDeleteAccountModal()` |
| 6428 | async `doDeleteAccount()` |

## 🌐 Global state

> ตัวแปรพวกนี้อยู่นอก function = ทุกหน้าใช้ร่วมกัน · **แก้ function ที่เขียนตัวไหน ต้องไล่ดูทุกตัวที่อ่านมันด้วย**

| บรรทัด | ตัวแปร | ค่าเริ่มต้น | ถูกอ้างถึง (บรรทัด) |
|---|---|---|---|
| 2329 | `_lang` | `localStorage.getItem('wh_lang') || 'th'` | 2329, 2330, 2332, 2680, 4038, 4224, 4721, 4768, 4821, 5643, 5680, 5751 …(+7) |
| 2378 | `token` | `localStorage.getItem('wh_token') || ''` | 39, 40, 41, 42, 295, 2346, 2378, 2411, 2411, 2562, 2621, 2624 …(+12) |
| 2379 | `userRole` | `localStorage.getItem('wh_role') || ''` | 2379, 2622, 2625, 2627, 2633, 2654, 2654, 2656, 2657, 2658, 3169, 3179 …(+7) |
| 2380 | `userId` | `localStorage.getItem('wh_uid') || ''` | 2380, 2623, 2626, 2633, 2979, 2982, 3655, 6245 |
| 2381 | `callCount` | `0` | 2381, 2456, 2457 |
| 2382 | `debugOpen` | `false` | 2382, 2395, 2396, 2403, 2403, 2404, 2405 |
| 2718 | `myPhone` | `''` | 2718, 2719, 2751, 3464, 3465, 3609, 3690 |
| 2720 | `p` | `null` | 85, 95, 175, 480, 546, 556, 664, 757, 823, 833, 931, 931 …(+248) |
| 3464 | `myPhone` | `''` | 2718, 2719, 2751, 3464, 3465, 3609, 3690 |
| 3815 | `_pendingApplyJobId` | `(() => {` | 3810, 3815, 3821, 3909 |
| 3843 | `permitOk` | `true` | 3843, 3847, 3855 |
| 3925 | `_nearbyMap` | `null` | 3925, 3939, 3939, 3987, 3988, 4005, 4011, 4015, 4097, 4104, 4104, 4106 |
| 3926 | `_nearbyCircle` | `null` | 3926, 4009, 4009, 4014, 4021, 4021 |
| 3927 | `_nearbyMarker` | `null` | 3927, 4008, 4008, 4010 |
| 3928 | `_jobMarkers` | `[]` | 3928, 4086, 4087, 4107 |
| 3929 | `_nearbyScope` | `'related'` | 3929, 3949, 3951, 3952, 4083 |
| 4345 | `startMin` | `sh * 60 + sm, endMin = eh * 60 + em` | 4345, 4346, 4347 |
| 4476 | `_rosterPoll` | `null, _rosterTick = null, _rosterSig = n…` | 4476, 4482, 4482, 4482, 4522, 4554, 4554 |
| 4493 | `s` | `((h2*60+m2) - (h1*60+m1)) * 60` | 1255, 1255, 2215, 3168, 3169, 3171, 3485, 3485, 3487, 3487, 3511, 3512 …(+50) |
| 4501 | `late` | `(now.getHours()*60 + now.getMinutes()) -…` | 4501, 4502, 4502, 4502, 4502, 4503 |
| 4650 | `_asTick` | `null` | 4650, 4651, 4651, 4651, 4685 |
| 4722 | `availOn` | `true` | 4722, 4723, 4737, 4737, 4737 |
| 4739 | `h` | `''` | 2410, 2411, 2412, 4500, 4501, 4739, 4740, 4745, 4750, 4754, 4757, 4761 …(+2) |
| 5052 | `autocompletes` | `{}` | 5052, 5078 |
| 5598 | `_notifTimer` | `null` | 5598, 5686 |
| 5599 | `_notifFilter` | `'all'` | 2705, 5599, 5711, 5728, 5732 |
| 5867 | `_categoriesCache` | `null` | 5867, 5870, 5870, 5872, 5873 |
| 5935 | `_titleLabelsLang` | `null` | 5935, 5937, 5947 |
| 6172 | `_sessionTimer` | `null` | 6172, 6179, 6187, 6227 |
| 6173 | `_sessionWarnTimer` | `null` | 6173, 6180, 6185, 6228 |
| 6174 | `_countdownTimer` | `null` | 6174, 6183, 6196, 6202, 6229 |
| 6195 | `remaining` | `SESSION_WARN_MS / 1000` | 6195, 6197, 6198, 6199, 6202 |

## ⏱️ Timer / Polling

| ตั้งที่บรรทัด | handle | ชนิด | เรียก | เคลียร์ที่บรรทัด |
|---|---|---|---|---|
| 4554 | `_rosterPoll` | setInterval | `loadRoster` | 4482 |
| 4555 | `_rosterTick` | setInterval | `tickRosterTimers` | 4483 |
| 4685 | `_asTick` | setInterval | `tickActiveShiftTimers` | 4651 |
| 5686 | `_notifTimer` | setInterval | `refreshNotifBadge` | **⚠️ ไม่เคยเคลียร์** |
| 6185 | `_sessionWarnTimer` | setTimeout | `_showSessionWarning` | 6180, 6228 |
| 6187 | `_sessionTimer` | setTimeout | `(inline)` | 6179, 6227 |
| 6196 | `_countdownTimer` | setInterval | `(inline)` | 6183, 6202, 6229 |

## 🐒 Function ที่ถูกเขียนทับภายหลัง (monkey patch)

> 🔴 **อ่านก่อนแก้:** ตัวประกาศเดิมกับตัวที่ทำงานจริง**คนละตัว** · แก้ที่ `function foo()` เฉยๆ จะไม่มีผลกับ wrapper

| function | ประกาศเดิม | ถูกเขียนทับที่ |
|---|---|---|
| `saveSession` | 2620 | **6220** |
| `doLogout` | 2630 | **6226** |

## 🔌 Backend endpoints ที่ frontend เรียก

`:x` = ส่วนที่เป็นตัวแปร (template literal)

| method | path | เรียกที่บรรทัด |
|---|---|---|
| GET | `/admin/disputes` | 3037 |
| PATCH | `/admin/disputes/:x/resolve` | 3059 |
| PATCH | `/admin/jobs/:x/status` | 3095 |
| PATCH | `/admin/kyc/:x/review` | 3028 |
| GET | `/admin/kyc/pending` | 2991 |
| GET | `/admin/payments` | 3104 |
| POST | `/admin/payments/:x/resolve` | 3148 |
| GET | `/admin/stats` | 2881 |
| PATCH | `/admin/users/:x/status` | 2982 |
| POST | `/applications/:x/accept-backup` | 5294 |
| POST | `/applications/:x/auto-confirm` | 5391 |
| POST | `/applications/:x/checkin` | 5312 |
| POST | `/applications/:x/complete` | 5333 |
| POST | `/applications/:x/confirm-payment` | 5515 |
| GET | `/applications/:x/contact` | 5253, 5371 |
| PATCH | `/applications/:x/decide` | 4781, 5021 |
| POST | `/applications/:x/dispute` | 5413 |
| PATCH | `/applications/:x/mark-noshow` | 4639 |
| FETCH | `/applications/:x/pay` | 5492 |
| POST | `/applications/:x/report-payment` | 5530 |
| POST | `/applications/:x/start` | 5346 |
| POST | `/applications/:x/verify` | 4645, 5359 |
| POST | `/auth/google/callback` | 2565 |
| GET | `/auth/google/url?role=:x` | 2542 |
| POST | `/auth/login` | 2583 |
| GET | `/auth/me` | 2719, 3189, 3465, 3833 |
| PATCH | `/auth/phone` | 2798, 3796 |
| POST | `/auth/register` | 2612 |
| POST | `/employers/profile` | 2795 |
| PATCH | `/employers/profile` | 2797 |
| GET | `/employers/profile/me` | 2721, 3318, 4296 |
| POST | `/employers/verify/request` | 5559 |
| FETCH | `/employers/workplace-photo` | 2824 |
| GET | `/job-categories` | 5872 |
| GET | `/job-categories/:x/titles` | 5910, 5941 |
| POST | `/jobs` | 4415 |
| POST | `/jobs/:x/apply` | 4158 |
| GET | `/jobs/:x/candidates` | 3323, 4535, 4932 |
| POST | `/jobs/:x/confirm-backup-wage` | 5278 |
| PATCH | `/jobs/:x/status` | 4916, 4923 |
| GET | `/jobs/mine` | 3319, 4525, 4815 |
| GET | `/jobs/nearby?lat=13.7018&lng=100.6011&radius_km=25&scope=all` | 3234 |
| GET | `/jobs/nearby?lat=:x&lng=:x&radius_km=:x&scope=:x` | 4083 |
| PATCH | `/notifications/:x/read` | 5789, 5808 |
| PATCH | `/notifications/read-all` | 5825 |
| GET | `/notifications/unread-count` | 5691 |
| GET | `/notifications:x` | 5729 |
| FETCH | `/public/stats` | 2511 |
| GET | `/review-tags?target_role=:x` | 6106 |
| POST | `/reviews` | 6158 |
| GET | `/reviews/me` | 6013 |
| GET | `/reviews/pending` | 6012 |
| FETCH | `/users/me` | 6433 |
| POST | `/users/report` | 5584 |
| GET | `/workers/applications` | 3187, 4176, 4666 |
| POST | `/workers/background-check/request` | 5546 |
| GET | `/workers/earnings` | 3188, 4866 |
| FETCH | `/workers/kyc/upload` | 2859 |
| POST | `/workers/profile` | 3756 |
| PATCH | `/workers/profile` | 3785, 4788, 4797 |
| GET | `/workers/profile/me` | 3186, 3467, 3832, 4665, 4723 |
| GET | `/zones` | 5883 |

---

_generated by `tools/gen_map.py` · source sha256 `29dfa85cc663`_
