# INDEX_MAP — แผนที่ `index.html`

> 🤖 **ไฟล์นี้ generate อัตโนมัติ — ห้ามแก้ด้วยมือ**  
> regenerate: `python tools/gen_map.py` · เช็คว่าเก่ายัง: `python tools/gen_map.py --check`  
> ส่วนที่เขียนด้วยมือ (coupling / กับดัก) อยู่ที่ **`COUPLING_MAP.md`** — สคริปต์ไม่แตะไฟล์นั้น

- generated: `2026-07-21 15:53` (BKK)
- source: `index.html` · **6,416 บรรทัด** · sha256 `02f1c4ae627a`
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
| 1871–6223 | **JS (ก้อนหลัก)** · 4,352 บรรทัด |
| 6224–6237 | HTML markup |
| 6238–6318 | JS · 80 บรรทัด |
| 6319–6375 | HTML markup |
| 6376–6412 | JS · 36 บรรทัด |
| 6413–6416 | HTML markup |

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
| 2825 | KYC UPLOAD |
| 2865 | ADMIN DASHBOARD |
| 3142 | SIDEBAR TOGGLE (mobile) |
| 3155 | DASHBOARD |
| 3410 | WORKER PROFILE |
| 3756 | PROFILE COMPLETENESS (gate ก่อนสมัครงาน) |
| 3875 | NEARBY MAP INIT |
| 4009 | NEARBY JOBS |
| 4122 | MY APPLICATIONS |
| 4242 | EMPLOYER PROFILE CHECK |
| 4304 | POST JOB |
| 4438 | LIVE ROSTER |
| 4612 | ACTIVE SHIFT (worker — กระจกสะท้อน Roster) |
| 4679 | SETTINGS (role-aware) |
| 4764 | MY JOBS |
| 5014 | GOOGLE MAPS |
| 5137 | POST-JOB: inherit ที่อยู่หน้างานจากโปรไฟล์บริษัท |
| 5235 | JOB LIFECYCLE |
| 5387 | PAYMENT PROOF |
| 5503 | TRUST & SAFETY |
| 5559 | NOTIFICATIONS |
| 5804 | REVIEW SUMMARY |
| 5828 | JOB CATEGORIES CASCADE |
| 5883 | SKILLS แบบหลายตำแหน่ง (สูงสุด 3) |
| 5968 | REVIEWS |
| 5981 | Pending reviews |
| 6030 | Received reviews |
| 6130 | SESSION TIMEOUT |
| 6200 | START |

## 📄 หน้า (page) → ตัวโหลด → mount point

`showPage(key)` คือ router · มันซ่อน `.page` ทุกตัวแล้วโชว์ `#page-<key>` จากนั้นเรียก loader ตามตาราง

| page id | บรรทัด | key ที่ส่งให้ showPage | loader | mount point (JS เขียน innerHTML ลงตรงนี้) |
|---|---|---|---|---|
| `page-dashboard` | 1462–1472 | `dashboard` | — | `#dashContent` `#dashHeader` `#dashStats` |
| `page-nearby` | 1473–1516 | `nearby` | `initNearbyMap()` @3929 | `#nearbyResults` `#searchMapPreview` |
| `page-myapps` | 1517–1525 | `myapps` | `loadMyApps()` @4123 | `#myAppsContent` |
| `page-workerprofile` | 1526–1535 | `workerprofile` | `loadWorkerProfile()` @3411 | `#alertWorkerProfile` `#workerProfileContent` |
| `page-postjob` | 1536–1652 | `postjob` | `checkEmployerProfile()` @4243 | `#alertPostJob` `#employerProfileCheck` `#jobHoursSummary` `#jobProfileMapPreview` |
| `page-myjobs` | 1653–1661 | `myjobs` | `loadMyJobs()` @4774 | `#myJobsContent` |
| `page-roster` | 1662–1670 | `roster` | `loadRoster()` @4482 | `#rosterContent` |
| `page-employerprofile` | 1671–1679 | `employerprofile` | `loadEmployerProfile()` @2715 | `#employerProfileContent` |
| `page-activeshift` | 1680–1686 | `activeshift` | `loadActiveShift()` @4622 | `#activeShiftContent` |
| `page-settings` | 1687–1694 | `settings` | `loadSettings()` @4680 | `#settingsContent` |
| `page-admin-stats` | 1695–1703 | `admin-stats` | `loadAdminStats()` @2866 | `#adminStatsContent` |
| `page-admin-users` | 1704–1717 | `admin-users` | `loadAdminUsers()` @2944 | `#adminUsersContent` |
| `page-admin-kyc` | 1718–1726 | `admin-kyc` | `loadAdminKYC()` @2976 | `#adminKYCContent` |
| `page-admin-disputes` | 1727–1735 | `admin-disputes` | `loadAdminDisputes()` @3022 | `#adminDisputesContent` |
| `page-admin-jobs` | 1736–1749 | `admin-jobs` | `loadAdminJobs()` @3053 | `#adminJobsContent` |
| `page-admin-payments` | 1750–1758 | `admin-payments` | `loadAdminPayments()` @3089 | `#adminPaymentsContent` |
| `page-notifications` | 1759–1777 | `notifications` | `setNotifFilter()` @5673 | `#notificationsContent` |
| `page-earnings` | 1778–1785 | `earnings` | — | `#earningsContent` |
| `page-myreviews` | 1786–1870 | `myreviews` | `loadMyReviews()` @5970 | `#alertPay` `#alertReport` `#debugLogs` `#myReviewsContent` |

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
| 2775–2804 | async `doSaveEmployerProfile(isNew)` |
| 2805–2825 | async `uploadEmpPhoto(input)` |

### KYC UPLOAD

| บรรทัด | function |
|---|---|
| 2826–2833 | `previewKYCImg(input, previewId)` |
| 2834–2865 | async `submitKYC()` |

### ADMIN DASHBOARD

| บรรทัด | function |
|---|---|
| 2866–2943 | async `loadAdminStats()` |
| 2944–2967 | async `loadAdminUsers(role=null, status=null, page=1)` |
| 2968–2975 | async `adminUpdateUserStatus(userId, status)` |
| 2976–3012 | async `loadAdminKYC()` |
| 3013–3021 | async `adminKYCReview(workerId, decision)` |
| 3022–3043 | async `loadAdminDisputes()` |
| 3044–3052 | async `adminResolveDispute(disputeId, decision)` |
| 3053–3081 | async `loadAdminJobs(status=null, page=1)` |
| 3082–3088 | async `adminUpdateJobStatus(jobId, status)` |
| 3089–3132 | async `loadAdminPayments()` |
| 3133–3142 | async `adminResolvePayment(appId)` |

### SIDEBAR TOGGLE (mobile)

| บรรทัด | function |
|---|---|
| 3143–3146 | `openSidebar()` |
| 3147–3150 | `closeSidebar()` |
| 3151–3155 | `toggleSidebar()` |

### DASHBOARD

| บรรทัด | function |
|---|---|
| 3156–3162 | `dashInitials(name)` |
| 3163–3410 | async `loadDashboard()` |

### WORKER PROFILE

| บรรทัด | function |
|---|---|
| 3411–3690 | async `loadWorkerProfile()` |
| 3691–3696 | `showEditProfile()` |
| 3697–3725 | async `doCreateProfile()` |
| 3726–3770 | async `doUpdateProfile()` |

### PROFILE COMPLETENESS (gate ก่อนสมัครงาน)

| บรรทัด | function |
|---|---|
| 3771–3780 | `setPendingApply(v)` |
| 3781–3791 | async `fetchWorkerStatus()` |
| 3792–3820 | `workerChecklist(profile, phone)` |
| 3821–3850 | `showProfileGateModal(items)` |
| 3851–3858 | `goCompleteProfile()` |
| 3859–3883 | async `returnToPendingApply(alertId)` |

### NEARBY MAP INIT

| บรรทัด | function |
|---|---|
| 3884–3891 | `sizeNearby()` |
| 3892–3898 | `_onNearbyResize()` |
| 3899–3907 | `setNearbyScope(scope)` |
| 3908–3928 | `_nbPill(lat, lng, label, active, onClick)` |
| 3929–3933 | `initNearbyMap()` |
| 3934–3980 | `buildMap(lat, lng)` |
| 3981–3994 | `onGeoOk(pos)` |
| 3995–4021 | `onGeoFail()` |

### NEARBY JOBS

| บรรทัด | function |
|---|---|
| 4022–4089 | async `searchNearby()` |
| 4090–4122 | async `applyJob(jobId, lat, lng, btn)` |

### MY APPLICATIONS

| บรรทัด | function |
|---|---|
| 4123–4242 | async `loadMyApps()` |

### EMPLOYER PROFILE CHECK

| บรรทัด | function |
|---|---|
| 4243–4289 | async `checkEmployerProfile()` |
| 4290–4304 | async `doCreateEmployerProfile()` |

### POST JOB

| บรรทัด | function |
|---|---|
| 4305–4312 | `calcWorkHours(start, end)` |
| 4313–4332 | `updateHoursSummary()` |
| 4333–4337 | `toggleJobOT()` |
| 4338–4391 | async `doPostJob()` |
| 4392–4440 | `ico(n, sz)` |

### LIVE ROSTER

| บรรทัด | function |
|---|---|
| 4441–4441 | `_elapsedSec(iso)` |
| 4442–4443 | `_hhmmss(s)` |
| 4444–4447 | `stopRosterPolling()` |
| 4448–4452 | `_fmtHM(iso)` |
| 4453–4459 | `_shiftSeconds(ws, we)` |
| 4460–4467 | `_minutesLate(ws)` |
| 4468–4470 | `_rosterRank(kind)` |
| 4471–4481 | `_rosterKind(c)` |
| 4482–4520 | async `loadRoster()` |
| 4521–4586 | `renderRosterRow(r)` |
| 4587–4598 | `tickRosterTimers()` |
| 4599–4605 | async `markNoShow(appId, btn)` |
| 4606–4613 | async `rosterVerifyPay(appId, jobId, jobTitle, amount, btn)` |

### ACTIVE SHIFT (worker — กระจกสะท้อน Roster)

| บรรทัด | function |
|---|---|
| 4614–4614 | `stopActiveShiftTimer()` |
| 4615–4621 | `tickActiveShiftTimers()` |
| 4622–4651 | async `loadActiveShift()` |
| 4652–4679 | `renderShiftCard(a)` |

### SETTINGS (role-aware)

| บรรทัด | function |
|---|---|
| 4680–4730 | async `loadSettings()` |
| 4731–4732 | `toggleLangSetting()` |
| 4733–4741 | `toggleAppTheme()` |
| 4742–4747 | async `dashHire(appId, btn)` |
| 4748–4758 | async `toggleAvailable(elm)` |
| 4759–4764 | async `toggleAvailInput(el)` |

### MY JOBS

| บรรทัด | function |
|---|---|
| 4765–4773 | `autoCloseCountdown(autoCloseAt)` |
| 4774–4824 | async `loadMyJobs()` |
| 4825–4875 | async `loadEarnings()` |
| 4876–4883 | async `closeJob(jobId)` |
| 4884–4890 | async `reopenJob(jobId)` |
| 4891–4979 | async `loadCandidates(jobId, jobTitle, jobWage)` |
| 4980–5016 | async `decide(appId, decision, btn)` |

### GOOGLE MAPS

| บรรทัด | function |
|---|---|
| 5017–5044 | `initPlacesAutocomplete(inputId, latId, lngId, displayId, mapPreviewId)` |
| 5045–5059 | `updatePinLocation(lat, lng, latId, lngId, displayId, inputId)` |
| 5060–5104 | `showMapPreview(containerId, lat, lng, label, latId, lngId, displayId, inputId)` |
| 5105–5135 | `setLocationFromGPS(latId, lngId, displayId, mapPreviewId, inputId)` |
| 5136–5137 | `useMyLocation()` |

### POST-JOB: inherit ที่อยู่หน้างานจากโปรไฟล์บริษัท

| บรรทัด | function |
|---|---|
| 5138–5162 | `applyProfileLocationToPostJob(emp)` |
| 5163–5170 | `toggleProfileLocation(cb)` |
| 5171–5197 | `showStaticMap(containerId, lat, lng, label)` |
| 5198–5204 | `initAllAutocompletes()` |
| 5205–5236 | async `showContact(appId, btn)` |

### JOB LIFECYCLE

| บรรทัด | function |
|---|---|
| 5237–5252 | async `doConfirmBackupWage(jobId, amount, btn)` |
| 5253–5269 | async `doAcceptBackup(appId, btn)` |
| 5270–5291 | async `doCheckin(appId, btn)` |
| 5292–5304 | async `doComplete(appId, btn)` |
| 5305–5317 | async `doStart(appId, btn)` |
| 5318–5330 | async `doVerify(appId, btn)` |
| 5331–5349 | async `showEmployerContact(appId, btn)` |
| 5350–5369 | async `toggleAutoConfirm(appId, btn)` |
| 5370–5388 | async `doDispute(appId, btn)` |

### PAYMENT PROOF

| บรรทัด | function |
|---|---|
| 5389–5393 | `payMethodChanged()` |
| 5394–5423 | `openPayModal(appId, jobId, jobTitle, amount)` |
| 5424–5427 | `closePayModal()` |
| 5428–5472 | async `doPaySubmit()` |
| 5473–5487 | async `doConfirmPayment(appId, btn)` |
| 5488–5504 | async `doReportPayment(appId, btn)` |

### TRUST & SAFETY

| บรรทัด | function |
|---|---|
| 5505–5517 | async `requestBackgroundCheck(btn)` |
| 5518–5530 | async `requestEmployerVerify(btn)` |
| 5531–5537 | `showReportModal(targetUserId)` |
| 5538–5541 | `closeReportModal()` |
| 5542–5576 | async `submitReport()` |

### NOTIFICATIONS

| บรรทัด | function |
|---|---|
| 5577–5604 | `_notifLabelMap(type)` |
| 5605–5635 | `_notifTranslateTitle(title)` |
| 5636–5646 | `_notifDateLabel(dateStr)` |
| 5647–5651 | async `startNotifPolling()` |
| 5652–5672 | async `refreshNotifBadge()` |
| 5673–5686 | `setNotifFilter(filter)` |
| 5687–5749 | async `loadNotifications()` |
| 5750–5765 | async `markNotifRead(notifId, btn)` |
| 5766–5783 | async `notifOpen(notifId, type, cardEl)` |
| 5784–5805 | async `markAllRead()` |

### REVIEW SUMMARY

| บรรทัด | function |
|---|---|
| 5806–5831 | async `loadReviewSummary(userIdForReview, role, containerId)` |

### JOB CATEGORIES CASCADE

| บรรทัด | function |
|---|---|
| 5832–5842 | async `loadCategories()` |
| 5843–5862 | async `initCategoryDropdowns()` |
| 5863–5898 | async `loadJobTitles(categorySelectId, titleSelectId)` |

### SKILLS แบบหลายตำแหน่ง (สูงสุด 3)

| บรรทัด | function |
|---|---|
| 5899–5913 | async `ensureTitleLabels()` |
| 5914–5918 | `getSkillList(hiddenInputId)` |
| 5919–5938 | `renderSkillChips(hiddenInputId, containerId, selectId)` |
| 5939–5958 | `syncSkillCode(titleSelectId, hiddenInputId, containerId)` |
| 5959–5969 | `removeSkill(code, hiddenInputId, containerId, selectId)` |

### REVIEWS

| บรรทัด | function |
|---|---|
| 5970–6066 | async `loadMyReviews()` |

### Received reviews

| บรรทัด | function |
|---|---|
| 6067–6080 | async `loadTagsForReview(appId, targetRole)` |
| 6081–6088 | `setStar(appId, val)` |
| 6089–6092 | `toggleTag(appId, tagKey, el)` |
| 6093–6098 | `setRehire(appId, val, btn)` |
| 6099–6138 | async `submitReview(appId, targetRole)` |

### SESSION TIMEOUT

| บรรทัด | function |
|---|---|
| 6139–6155 | `_resetSessionTimers()` |
| 6156–6168 | `_showSessionWarning()` |
| 6169–6262 | `extendSession()` |

### START

| บรรทัด | function |
|---|---|
| 6263–6266 | `openPolicyModal(tab)` |
| 6267–6269 | `closePolicyModal()` |
| 6270–6277 | `switchPolicyTab(tab)` |
| 6278–6313 | `showOnboardModal(role)` |
| 6314–6376 | `closeOnboardModal()` |
| 6377–6382 | `openDeleteAccountModal()` |
| 6383–6390 | `closeDeleteAccountModal()` |
| 6391 | async `doDeleteAccount()` |

## 🌐 Global state

> ตัวแปรพวกนี้อยู่นอก function = ทุกหน้าใช้ร่วมกัน · **แก้ function ที่เขียนตัวไหน ต้องไล่ดูทุกตัวที่อ่านมันด้วย**

| บรรทัด | ตัวแปร | ค่าเริ่มต้น | ถูกอ้างถึง (บรรทัด) |
|---|---|---|---|
| 2329 | `_lang` | `localStorage.getItem('wh_lang') || 'th'` | 2329, 2330, 2332, 2680, 3989, 4175, 4684, 4731, 4784, 5606, 5643, 5714 …(+7) |
| 2378 | `token` | `localStorage.getItem('wh_token') || ''` | 39, 40, 41, 42, 295, 2346, 2378, 2411, 2411, 2562, 2621, 2624 …(+12) |
| 2379 | `userRole` | `localStorage.getItem('wh_role') || ''` | 2379, 2622, 2625, 2627, 2633, 2654, 2654, 2656, 2657, 2658, 3158, 3168 …(+7) |
| 2380 | `userId` | `localStorage.getItem('wh_uid') || ''` | 2380, 2623, 2626, 2633, 2968, 2971, 3606, 6208 |
| 2381 | `callCount` | `0` | 2381, 2456, 2457 |
| 2382 | `debugOpen` | `false` | 2382, 2395, 2396, 2403, 2403, 2404, 2405 |
| 2718 | `myPhone` | `''` | 2718, 2719, 2751, 3415, 3416, 3560, 3641 |
| 2720 | `p` | `null` | 85, 95, 175, 480, 546, 556, 664, 757, 823, 833, 931, 931 …(+248) |
| 3415 | `myPhone` | `''` | 2718, 2719, 2751, 3415, 3416, 3560, 3641 |
| 3766 | `_pendingApplyJobId` | `(() => {` | 3761, 3766, 3772, 3860 |
| 3794 | `permitOk` | `true` | 3794, 3798, 3806 |
| 3876 | `_nearbyMap` | `null` | 3876, 3890, 3890, 3938, 3939, 3956, 3962, 3966, 4048, 4055, 4055, 4057 |
| 3877 | `_nearbyCircle` | `null` | 3877, 3960, 3960, 3965, 3972, 3972 |
| 3878 | `_nearbyMarker` | `null` | 3878, 3959, 3959, 3961 |
| 3879 | `_jobMarkers` | `[]` | 3879, 4037, 4038, 4058 |
| 3880 | `_nearbyScope` | `'related'` | 3880, 3900, 3902, 3903, 4034 |
| 4308 | `startMin` | `sh * 60 + sm, endMin = eh * 60 + em` | 4308, 4309, 4310 |
| 4439 | `_rosterPoll` | `null, _rosterTick = null, _rosterSig = n…` | 4439, 4445, 4445, 4445, 4485, 4517, 4517 |
| 4456 | `s` | `((h2*60+m2) - (h1*60+m1)) * 60` | 1255, 1255, 2215, 3157, 3158, 3160, 3436, 3436, 3438, 3438, 3462, 3463 …(+50) |
| 4464 | `late` | `(now.getHours()*60 + now.getMinutes()) -…` | 4464, 4465, 4465, 4465, 4465, 4466 |
| 4613 | `_asTick` | `null` | 4613, 4614, 4614, 4614, 4648 |
| 4685 | `availOn` | `true` | 4685, 4686, 4700, 4700, 4700 |
| 4702 | `h` | `''` | 2410, 2411, 2412, 4463, 4464, 4702, 4703, 4708, 4713, 4717, 4720, 4724 …(+2) |
| 5015 | `autocompletes` | `{}` | 5015, 5041 |
| 5561 | `_notifTimer` | `null` | 5561, 5649 |
| 5562 | `_notifFilter` | `'all'` | 2705, 5562, 5674, 5691, 5695 |
| 5830 | `_categoriesCache` | `null` | 5830, 5833, 5833, 5835, 5836 |
| 5898 | `_titleLabelsLang` | `null` | 5898, 5900, 5910 |
| 6135 | `_sessionTimer` | `null` | 6135, 6142, 6150, 6190 |
| 6136 | `_sessionWarnTimer` | `null` | 6136, 6143, 6148, 6191 |
| 6137 | `_countdownTimer` | `null` | 6137, 6146, 6159, 6165, 6192 |
| 6158 | `remaining` | `SESSION_WARN_MS / 1000` | 6158, 6160, 6161, 6162, 6165 |

## ⏱️ Timer / Polling

| ตั้งที่บรรทัด | handle | ชนิด | เรียก | เคลียร์ที่บรรทัด |
|---|---|---|---|---|
| 4517 | `_rosterPoll` | setInterval | `loadRoster` | 4445 |
| 4518 | `_rosterTick` | setInterval | `tickRosterTimers` | 4446 |
| 4648 | `_asTick` | setInterval | `tickActiveShiftTimers` | 4614 |
| 5649 | `_notifTimer` | setInterval | `refreshNotifBadge` | **⚠️ ไม่เคยเคลียร์** |
| 6148 | `_sessionWarnTimer` | setTimeout | `_showSessionWarning` | 6143, 6191 |
| 6150 | `_sessionTimer` | setTimeout | `(inline)` | 6142, 6190 |
| 6159 | `_countdownTimer` | setInterval | `(inline)` | 6146, 6165, 6192 |

## 🐒 Function ที่ถูกเขียนทับภายหลัง (monkey patch)

> 🔴 **อ่านก่อนแก้:** ตัวประกาศเดิมกับตัวที่ทำงานจริง**คนละตัว** · แก้ที่ `function foo()` เฉยๆ จะไม่มีผลกับ wrapper

| function | ประกาศเดิม | ถูกเขียนทับที่ |
|---|---|---|
| `saveSession` | 2620 | **6183** |
| `doLogout` | 2630 | **6189** |

## 🔌 Backend endpoints ที่ frontend เรียก

`:x` = ส่วนที่เป็นตัวแปร (template literal)

| method | path | เรียกที่บรรทัด |
|---|---|---|
| GET | `/admin/disputes` | 3026 |
| PATCH | `/admin/disputes/:x/resolve` | 3048 |
| PATCH | `/admin/jobs/:x/status` | 3084 |
| PATCH | `/admin/kyc/:x/review` | 3017 |
| GET | `/admin/kyc/pending` | 2980 |
| GET | `/admin/payments` | 3093 |
| POST | `/admin/payments/:x/resolve` | 3137 |
| GET | `/admin/stats` | 2870 |
| PATCH | `/admin/users/:x/status` | 2971 |
| POST | `/applications/:x/accept-backup` | 5257 |
| POST | `/applications/:x/auto-confirm` | 5354 |
| POST | `/applications/:x/checkin` | 5275 |
| POST | `/applications/:x/complete` | 5296 |
| POST | `/applications/:x/confirm-payment` | 5478 |
| GET | `/applications/:x/contact` | 5216, 5334 |
| PATCH | `/applications/:x/decide` | 4744, 4984 |
| POST | `/applications/:x/dispute` | 5376 |
| PATCH | `/applications/:x/mark-noshow` | 4602 |
| FETCH | `/applications/:x/pay` | 5455 |
| POST | `/applications/:x/report-payment` | 5493 |
| POST | `/applications/:x/start` | 5309 |
| POST | `/applications/:x/verify` | 4608, 5322 |
| POST | `/auth/google/callback` | 2565 |
| GET | `/auth/google/url?role=:x` | 2542 |
| POST | `/auth/login` | 2583 |
| GET | `/auth/me` | 2719, 3178, 3416, 3784 |
| PATCH | `/auth/phone` | 2798, 3747 |
| POST | `/auth/register` | 2612 |
| POST | `/employers/profile` | 2795, 4292 |
| PATCH | `/employers/profile` | 2797 |
| GET | `/employers/profile/me` | 2721, 3307, 4247 |
| POST | `/employers/verify/request` | 5522 |
| FETCH | `/employers/workplace-photo` | 2813 |
| GET | `/job-categories` | 5835 |
| GET | `/job-categories/:x/titles` | 5873, 5904 |
| POST | `/jobs` | 4378 |
| POST | `/jobs/:x/apply` | 4109 |
| GET | `/jobs/:x/candidates` | 3312, 4498, 4895 |
| POST | `/jobs/:x/confirm-backup-wage` | 5241 |
| PATCH | `/jobs/:x/status` | 4879, 4886 |
| GET | `/jobs/mine` | 3308, 4488, 4778 |
| GET | `/jobs/nearby?lat=13.7018&lng=100.6011&radius_km=25&scope=all` | 3223 |
| GET | `/jobs/nearby?lat=:x&lng=:x&radius_km=:x&scope=:x` | 4034 |
| PATCH | `/notifications/:x/read` | 5752, 5771 |
| PATCH | `/notifications/read-all` | 5788 |
| GET | `/notifications/unread-count` | 5654 |
| GET | `/notifications:x` | 5692 |
| FETCH | `/public/stats` | 2511 |
| GET | `/review-tags?target_role=:x` | 6069 |
| POST | `/reviews` | 6121 |
| GET | `/reviews/me` | 5976 |
| GET | `/reviews/pending` | 5975 |
| FETCH | `/users/me` | 6396 |
| POST | `/users/report` | 5547 |
| GET | `/workers/applications` | 3176, 4127, 4629 |
| POST | `/workers/background-check/request` | 5509 |
| GET | `/workers/earnings` | 3177, 4829 |
| FETCH | `/workers/kyc/upload` | 2848 |
| POST | `/workers/profile` | 3707 |
| PATCH | `/workers/profile` | 3736, 4751, 4760 |
| GET | `/workers/profile/me` | 3175, 3418, 3783, 4628, 4686 |
| GET | `/zones` | 5846 |

---

_generated by `tools/gen_map.py` · source sha256 `02f1c4ae627a`_
