# INDEX_MAP — แผนที่ `index.html`

> 🤖 **ไฟล์นี้ generate อัตโนมัติ — ห้ามแก้ด้วยมือ**  
> regenerate: `python tools/gen_map.py` · เช็คว่าเก่ายัง: `python tools/gen_map.py --check`  
> ส่วนที่เขียนด้วยมือ (coupling / กับดัก) อยู่ที่ **`COUPLING_MAP.md`** — สคริปต์ไม่แตะไฟล์นั้น

- generated: `2026-07-21 16:44` (BKK)
- source: `index.html` · **6,468 บรรทัด** · sha256 `6292c2d5fde0`
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
| 1871–6275 | **JS (ก้อนหลัก)** · 4,404 บรรทัด |
| 6276–6289 | HTML markup |
| 6290–6370 | JS · 80 บรรทัด |
| 6371–6427 | HTML markup |
| 6428–6464 | JS · 36 บรรทัด |
| 6465–6468 | HTML markup |

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
| 2838 | KYC UPLOAD |
| 2878 | ADMIN DASHBOARD |
| 3155 | SIDEBAR TOGGLE (mobile) |
| 3168 | DASHBOARD |
| 3474 | WORKER PROFILE |
| 3820 | PROFILE COMPLETENESS (gate ก่อนสมัครงาน) |
| 3939 | NEARBY MAP INIT |
| 4073 | NEARBY JOBS |
| 4186 | MY APPLICATIONS |
| 4306 | EMPLOYER PROFILE CHECK |
| 4356 | POST JOB |
| 4490 | LIVE ROSTER |
| 4664 | ACTIVE SHIFT (worker — กระจกสะท้อน Roster) |
| 4731 | SETTINGS (role-aware) |
| 4816 | MY JOBS |
| 5066 | GOOGLE MAPS |
| 5189 | POST-JOB: inherit ที่อยู่หน้างานจากโปรไฟล์บริษัท |
| 5287 | JOB LIFECYCLE |
| 5439 | PAYMENT PROOF |
| 5555 | TRUST & SAFETY |
| 5611 | NOTIFICATIONS |
| 5856 | REVIEW SUMMARY |
| 5880 | JOB CATEGORIES CASCADE |
| 5935 | SKILLS แบบหลายตำแหน่ง (สูงสุด 3) |
| 6020 | REVIEWS |
| 6033 | Pending reviews |
| 6082 | Received reviews |
| 6182 | SESSION TIMEOUT |
| 6252 | START |

## 📄 หน้า (page) → ตัวโหลด → mount point

`showPage(key)` คือ router · มันซ่อน `.page` ทุกตัวแล้วโชว์ `#page-<key>` จากนั้นเรียก loader ตามตาราง

| page id | บรรทัด | key ที่ส่งให้ showPage | loader | mount point (JS เขียน innerHTML ลงตรงนี้) |
|---|---|---|---|---|
| `page-dashboard` | 1462–1472 | `dashboard` | — | `#dashContent` `#dashHeader` `#dashStats` |
| `page-nearby` | 1473–1516 | `nearby` | `initNearbyMap()` @3993 | `#nearbyResults` `#searchMapPreview` |
| `page-myapps` | 1517–1525 | `myapps` | `loadMyApps()` @4187 | `#myAppsContent` |
| `page-workerprofile` | 1526–1535 | `workerprofile` | `loadWorkerProfile()` @3475 | `#alertWorkerProfile` `#workerProfileContent` |
| `page-postjob` | 1536–1652 | `postjob` | `checkEmployerProfile()` @4307 | `#alertPostJob` `#employerProfileCheck` `#jobHoursSummary` `#jobProfileMapPreview` |
| `page-myjobs` | 1653–1661 | `myjobs` | `loadMyJobs()` @4826 | `#myJobsContent` |
| `page-roster` | 1662–1670 | `roster` | `loadRoster()` @4534 | `#rosterContent` |
| `page-employerprofile` | 1671–1679 | `employerprofile` | `loadEmployerProfile()` @2715 | `#employerProfileContent` |
| `page-activeshift` | 1680–1686 | `activeshift` | `loadActiveShift()` @4674 | `#activeShiftContent` |
| `page-settings` | 1687–1694 | `settings` | `loadSettings()` @4732 | `#settingsContent` |
| `page-admin-stats` | 1695–1703 | `admin-stats` | `loadAdminStats()` @2879 | `#adminStatsContent` |
| `page-admin-users` | 1704–1717 | `admin-users` | `loadAdminUsers()` @2957 | `#adminUsersContent` |
| `page-admin-kyc` | 1718–1726 | `admin-kyc` | `loadAdminKYC()` @2989 | `#adminKYCContent` |
| `page-admin-disputes` | 1727–1735 | `admin-disputes` | `loadAdminDisputes()` @3035 | `#adminDisputesContent` |
| `page-admin-jobs` | 1736–1749 | `admin-jobs` | `loadAdminJobs()` @3066 | `#adminJobsContent` |
| `page-admin-payments` | 1750–1758 | `admin-payments` | `loadAdminPayments()` @3102 | `#adminPaymentsContent` |
| `page-notifications` | 1759–1777 | `notifications` | `setNotifFilter()` @5725 | `#notificationsContent` |
| `page-earnings` | 1778–1785 | `earnings` | — | `#earningsContent` |
| `page-myreviews` | 1786–1870 | `myreviews` | `loadMyReviews()` @6022 | `#alertPay` `#alertReport` `#debugLogs` `#myReviewsContent` |

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
| 2775–2817 | async `doSaveEmployerProfile(isNew)` |
| 2818–2838 | async `uploadEmpPhoto(input)` |

### KYC UPLOAD

| บรรทัด | function |
|---|---|
| 2839–2846 | `previewKYCImg(input, previewId)` |
| 2847–2878 | async `submitKYC()` |

### ADMIN DASHBOARD

| บรรทัด | function |
|---|---|
| 2879–2956 | async `loadAdminStats()` |
| 2957–2980 | async `loadAdminUsers(role=null, status=null, page=1)` |
| 2981–2988 | async `adminUpdateUserStatus(userId, status)` |
| 2989–3025 | async `loadAdminKYC()` |
| 3026–3034 | async `adminKYCReview(workerId, decision)` |
| 3035–3056 | async `loadAdminDisputes()` |
| 3057–3065 | async `adminResolveDispute(disputeId, decision)` |
| 3066–3094 | async `loadAdminJobs(status=null, page=1)` |
| 3095–3101 | async `adminUpdateJobStatus(jobId, status)` |
| 3102–3145 | async `loadAdminPayments()` |
| 3146–3155 | async `adminResolvePayment(appId)` |

### SIDEBAR TOGGLE (mobile)

| บรรทัด | function |
|---|---|
| 3156–3159 | `openSidebar()` |
| 3160–3163 | `closeSidebar()` |
| 3164–3168 | `toggleSidebar()` |

### DASHBOARD

| บรรทัด | function |
|---|---|
| 3169–3175 | `dashInitials(name)` |
| 3176–3474 | async `loadDashboard()` |

### WORKER PROFILE

| บรรทัด | function |
|---|---|
| 3475–3754 | async `loadWorkerProfile()` |
| 3755–3760 | `showEditProfile()` |
| 3761–3789 | async `doCreateProfile()` |
| 3790–3834 | async `doUpdateProfile()` |

### PROFILE COMPLETENESS (gate ก่อนสมัครงาน)

| บรรทัด | function |
|---|---|
| 3835–3844 | `setPendingApply(v)` |
| 3845–3855 | async `fetchWorkerStatus()` |
| 3856–3884 | `workerChecklist(profile, phone)` |
| 3885–3914 | `showProfileGateModal(items)` |
| 3915–3922 | `goCompleteProfile()` |
| 3923–3947 | async `returnToPendingApply(alertId)` |

### NEARBY MAP INIT

| บรรทัด | function |
|---|---|
| 3948–3955 | `sizeNearby()` |
| 3956–3962 | `_onNearbyResize()` |
| 3963–3971 | `setNearbyScope(scope)` |
| 3972–3992 | `_nbPill(lat, lng, label, active, onClick)` |
| 3993–3997 | `initNearbyMap()` |
| 3998–4044 | `buildMap(lat, lng)` |
| 4045–4058 | `onGeoOk(pos)` |
| 4059–4085 | `onGeoFail()` |

### NEARBY JOBS

| บรรทัด | function |
|---|---|
| 4086–4153 | async `searchNearby()` |
| 4154–4186 | async `applyJob(jobId, lat, lng, btn)` |

### MY APPLICATIONS

| บรรทัด | function |
|---|---|
| 4187–4306 | async `loadMyApps()` |

### EMPLOYER PROFILE CHECK

| บรรทัด | function |
|---|---|
| 4307–4350 | async `checkEmployerProfile()` |
| 4351–4356 | `goCreateEmployerProfile()` |

### POST JOB

| บรรทัด | function |
|---|---|
| 4357–4364 | `calcWorkHours(start, end)` |
| 4365–4384 | `updateHoursSummary()` |
| 4385–4389 | `toggleJobOT()` |
| 4390–4443 | async `doPostJob()` |
| 4444–4492 | `ico(n, sz)` |

### LIVE ROSTER

| บรรทัด | function |
|---|---|
| 4493–4493 | `_elapsedSec(iso)` |
| 4494–4495 | `_hhmmss(s)` |
| 4496–4499 | `stopRosterPolling()` |
| 4500–4504 | `_fmtHM(iso)` |
| 4505–4511 | `_shiftSeconds(ws, we)` |
| 4512–4519 | `_minutesLate(ws)` |
| 4520–4522 | `_rosterRank(kind)` |
| 4523–4533 | `_rosterKind(c)` |
| 4534–4572 | async `loadRoster()` |
| 4573–4638 | `renderRosterRow(r)` |
| 4639–4650 | `tickRosterTimers()` |
| 4651–4657 | async `markNoShow(appId, btn)` |
| 4658–4665 | async `rosterVerifyPay(appId, jobId, jobTitle, amount, btn)` |

### ACTIVE SHIFT (worker — กระจกสะท้อน Roster)

| บรรทัด | function |
|---|---|
| 4666–4666 | `stopActiveShiftTimer()` |
| 4667–4673 | `tickActiveShiftTimers()` |
| 4674–4703 | async `loadActiveShift()` |
| 4704–4731 | `renderShiftCard(a)` |

### SETTINGS (role-aware)

| บรรทัด | function |
|---|---|
| 4732–4782 | async `loadSettings()` |
| 4783–4784 | `toggleLangSetting()` |
| 4785–4793 | `toggleAppTheme()` |
| 4794–4799 | async `dashHire(appId, btn)` |
| 4800–4810 | async `toggleAvailable(elm)` |
| 4811–4816 | async `toggleAvailInput(el)` |

### MY JOBS

| บรรทัด | function |
|---|---|
| 4817–4825 | `autoCloseCountdown(autoCloseAt)` |
| 4826–4876 | async `loadMyJobs()` |
| 4877–4927 | async `loadEarnings()` |
| 4928–4935 | async `closeJob(jobId)` |
| 4936–4942 | async `reopenJob(jobId)` |
| 4943–5031 | async `loadCandidates(jobId, jobTitle, jobWage)` |
| 5032–5068 | async `decide(appId, decision, btn)` |

### GOOGLE MAPS

| บรรทัด | function |
|---|---|
| 5069–5096 | `initPlacesAutocomplete(inputId, latId, lngId, displayId, mapPreviewId)` |
| 5097–5111 | `updatePinLocation(lat, lng, latId, lngId, displayId, inputId)` |
| 5112–5156 | `showMapPreview(containerId, lat, lng, label, latId, lngId, displayId, inputId)` |
| 5157–5187 | `setLocationFromGPS(latId, lngId, displayId, mapPreviewId, inputId)` |
| 5188–5189 | `useMyLocation()` |

### POST-JOB: inherit ที่อยู่หน้างานจากโปรไฟล์บริษัท

| บรรทัด | function |
|---|---|
| 5190–5214 | `applyProfileLocationToPostJob(emp)` |
| 5215–5222 | `toggleProfileLocation(cb)` |
| 5223–5249 | `showStaticMap(containerId, lat, lng, label)` |
| 5250–5256 | `initAllAutocompletes()` |
| 5257–5288 | async `showContact(appId, btn)` |

### JOB LIFECYCLE

| บรรทัด | function |
|---|---|
| 5289–5304 | async `doConfirmBackupWage(jobId, amount, btn)` |
| 5305–5321 | async `doAcceptBackup(appId, btn)` |
| 5322–5343 | async `doCheckin(appId, btn)` |
| 5344–5356 | async `doComplete(appId, btn)` |
| 5357–5369 | async `doStart(appId, btn)` |
| 5370–5382 | async `doVerify(appId, btn)` |
| 5383–5401 | async `showEmployerContact(appId, btn)` |
| 5402–5421 | async `toggleAutoConfirm(appId, btn)` |
| 5422–5440 | async `doDispute(appId, btn)` |

### PAYMENT PROOF

| บรรทัด | function |
|---|---|
| 5441–5445 | `payMethodChanged()` |
| 5446–5475 | `openPayModal(appId, jobId, jobTitle, amount)` |
| 5476–5479 | `closePayModal()` |
| 5480–5524 | async `doPaySubmit()` |
| 5525–5539 | async `doConfirmPayment(appId, btn)` |
| 5540–5556 | async `doReportPayment(appId, btn)` |

### TRUST & SAFETY

| บรรทัด | function |
|---|---|
| 5557–5569 | async `requestBackgroundCheck(btn)` |
| 5570–5582 | async `requestEmployerVerify(btn)` |
| 5583–5589 | `showReportModal(targetUserId)` |
| 5590–5593 | `closeReportModal()` |
| 5594–5628 | async `submitReport()` |

### NOTIFICATIONS

| บรรทัด | function |
|---|---|
| 5629–5656 | `_notifLabelMap(type)` |
| 5657–5687 | `_notifTranslateTitle(title)` |
| 5688–5698 | `_notifDateLabel(dateStr)` |
| 5699–5703 | async `startNotifPolling()` |
| 5704–5724 | async `refreshNotifBadge()` |
| 5725–5738 | `setNotifFilter(filter)` |
| 5739–5801 | async `loadNotifications()` |
| 5802–5817 | async `markNotifRead(notifId, btn)` |
| 5818–5835 | async `notifOpen(notifId, type, cardEl)` |
| 5836–5857 | async `markAllRead()` |

### REVIEW SUMMARY

| บรรทัด | function |
|---|---|
| 5858–5883 | async `loadReviewSummary(userIdForReview, role, containerId)` |

### JOB CATEGORIES CASCADE

| บรรทัด | function |
|---|---|
| 5884–5894 | async `loadCategories()` |
| 5895–5914 | async `initCategoryDropdowns()` |
| 5915–5950 | async `loadJobTitles(categorySelectId, titleSelectId)` |

### SKILLS แบบหลายตำแหน่ง (สูงสุด 3)

| บรรทัด | function |
|---|---|
| 5951–5965 | async `ensureTitleLabels()` |
| 5966–5970 | `getSkillList(hiddenInputId)` |
| 5971–5990 | `renderSkillChips(hiddenInputId, containerId, selectId)` |
| 5991–6010 | `syncSkillCode(titleSelectId, hiddenInputId, containerId)` |
| 6011–6021 | `removeSkill(code, hiddenInputId, containerId, selectId)` |

### REVIEWS

| บรรทัด | function |
|---|---|
| 6022–6118 | async `loadMyReviews()` |

### Received reviews

| บรรทัด | function |
|---|---|
| 6119–6132 | async `loadTagsForReview(appId, targetRole)` |
| 6133–6140 | `setStar(appId, val)` |
| 6141–6144 | `toggleTag(appId, tagKey, el)` |
| 6145–6150 | `setRehire(appId, val, btn)` |
| 6151–6190 | async `submitReview(appId, targetRole)` |

### SESSION TIMEOUT

| บรรทัด | function |
|---|---|
| 6191–6207 | `_resetSessionTimers()` |
| 6208–6220 | `_showSessionWarning()` |
| 6221–6314 | `extendSession()` |

### START

| บรรทัด | function |
|---|---|
| 6315–6318 | `openPolicyModal(tab)` |
| 6319–6321 | `closePolicyModal()` |
| 6322–6329 | `switchPolicyTab(tab)` |
| 6330–6365 | `showOnboardModal(role)` |
| 6366–6428 | `closeOnboardModal()` |
| 6429–6434 | `openDeleteAccountModal()` |
| 6435–6442 | `closeDeleteAccountModal()` |
| 6443 | async `doDeleteAccount()` |

## 🌐 Global state

> ตัวแปรพวกนี้อยู่นอก function = ทุกหน้าใช้ร่วมกัน · **แก้ function ที่เขียนตัวไหน ต้องไล่ดูทุกตัวที่อ่านมันด้วย**

| บรรทัด | ตัวแปร | ค่าเริ่มต้น | ถูกอ้างถึง (บรรทัด) |
|---|---|---|---|
| 2329 | `_lang` | `localStorage.getItem('wh_lang') || 'th'` | 2329, 2330, 2332, 2680, 4053, 4239, 4736, 4783, 4836, 5658, 5695, 5766 …(+7) |
| 2378 | `token` | `localStorage.getItem('wh_token') || ''` | 39, 40, 41, 42, 295, 2346, 2378, 2411, 2411, 2562, 2621, 2624 …(+12) |
| 2379 | `userRole` | `localStorage.getItem('wh_role') || ''` | 2379, 2622, 2625, 2627, 2633, 2654, 2654, 2656, 2657, 2658, 3171, 3181 …(+7) |
| 2380 | `userId` | `localStorage.getItem('wh_uid') || ''` | 2380, 2623, 2626, 2633, 2981, 2984, 3670, 6260 |
| 2381 | `callCount` | `0` | 2381, 2456, 2457 |
| 2382 | `debugOpen` | `false` | 2382, 2395, 2396, 2403, 2403, 2404, 2405 |
| 2718 | `myPhone` | `''` | 2718, 2719, 2751, 3479, 3480, 3624, 3705 |
| 2720 | `p` | `null` | 85, 95, 175, 480, 546, 556, 664, 757, 823, 833, 931, 931 …(+248) |
| 3479 | `myPhone` | `''` | 2718, 2719, 2751, 3479, 3480, 3624, 3705 |
| 3830 | `_pendingApplyJobId` | `(() => {` | 3825, 3830, 3836, 3924 |
| 3858 | `permitOk` | `true` | 3858, 3862, 3870 |
| 3940 | `_nearbyMap` | `null` | 3940, 3954, 3954, 4002, 4003, 4020, 4026, 4030, 4112, 4119, 4119, 4121 |
| 3941 | `_nearbyCircle` | `null` | 3941, 4024, 4024, 4029, 4036, 4036 |
| 3942 | `_nearbyMarker` | `null` | 3942, 4023, 4023, 4025 |
| 3943 | `_jobMarkers` | `[]` | 3943, 4101, 4102, 4122 |
| 3944 | `_nearbyScope` | `'related'` | 3944, 3964, 3966, 3967, 4098 |
| 4360 | `startMin` | `sh * 60 + sm, endMin = eh * 60 + em` | 4360, 4361, 4362 |
| 4491 | `_rosterPoll` | `null, _rosterTick = null, _rosterSig = n…` | 4491, 4497, 4497, 4497, 4537, 4569, 4569 |
| 4508 | `s` | `((h2*60+m2) - (h1*60+m1)) * 60` | 1255, 1255, 2215, 3170, 3171, 3173, 3500, 3500, 3502, 3502, 3526, 3527 …(+50) |
| 4516 | `late` | `(now.getHours()*60 + now.getMinutes()) -…` | 4516, 4517, 4517, 4517, 4517, 4518 |
| 4665 | `_asTick` | `null` | 4665, 4666, 4666, 4666, 4700 |
| 4737 | `availOn` | `true` | 4737, 4738, 4752, 4752, 4752 |
| 4754 | `h` | `''` | 2410, 2411, 2412, 4515, 4516, 4754, 4755, 4760, 4765, 4769, 4772, 4776 …(+2) |
| 5067 | `autocompletes` | `{}` | 5067, 5093 |
| 5613 | `_notifTimer` | `null` | 5613, 5701 |
| 5614 | `_notifFilter` | `'all'` | 2705, 5614, 5726, 5743, 5747 |
| 5882 | `_categoriesCache` | `null` | 5882, 5885, 5885, 5887, 5888 |
| 5950 | `_titleLabelsLang` | `null` | 5950, 5952, 5962 |
| 6187 | `_sessionTimer` | `null` | 6187, 6194, 6202, 6242 |
| 6188 | `_sessionWarnTimer` | `null` | 6188, 6195, 6200, 6243 |
| 6189 | `_countdownTimer` | `null` | 6189, 6198, 6211, 6217, 6244 |
| 6210 | `remaining` | `SESSION_WARN_MS / 1000` | 6210, 6212, 6213, 6214, 6217 |

## ⏱️ Timer / Polling

| ตั้งที่บรรทัด | handle | ชนิด | เรียก | เคลียร์ที่บรรทัด |
|---|---|---|---|---|
| 4569 | `_rosterPoll` | setInterval | `loadRoster` | 4497 |
| 4570 | `_rosterTick` | setInterval | `tickRosterTimers` | 4498 |
| 4700 | `_asTick` | setInterval | `tickActiveShiftTimers` | 4666 |
| 5701 | `_notifTimer` | setInterval | `refreshNotifBadge` | **⚠️ ไม่เคยเคลียร์** |
| 6200 | `_sessionWarnTimer` | setTimeout | `_showSessionWarning` | 6195, 6243 |
| 6202 | `_sessionTimer` | setTimeout | `(inline)` | 6194, 6242 |
| 6211 | `_countdownTimer` | setInterval | `(inline)` | 6198, 6217, 6244 |

## 🐒 Function ที่ถูกเขียนทับภายหลัง (monkey patch)

> 🔴 **อ่านก่อนแก้:** ตัวประกาศเดิมกับตัวที่ทำงานจริง**คนละตัว** · แก้ที่ `function foo()` เฉยๆ จะไม่มีผลกับ wrapper

| function | ประกาศเดิม | ถูกเขียนทับที่ |
|---|---|---|
| `saveSession` | 2620 | **6235** |
| `doLogout` | 2630 | **6241** |

## 🔌 Backend endpoints ที่ frontend เรียก

`:x` = ส่วนที่เป็นตัวแปร (template literal)

| method | path | เรียกที่บรรทัด |
|---|---|---|
| GET | `/admin/disputes` | 3039 |
| PATCH | `/admin/disputes/:x/resolve` | 3061 |
| PATCH | `/admin/jobs/:x/status` | 3097 |
| PATCH | `/admin/kyc/:x/review` | 3030 |
| GET | `/admin/kyc/pending` | 2993 |
| GET | `/admin/payments` | 3106 |
| POST | `/admin/payments/:x/resolve` | 3150 |
| GET | `/admin/stats` | 2883 |
| PATCH | `/admin/users/:x/status` | 2984 |
| POST | `/applications/:x/accept-backup` | 5309 |
| POST | `/applications/:x/auto-confirm` | 5406 |
| POST | `/applications/:x/checkin` | 5327 |
| POST | `/applications/:x/complete` | 5348 |
| POST | `/applications/:x/confirm-payment` | 5530 |
| GET | `/applications/:x/contact` | 5268, 5386 |
| PATCH | `/applications/:x/decide` | 4796, 5036 |
| POST | `/applications/:x/dispute` | 5428 |
| PATCH | `/applications/:x/mark-noshow` | 4654 |
| FETCH | `/applications/:x/pay` | 5507 |
| POST | `/applications/:x/report-payment` | 5545 |
| POST | `/applications/:x/start` | 5361 |
| POST | `/applications/:x/verify` | 4660, 5374 |
| POST | `/auth/google/callback` | 2565 |
| GET | `/auth/google/url?role=:x` | 2542 |
| POST | `/auth/login` | 2583 |
| GET | `/auth/me` | 2719, 3191, 3480, 3848 |
| PATCH | `/auth/phone` | 2798, 3811 |
| POST | `/auth/register` | 2612 |
| POST | `/employers/profile` | 2795 |
| PATCH | `/employers/profile` | 2797 |
| GET | `/employers/profile/me` | 2721, 3320, 4311 |
| POST | `/employers/verify/request` | 5574 |
| FETCH | `/employers/workplace-photo` | 2826 |
| GET | `/job-categories` | 5887 |
| GET | `/job-categories/:x/titles` | 5925, 5956 |
| POST | `/jobs` | 4430 |
| POST | `/jobs/:x/apply` | 4173 |
| GET | `/jobs/:x/candidates` | 3325, 4550, 4947 |
| POST | `/jobs/:x/confirm-backup-wage` | 5293 |
| PATCH | `/jobs/:x/status` | 4931, 4938 |
| GET | `/jobs/mine` | 3321, 4540, 4830 |
| GET | `/jobs/nearby?lat=13.7018&lng=100.6011&radius_km=25&scope=all` | 3236 |
| GET | `/jobs/nearby?lat=:x&lng=:x&radius_km=:x&scope=:x` | 4098 |
| PATCH | `/notifications/:x/read` | 5804, 5823 |
| PATCH | `/notifications/read-all` | 5840 |
| GET | `/notifications/unread-count` | 5706 |
| GET | `/notifications:x` | 5744 |
| FETCH | `/public/stats` | 2511 |
| GET | `/review-tags?target_role=:x` | 6121 |
| POST | `/reviews` | 6173 |
| GET | `/reviews/me` | 6028 |
| GET | `/reviews/pending` | 6027 |
| FETCH | `/users/me` | 6448 |
| POST | `/users/report` | 5599 |
| GET | `/workers/applications` | 3189, 4191, 4681 |
| POST | `/workers/background-check/request` | 5561 |
| GET | `/workers/earnings` | 3190, 4881 |
| FETCH | `/workers/kyc/upload` | 2861 |
| POST | `/workers/profile` | 3771 |
| PATCH | `/workers/profile` | 3800, 4803, 4812 |
| GET | `/workers/profile/me` | 3188, 3482, 3847, 4680, 4738 |
| GET | `/zones` | 5898 |

---

_generated by `tools/gen_map.py` · source sha256 `6292c2d5fde0`_
