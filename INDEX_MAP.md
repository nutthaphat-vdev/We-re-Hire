# INDEX_MAP — แผนที่ `index.html`

> 🤖 **ไฟล์นี้ generate อัตโนมัติ — ห้ามแก้ด้วยมือ**  
> regenerate: `python tools/gen_map.py` · เช็คว่าเก่ายัง: `python tools/gen_map.py --check`  
> ส่วนที่เขียนด้วยมือ (coupling / กับดัก) อยู่ที่ **`COUPLING_MAP.md`** — สคริปต์ไม่แตะไฟล์นั้น

- generated: `2026-07-21 16:39` (BKK)
- source: `index.html` · **6,462 บรรทัด** · sha256 `9fcdbd3a2fd3`
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
| 1871–6269 | **JS (ก้อนหลัก)** · 4,398 บรรทัด |
| 6270–6283 | HTML markup |
| 6284–6364 | JS · 80 บรรทัด |
| 6365–6421 | HTML markup |
| 6422–6458 | JS · 36 บรรทัด |
| 6459–6462 | HTML markup |

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
| 3468 | WORKER PROFILE |
| 3814 | PROFILE COMPLETENESS (gate ก่อนสมัครงาน) |
| 3933 | NEARBY MAP INIT |
| 4067 | NEARBY JOBS |
| 4180 | MY APPLICATIONS |
| 4300 | EMPLOYER PROFILE CHECK |
| 4350 | POST JOB |
| 4484 | LIVE ROSTER |
| 4658 | ACTIVE SHIFT (worker — กระจกสะท้อน Roster) |
| 4725 | SETTINGS (role-aware) |
| 4810 | MY JOBS |
| 5060 | GOOGLE MAPS |
| 5183 | POST-JOB: inherit ที่อยู่หน้างานจากโปรไฟล์บริษัท |
| 5281 | JOB LIFECYCLE |
| 5433 | PAYMENT PROOF |
| 5549 | TRUST & SAFETY |
| 5605 | NOTIFICATIONS |
| 5850 | REVIEW SUMMARY |
| 5874 | JOB CATEGORIES CASCADE |
| 5929 | SKILLS แบบหลายตำแหน่ง (สูงสุด 3) |
| 6014 | REVIEWS |
| 6027 | Pending reviews |
| 6076 | Received reviews |
| 6176 | SESSION TIMEOUT |
| 6246 | START |

## 📄 หน้า (page) → ตัวโหลด → mount point

`showPage(key)` คือ router · มันซ่อน `.page` ทุกตัวแล้วโชว์ `#page-<key>` จากนั้นเรียก loader ตามตาราง

| page id | บรรทัด | key ที่ส่งให้ showPage | loader | mount point (JS เขียน innerHTML ลงตรงนี้) |
|---|---|---|---|---|
| `page-dashboard` | 1462–1472 | `dashboard` | — | `#dashContent` `#dashHeader` `#dashStats` |
| `page-nearby` | 1473–1516 | `nearby` | `initNearbyMap()` @3987 | `#nearbyResults` `#searchMapPreview` |
| `page-myapps` | 1517–1525 | `myapps` | `loadMyApps()` @4181 | `#myAppsContent` |
| `page-workerprofile` | 1526–1535 | `workerprofile` | `loadWorkerProfile()` @3469 | `#alertWorkerProfile` `#workerProfileContent` |
| `page-postjob` | 1536–1652 | `postjob` | `checkEmployerProfile()` @4301 | `#alertPostJob` `#employerProfileCheck` `#jobHoursSummary` `#jobProfileMapPreview` |
| `page-myjobs` | 1653–1661 | `myjobs` | `loadMyJobs()` @4820 | `#myJobsContent` |
| `page-roster` | 1662–1670 | `roster` | `loadRoster()` @4528 | `#rosterContent` |
| `page-employerprofile` | 1671–1679 | `employerprofile` | `loadEmployerProfile()` @2715 | `#employerProfileContent` |
| `page-activeshift` | 1680–1686 | `activeshift` | `loadActiveShift()` @4668 | `#activeShiftContent` |
| `page-settings` | 1687–1694 | `settings` | `loadSettings()` @4726 | `#settingsContent` |
| `page-admin-stats` | 1695–1703 | `admin-stats` | `loadAdminStats()` @2879 | `#adminStatsContent` |
| `page-admin-users` | 1704–1717 | `admin-users` | `loadAdminUsers()` @2957 | `#adminUsersContent` |
| `page-admin-kyc` | 1718–1726 | `admin-kyc` | `loadAdminKYC()` @2989 | `#adminKYCContent` |
| `page-admin-disputes` | 1727–1735 | `admin-disputes` | `loadAdminDisputes()` @3035 | `#adminDisputesContent` |
| `page-admin-jobs` | 1736–1749 | `admin-jobs` | `loadAdminJobs()` @3066 | `#adminJobsContent` |
| `page-admin-payments` | 1750–1758 | `admin-payments` | `loadAdminPayments()` @3102 | `#adminPaymentsContent` |
| `page-notifications` | 1759–1777 | `notifications` | `setNotifFilter()` @5719 | `#notificationsContent` |
| `page-earnings` | 1778–1785 | `earnings` | — | `#earningsContent` |
| `page-myreviews` | 1786–1870 | `myreviews` | `loadMyReviews()` @6016 | `#alertPay` `#alertReport` `#debugLogs` `#myReviewsContent` |

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
| 3176–3468 | async `loadDashboard()` |

### WORKER PROFILE

| บรรทัด | function |
|---|---|
| 3469–3748 | async `loadWorkerProfile()` |
| 3749–3754 | `showEditProfile()` |
| 3755–3783 | async `doCreateProfile()` |
| 3784–3828 | async `doUpdateProfile()` |

### PROFILE COMPLETENESS (gate ก่อนสมัครงาน)

| บรรทัด | function |
|---|---|
| 3829–3838 | `setPendingApply(v)` |
| 3839–3849 | async `fetchWorkerStatus()` |
| 3850–3878 | `workerChecklist(profile, phone)` |
| 3879–3908 | `showProfileGateModal(items)` |
| 3909–3916 | `goCompleteProfile()` |
| 3917–3941 | async `returnToPendingApply(alertId)` |

### NEARBY MAP INIT

| บรรทัด | function |
|---|---|
| 3942–3949 | `sizeNearby()` |
| 3950–3956 | `_onNearbyResize()` |
| 3957–3965 | `setNearbyScope(scope)` |
| 3966–3986 | `_nbPill(lat, lng, label, active, onClick)` |
| 3987–3991 | `initNearbyMap()` |
| 3992–4038 | `buildMap(lat, lng)` |
| 4039–4052 | `onGeoOk(pos)` |
| 4053–4079 | `onGeoFail()` |

### NEARBY JOBS

| บรรทัด | function |
|---|---|
| 4080–4147 | async `searchNearby()` |
| 4148–4180 | async `applyJob(jobId, lat, lng, btn)` |

### MY APPLICATIONS

| บรรทัด | function |
|---|---|
| 4181–4300 | async `loadMyApps()` |

### EMPLOYER PROFILE CHECK

| บรรทัด | function |
|---|---|
| 4301–4344 | async `checkEmployerProfile()` |
| 4345–4350 | `goCreateEmployerProfile()` |

### POST JOB

| บรรทัด | function |
|---|---|
| 4351–4358 | `calcWorkHours(start, end)` |
| 4359–4378 | `updateHoursSummary()` |
| 4379–4383 | `toggleJobOT()` |
| 4384–4437 | async `doPostJob()` |
| 4438–4486 | `ico(n, sz)` |

### LIVE ROSTER

| บรรทัด | function |
|---|---|
| 4487–4487 | `_elapsedSec(iso)` |
| 4488–4489 | `_hhmmss(s)` |
| 4490–4493 | `stopRosterPolling()` |
| 4494–4498 | `_fmtHM(iso)` |
| 4499–4505 | `_shiftSeconds(ws, we)` |
| 4506–4513 | `_minutesLate(ws)` |
| 4514–4516 | `_rosterRank(kind)` |
| 4517–4527 | `_rosterKind(c)` |
| 4528–4566 | async `loadRoster()` |
| 4567–4632 | `renderRosterRow(r)` |
| 4633–4644 | `tickRosterTimers()` |
| 4645–4651 | async `markNoShow(appId, btn)` |
| 4652–4659 | async `rosterVerifyPay(appId, jobId, jobTitle, amount, btn)` |

### ACTIVE SHIFT (worker — กระจกสะท้อน Roster)

| บรรทัด | function |
|---|---|
| 4660–4660 | `stopActiveShiftTimer()` |
| 4661–4667 | `tickActiveShiftTimers()` |
| 4668–4697 | async `loadActiveShift()` |
| 4698–4725 | `renderShiftCard(a)` |

### SETTINGS (role-aware)

| บรรทัด | function |
|---|---|
| 4726–4776 | async `loadSettings()` |
| 4777–4778 | `toggleLangSetting()` |
| 4779–4787 | `toggleAppTheme()` |
| 4788–4793 | async `dashHire(appId, btn)` |
| 4794–4804 | async `toggleAvailable(elm)` |
| 4805–4810 | async `toggleAvailInput(el)` |

### MY JOBS

| บรรทัด | function |
|---|---|
| 4811–4819 | `autoCloseCountdown(autoCloseAt)` |
| 4820–4870 | async `loadMyJobs()` |
| 4871–4921 | async `loadEarnings()` |
| 4922–4929 | async `closeJob(jobId)` |
| 4930–4936 | async `reopenJob(jobId)` |
| 4937–5025 | async `loadCandidates(jobId, jobTitle, jobWage)` |
| 5026–5062 | async `decide(appId, decision, btn)` |

### GOOGLE MAPS

| บรรทัด | function |
|---|---|
| 5063–5090 | `initPlacesAutocomplete(inputId, latId, lngId, displayId, mapPreviewId)` |
| 5091–5105 | `updatePinLocation(lat, lng, latId, lngId, displayId, inputId)` |
| 5106–5150 | `showMapPreview(containerId, lat, lng, label, latId, lngId, displayId, inputId)` |
| 5151–5181 | `setLocationFromGPS(latId, lngId, displayId, mapPreviewId, inputId)` |
| 5182–5183 | `useMyLocation()` |

### POST-JOB: inherit ที่อยู่หน้างานจากโปรไฟล์บริษัท

| บรรทัด | function |
|---|---|
| 5184–5208 | `applyProfileLocationToPostJob(emp)` |
| 5209–5216 | `toggleProfileLocation(cb)` |
| 5217–5243 | `showStaticMap(containerId, lat, lng, label)` |
| 5244–5250 | `initAllAutocompletes()` |
| 5251–5282 | async `showContact(appId, btn)` |

### JOB LIFECYCLE

| บรรทัด | function |
|---|---|
| 5283–5298 | async `doConfirmBackupWage(jobId, amount, btn)` |
| 5299–5315 | async `doAcceptBackup(appId, btn)` |
| 5316–5337 | async `doCheckin(appId, btn)` |
| 5338–5350 | async `doComplete(appId, btn)` |
| 5351–5363 | async `doStart(appId, btn)` |
| 5364–5376 | async `doVerify(appId, btn)` |
| 5377–5395 | async `showEmployerContact(appId, btn)` |
| 5396–5415 | async `toggleAutoConfirm(appId, btn)` |
| 5416–5434 | async `doDispute(appId, btn)` |

### PAYMENT PROOF

| บรรทัด | function |
|---|---|
| 5435–5439 | `payMethodChanged()` |
| 5440–5469 | `openPayModal(appId, jobId, jobTitle, amount)` |
| 5470–5473 | `closePayModal()` |
| 5474–5518 | async `doPaySubmit()` |
| 5519–5533 | async `doConfirmPayment(appId, btn)` |
| 5534–5550 | async `doReportPayment(appId, btn)` |

### TRUST & SAFETY

| บรรทัด | function |
|---|---|
| 5551–5563 | async `requestBackgroundCheck(btn)` |
| 5564–5576 | async `requestEmployerVerify(btn)` |
| 5577–5583 | `showReportModal(targetUserId)` |
| 5584–5587 | `closeReportModal()` |
| 5588–5622 | async `submitReport()` |

### NOTIFICATIONS

| บรรทัด | function |
|---|---|
| 5623–5650 | `_notifLabelMap(type)` |
| 5651–5681 | `_notifTranslateTitle(title)` |
| 5682–5692 | `_notifDateLabel(dateStr)` |
| 5693–5697 | async `startNotifPolling()` |
| 5698–5718 | async `refreshNotifBadge()` |
| 5719–5732 | `setNotifFilter(filter)` |
| 5733–5795 | async `loadNotifications()` |
| 5796–5811 | async `markNotifRead(notifId, btn)` |
| 5812–5829 | async `notifOpen(notifId, type, cardEl)` |
| 5830–5851 | async `markAllRead()` |

### REVIEW SUMMARY

| บรรทัด | function |
|---|---|
| 5852–5877 | async `loadReviewSummary(userIdForReview, role, containerId)` |

### JOB CATEGORIES CASCADE

| บรรทัด | function |
|---|---|
| 5878–5888 | async `loadCategories()` |
| 5889–5908 | async `initCategoryDropdowns()` |
| 5909–5944 | async `loadJobTitles(categorySelectId, titleSelectId)` |

### SKILLS แบบหลายตำแหน่ง (สูงสุด 3)

| บรรทัด | function |
|---|---|
| 5945–5959 | async `ensureTitleLabels()` |
| 5960–5964 | `getSkillList(hiddenInputId)` |
| 5965–5984 | `renderSkillChips(hiddenInputId, containerId, selectId)` |
| 5985–6004 | `syncSkillCode(titleSelectId, hiddenInputId, containerId)` |
| 6005–6015 | `removeSkill(code, hiddenInputId, containerId, selectId)` |

### REVIEWS

| บรรทัด | function |
|---|---|
| 6016–6112 | async `loadMyReviews()` |

### Received reviews

| บรรทัด | function |
|---|---|
| 6113–6126 | async `loadTagsForReview(appId, targetRole)` |
| 6127–6134 | `setStar(appId, val)` |
| 6135–6138 | `toggleTag(appId, tagKey, el)` |
| 6139–6144 | `setRehire(appId, val, btn)` |
| 6145–6184 | async `submitReview(appId, targetRole)` |

### SESSION TIMEOUT

| บรรทัด | function |
|---|---|
| 6185–6201 | `_resetSessionTimers()` |
| 6202–6214 | `_showSessionWarning()` |
| 6215–6308 | `extendSession()` |

### START

| บรรทัด | function |
|---|---|
| 6309–6312 | `openPolicyModal(tab)` |
| 6313–6315 | `closePolicyModal()` |
| 6316–6323 | `switchPolicyTab(tab)` |
| 6324–6359 | `showOnboardModal(role)` |
| 6360–6422 | `closeOnboardModal()` |
| 6423–6428 | `openDeleteAccountModal()` |
| 6429–6436 | `closeDeleteAccountModal()` |
| 6437 | async `doDeleteAccount()` |

## 🌐 Global state

> ตัวแปรพวกนี้อยู่นอก function = ทุกหน้าใช้ร่วมกัน · **แก้ function ที่เขียนตัวไหน ต้องไล่ดูทุกตัวที่อ่านมันด้วย**

| บรรทัด | ตัวแปร | ค่าเริ่มต้น | ถูกอ้างถึง (บรรทัด) |
|---|---|---|---|
| 2329 | `_lang` | `localStorage.getItem('wh_lang') || 'th'` | 2329, 2330, 2332, 2680, 4047, 4233, 4730, 4777, 4830, 5652, 5689, 5760 …(+7) |
| 2378 | `token` | `localStorage.getItem('wh_token') || ''` | 39, 40, 41, 42, 295, 2346, 2378, 2411, 2411, 2562, 2621, 2624 …(+12) |
| 2379 | `userRole` | `localStorage.getItem('wh_role') || ''` | 2379, 2622, 2625, 2627, 2633, 2654, 2654, 2656, 2657, 2658, 3171, 3181 …(+7) |
| 2380 | `userId` | `localStorage.getItem('wh_uid') || ''` | 2380, 2623, 2626, 2633, 2981, 2984, 3664, 6254 |
| 2381 | `callCount` | `0` | 2381, 2456, 2457 |
| 2382 | `debugOpen` | `false` | 2382, 2395, 2396, 2403, 2403, 2404, 2405 |
| 2718 | `myPhone` | `''` | 2718, 2719, 2751, 3473, 3474, 3618, 3699 |
| 2720 | `p` | `null` | 85, 95, 175, 480, 546, 556, 664, 757, 823, 833, 931, 931 …(+248) |
| 3473 | `myPhone` | `''` | 2718, 2719, 2751, 3473, 3474, 3618, 3699 |
| 3824 | `_pendingApplyJobId` | `(() => {` | 3819, 3824, 3830, 3918 |
| 3852 | `permitOk` | `true` | 3852, 3856, 3864 |
| 3934 | `_nearbyMap` | `null` | 3934, 3948, 3948, 3996, 3997, 4014, 4020, 4024, 4106, 4113, 4113, 4115 |
| 3935 | `_nearbyCircle` | `null` | 3935, 4018, 4018, 4023, 4030, 4030 |
| 3936 | `_nearbyMarker` | `null` | 3936, 4017, 4017, 4019 |
| 3937 | `_jobMarkers` | `[]` | 3937, 4095, 4096, 4116 |
| 3938 | `_nearbyScope` | `'related'` | 3938, 3958, 3960, 3961, 4092 |
| 4354 | `startMin` | `sh * 60 + sm, endMin = eh * 60 + em` | 4354, 4355, 4356 |
| 4485 | `_rosterPoll` | `null, _rosterTick = null, _rosterSig = n…` | 4485, 4491, 4491, 4491, 4531, 4563, 4563 |
| 4502 | `s` | `((h2*60+m2) - (h1*60+m1)) * 60` | 1255, 1255, 2215, 3170, 3171, 3173, 3494, 3494, 3496, 3496, 3520, 3521 …(+50) |
| 4510 | `late` | `(now.getHours()*60 + now.getMinutes()) -…` | 4510, 4511, 4511, 4511, 4511, 4512 |
| 4659 | `_asTick` | `null` | 4659, 4660, 4660, 4660, 4694 |
| 4731 | `availOn` | `true` | 4731, 4732, 4746, 4746, 4746 |
| 4748 | `h` | `''` | 2410, 2411, 2412, 4509, 4510, 4748, 4749, 4754, 4759, 4763, 4766, 4770 …(+2) |
| 5061 | `autocompletes` | `{}` | 5061, 5087 |
| 5607 | `_notifTimer` | `null` | 5607, 5695 |
| 5608 | `_notifFilter` | `'all'` | 2705, 5608, 5720, 5737, 5741 |
| 5876 | `_categoriesCache` | `null` | 5876, 5879, 5879, 5881, 5882 |
| 5944 | `_titleLabelsLang` | `null` | 5944, 5946, 5956 |
| 6181 | `_sessionTimer` | `null` | 6181, 6188, 6196, 6236 |
| 6182 | `_sessionWarnTimer` | `null` | 6182, 6189, 6194, 6237 |
| 6183 | `_countdownTimer` | `null` | 6183, 6192, 6205, 6211, 6238 |
| 6204 | `remaining` | `SESSION_WARN_MS / 1000` | 6204, 6206, 6207, 6208, 6211 |

## ⏱️ Timer / Polling

| ตั้งที่บรรทัด | handle | ชนิด | เรียก | เคลียร์ที่บรรทัด |
|---|---|---|---|---|
| 4563 | `_rosterPoll` | setInterval | `loadRoster` | 4491 |
| 4564 | `_rosterTick` | setInterval | `tickRosterTimers` | 4492 |
| 4694 | `_asTick` | setInterval | `tickActiveShiftTimers` | 4660 |
| 5695 | `_notifTimer` | setInterval | `refreshNotifBadge` | **⚠️ ไม่เคยเคลียร์** |
| 6194 | `_sessionWarnTimer` | setTimeout | `_showSessionWarning` | 6189, 6237 |
| 6196 | `_sessionTimer` | setTimeout | `(inline)` | 6188, 6236 |
| 6205 | `_countdownTimer` | setInterval | `(inline)` | 6192, 6211, 6238 |

## 🐒 Function ที่ถูกเขียนทับภายหลัง (monkey patch)

> 🔴 **อ่านก่อนแก้:** ตัวประกาศเดิมกับตัวที่ทำงานจริง**คนละตัว** · แก้ที่ `function foo()` เฉยๆ จะไม่มีผลกับ wrapper

| function | ประกาศเดิม | ถูกเขียนทับที่ |
|---|---|---|
| `saveSession` | 2620 | **6229** |
| `doLogout` | 2630 | **6235** |

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
| POST | `/applications/:x/accept-backup` | 5303 |
| POST | `/applications/:x/auto-confirm` | 5400 |
| POST | `/applications/:x/checkin` | 5321 |
| POST | `/applications/:x/complete` | 5342 |
| POST | `/applications/:x/confirm-payment` | 5524 |
| GET | `/applications/:x/contact` | 5262, 5380 |
| PATCH | `/applications/:x/decide` | 4790, 5030 |
| POST | `/applications/:x/dispute` | 5422 |
| PATCH | `/applications/:x/mark-noshow` | 4648 |
| FETCH | `/applications/:x/pay` | 5501 |
| POST | `/applications/:x/report-payment` | 5539 |
| POST | `/applications/:x/start` | 5355 |
| POST | `/applications/:x/verify` | 4654, 5368 |
| POST | `/auth/google/callback` | 2565 |
| GET | `/auth/google/url?role=:x` | 2542 |
| POST | `/auth/login` | 2583 |
| GET | `/auth/me` | 2719, 3191, 3474, 3842 |
| PATCH | `/auth/phone` | 2798, 3805 |
| POST | `/auth/register` | 2612 |
| POST | `/employers/profile` | 2795 |
| PATCH | `/employers/profile` | 2797 |
| GET | `/employers/profile/me` | 2721, 3320, 4305 |
| POST | `/employers/verify/request` | 5568 |
| FETCH | `/employers/workplace-photo` | 2826 |
| GET | `/job-categories` | 5881 |
| GET | `/job-categories/:x/titles` | 5919, 5950 |
| POST | `/jobs` | 4424 |
| POST | `/jobs/:x/apply` | 4167 |
| GET | `/jobs/:x/candidates` | 3325, 4544, 4941 |
| POST | `/jobs/:x/confirm-backup-wage` | 5287 |
| PATCH | `/jobs/:x/status` | 4925, 4932 |
| GET | `/jobs/mine` | 3321, 4534, 4824 |
| GET | `/jobs/nearby?lat=13.7018&lng=100.6011&radius_km=25&scope=all` | 3236 |
| GET | `/jobs/nearby?lat=:x&lng=:x&radius_km=:x&scope=:x` | 4092 |
| PATCH | `/notifications/:x/read` | 5798, 5817 |
| PATCH | `/notifications/read-all` | 5834 |
| GET | `/notifications/unread-count` | 5700 |
| GET | `/notifications:x` | 5738 |
| FETCH | `/public/stats` | 2511 |
| GET | `/review-tags?target_role=:x` | 6115 |
| POST | `/reviews` | 6167 |
| GET | `/reviews/me` | 6022 |
| GET | `/reviews/pending` | 6021 |
| FETCH | `/users/me` | 6442 |
| POST | `/users/report` | 5593 |
| GET | `/workers/applications` | 3189, 4185, 4675 |
| POST | `/workers/background-check/request` | 5555 |
| GET | `/workers/earnings` | 3190, 4875 |
| FETCH | `/workers/kyc/upload` | 2861 |
| POST | `/workers/profile` | 3765 |
| PATCH | `/workers/profile` | 3794, 4797, 4806 |
| GET | `/workers/profile/me` | 3188, 3476, 3841, 4674, 4732 |
| GET | `/zones` | 5892 |

---

_generated by `tools/gen_map.py` · source sha256 `9fcdbd3a2fd3`_
