# INDEX_MAP — แผนที่ `index.html`

> 🤖 **ไฟล์นี้ generate อัตโนมัติ — ห้ามแก้ด้วยมือ**  
> regenerate: `python tools/gen_map.py` · เช็คว่าเก่ายัง: `python tools/gen_map.py --check`  
> ส่วนที่เขียนด้วยมือ (coupling / กับดัก) อยู่ที่ **`COUPLING_MAP.md`** — สคริปต์ไม่แตะไฟล์นั้น

- generated: `2026-07-19 19:44` (BKK)
- source: `index.html` · **6,389 บรรทัด** · sha256 `bbab976b6a96`
- 168 functions · 19 pages · 62 endpoints

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
| 1871–6196 | **JS (ก้อนหลัก)** · 4,325 บรรทัด |
| 6197–6210 | HTML markup |
| 6211–6291 | JS · 80 บรรทัด |
| 6292–6348 | HTML markup |
| 6349–6385 | JS · 36 บรรทัด |
| 6386–6389 | HTML markup |

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
| 3748 | PROFILE COMPLETENESS (gate ก่อนสมัครงาน) |
| 3867 | NEARBY MAP INIT |
| 4001 | NEARBY JOBS |
| 4114 | MY APPLICATIONS |
| 4234 | EMPLOYER PROFILE CHECK |
| 4296 | POST JOB |
| 4430 | LIVE ROSTER |
| 4604 | ACTIVE SHIFT (worker — กระจกสะท้อน Roster) |
| 4671 | SETTINGS (role-aware) |
| 4756 | MY JOBS |
| 5006 | GOOGLE MAPS |
| 5129 | POST-JOB: inherit ที่อยู่หน้างานจากโปรไฟล์บริษัท |
| 5227 | JOB LIFECYCLE |
| 5379 | PAYMENT PROOF |
| 5495 | TRUST & SAFETY |
| 5551 | NOTIFICATIONS |
| 5796 | REVIEW SUMMARY |
| 5820 | JOB CATEGORIES CASCADE |
| 5875 | SKILLS แบบหลายตำแหน่ง (สูงสุด 3) |
| 5941 | REVIEWS |
| 5954 | Pending reviews |
| 6003 | Received reviews |
| 6103 | SESSION TIMEOUT |
| 6173 | START |

## 📄 หน้า (page) → ตัวโหลด → mount point

`showPage(key)` คือ router · มันซ่อน `.page` ทุกตัวแล้วโชว์ `#page-<key>` จากนั้นเรียก loader ตามตาราง

| page id | บรรทัด | key ที่ส่งให้ showPage | loader | mount point (JS เขียน innerHTML ลงตรงนี้) |
|---|---|---|---|---|
| `page-dashboard` | 1462–1472 | `dashboard` | — | `#dashContent` `#dashHeader` `#dashStats` |
| `page-nearby` | 1473–1516 | `nearby` | `initNearbyMap()` @3921 | `#nearbyResults` `#searchMapPreview` |
| `page-myapps` | 1517–1525 | `myapps` | `loadMyApps()` @4115 | `#myAppsContent` |
| `page-workerprofile` | 1526–1535 | `workerprofile` | `loadWorkerProfile()` @3411 | `#alertWorkerProfile` `#workerProfileContent` |
| `page-postjob` | 1536–1652 | `postjob` | `checkEmployerProfile()` @4235 | `#alertPostJob` `#employerProfileCheck` `#jobHoursSummary` `#jobProfileMapPreview` |
| `page-myjobs` | 1653–1661 | `myjobs` | `loadMyJobs()` @4766 | `#myJobsContent` |
| `page-roster` | 1662–1670 | `roster` | `loadRoster()` @4474 | `#rosterContent` |
| `page-employerprofile` | 1671–1679 | `employerprofile` | `loadEmployerProfile()` @2715 | `#employerProfileContent` |
| `page-activeshift` | 1680–1686 | `activeshift` | `loadActiveShift()` @4614 | `#activeShiftContent` |
| `page-settings` | 1687–1694 | `settings` | `loadSettings()` @4672 | `#settingsContent` |
| `page-admin-stats` | 1695–1703 | `admin-stats` | `loadAdminStats()` @2866 | `#adminStatsContent` |
| `page-admin-users` | 1704–1717 | `admin-users` | `loadAdminUsers()` @2944 | `#adminUsersContent` |
| `page-admin-kyc` | 1718–1726 | `admin-kyc` | `loadAdminKYC()` @2976 | `#adminKYCContent` |
| `page-admin-disputes` | 1727–1735 | `admin-disputes` | `loadAdminDisputes()` @3022 | `#adminDisputesContent` |
| `page-admin-jobs` | 1736–1749 | `admin-jobs` | `loadAdminJobs()` @3053 | `#adminJobsContent` |
| `page-admin-payments` | 1750–1758 | `admin-payments` | `loadAdminPayments()` @3089 | `#adminPaymentsContent` |
| `page-notifications` | 1759–1777 | `notifications` | `setNotifFilter()` @5665 | `#notificationsContent` |
| `page-earnings` | 1778–1785 | `earnings` | — | `#earningsContent` |
| `page-myreviews` | 1786–1870 | `myreviews` | `loadMyReviews()` @5943 | `#alertPay` `#alertReport` `#debugLogs` `#myReviewsContent` |

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
| 3411–3682 | async `loadWorkerProfile()` |
| 3683–3688 | `showEditProfile()` |
| 3689–3717 | async `doCreateProfile()` |
| 3718–3762 | async `doUpdateProfile()` |

### PROFILE COMPLETENESS (gate ก่อนสมัครงาน)

| บรรทัด | function |
|---|---|
| 3763–3772 | `setPendingApply(v)` |
| 3773–3783 | async `fetchWorkerStatus()` |
| 3784–3812 | `workerChecklist(profile, phone)` |
| 3813–3842 | `showProfileGateModal(items)` |
| 3843–3850 | `goCompleteProfile()` |
| 3851–3875 | async `returnToPendingApply(alertId)` |

### NEARBY MAP INIT

| บรรทัด | function |
|---|---|
| 3876–3883 | `sizeNearby()` |
| 3884–3890 | `_onNearbyResize()` |
| 3891–3899 | `setNearbyScope(scope)` |
| 3900–3920 | `_nbPill(lat, lng, label, active, onClick)` |
| 3921–3925 | `initNearbyMap()` |
| 3926–3972 | `buildMap(lat, lng)` |
| 3973–3986 | `onGeoOk(pos)` |
| 3987–4013 | `onGeoFail()` |

### NEARBY JOBS

| บรรทัด | function |
|---|---|
| 4014–4081 | async `searchNearby()` |
| 4082–4114 | async `applyJob(jobId, lat, lng, btn)` |

### MY APPLICATIONS

| บรรทัด | function |
|---|---|
| 4115–4234 | async `loadMyApps()` |

### EMPLOYER PROFILE CHECK

| บรรทัด | function |
|---|---|
| 4235–4281 | async `checkEmployerProfile()` |
| 4282–4296 | async `doCreateEmployerProfile()` |

### POST JOB

| บรรทัด | function |
|---|---|
| 4297–4304 | `calcWorkHours(start, end)` |
| 4305–4324 | `updateHoursSummary()` |
| 4325–4329 | `toggleJobOT()` |
| 4330–4383 | async `doPostJob()` |
| 4384–4432 | `ico(n, sz)` |

### LIVE ROSTER

| บรรทัด | function |
|---|---|
| 4433–4433 | `_elapsedSec(iso)` |
| 4434–4435 | `_hhmmss(s)` |
| 4436–4439 | `stopRosterPolling()` |
| 4440–4444 | `_fmtHM(iso)` |
| 4445–4451 | `_shiftSeconds(ws, we)` |
| 4452–4459 | `_minutesLate(ws)` |
| 4460–4462 | `_rosterRank(kind)` |
| 4463–4473 | `_rosterKind(c)` |
| 4474–4512 | async `loadRoster()` |
| 4513–4578 | `renderRosterRow(r)` |
| 4579–4590 | `tickRosterTimers()` |
| 4591–4597 | async `markNoShow(appId, btn)` |
| 4598–4605 | async `rosterVerifyPay(appId, jobId, jobTitle, amount, btn)` |

### ACTIVE SHIFT (worker — กระจกสะท้อน Roster)

| บรรทัด | function |
|---|---|
| 4606–4606 | `stopActiveShiftTimer()` |
| 4607–4613 | `tickActiveShiftTimers()` |
| 4614–4643 | async `loadActiveShift()` |
| 4644–4671 | `renderShiftCard(a)` |

### SETTINGS (role-aware)

| บรรทัด | function |
|---|---|
| 4672–4722 | async `loadSettings()` |
| 4723–4724 | `toggleLangSetting()` |
| 4725–4733 | `toggleAppTheme()` |
| 4734–4739 | async `dashHire(appId, btn)` |
| 4740–4750 | async `toggleAvailable(elm)` |
| 4751–4756 | async `toggleAvailInput(el)` |

### MY JOBS

| บรรทัด | function |
|---|---|
| 4757–4765 | `autoCloseCountdown(autoCloseAt)` |
| 4766–4816 | async `loadMyJobs()` |
| 4817–4867 | async `loadEarnings()` |
| 4868–4875 | async `closeJob(jobId)` |
| 4876–4882 | async `reopenJob(jobId)` |
| 4883–4971 | async `loadCandidates(jobId, jobTitle, jobWage)` |
| 4972–5008 | async `decide(appId, decision, btn)` |

### GOOGLE MAPS

| บรรทัด | function |
|---|---|
| 5009–5036 | `initPlacesAutocomplete(inputId, latId, lngId, displayId, mapPreviewId)` |
| 5037–5051 | `updatePinLocation(lat, lng, latId, lngId, displayId, inputId)` |
| 5052–5096 | `showMapPreview(containerId, lat, lng, label, latId, lngId, displayId, inputId)` |
| 5097–5127 | `setLocationFromGPS(latId, lngId, displayId, mapPreviewId, inputId)` |
| 5128–5129 | `useMyLocation()` |

### POST-JOB: inherit ที่อยู่หน้างานจากโปรไฟล์บริษัท

| บรรทัด | function |
|---|---|
| 5130–5154 | `applyProfileLocationToPostJob(emp)` |
| 5155–5162 | `toggleProfileLocation(cb)` |
| 5163–5189 | `showStaticMap(containerId, lat, lng, label)` |
| 5190–5196 | `initAllAutocompletes()` |
| 5197–5228 | async `showContact(appId, btn)` |

### JOB LIFECYCLE

| บรรทัด | function |
|---|---|
| 5229–5244 | async `doConfirmBackupWage(jobId, amount, btn)` |
| 5245–5261 | async `doAcceptBackup(appId, btn)` |
| 5262–5283 | async `doCheckin(appId, btn)` |
| 5284–5296 | async `doComplete(appId, btn)` |
| 5297–5309 | async `doStart(appId, btn)` |
| 5310–5322 | async `doVerify(appId, btn)` |
| 5323–5341 | async `showEmployerContact(appId, btn)` |
| 5342–5361 | async `toggleAutoConfirm(appId, btn)` |
| 5362–5380 | async `doDispute(appId, btn)` |

### PAYMENT PROOF

| บรรทัด | function |
|---|---|
| 5381–5385 | `payMethodChanged()` |
| 5386–5415 | `openPayModal(appId, jobId, jobTitle, amount)` |
| 5416–5419 | `closePayModal()` |
| 5420–5464 | async `doPaySubmit()` |
| 5465–5479 | async `doConfirmPayment(appId, btn)` |
| 5480–5496 | async `doReportPayment(appId, btn)` |

### TRUST & SAFETY

| บรรทัด | function |
|---|---|
| 5497–5509 | async `requestBackgroundCheck(btn)` |
| 5510–5522 | async `requestEmployerVerify(btn)` |
| 5523–5529 | `showReportModal(targetUserId)` |
| 5530–5533 | `closeReportModal()` |
| 5534–5568 | async `submitReport()` |

### NOTIFICATIONS

| บรรทัด | function |
|---|---|
| 5569–5596 | `_notifLabelMap(type)` |
| 5597–5627 | `_notifTranslateTitle(title)` |
| 5628–5638 | `_notifDateLabel(dateStr)` |
| 5639–5643 | async `startNotifPolling()` |
| 5644–5664 | async `refreshNotifBadge()` |
| 5665–5678 | `setNotifFilter(filter)` |
| 5679–5741 | async `loadNotifications()` |
| 5742–5757 | async `markNotifRead(notifId, btn)` |
| 5758–5775 | async `notifOpen(notifId, type, cardEl)` |
| 5776–5797 | async `markAllRead()` |

### REVIEW SUMMARY

| บรรทัด | function |
|---|---|
| 5798–5823 | async `loadReviewSummary(userIdForReview, role, containerId)` |

### JOB CATEGORIES CASCADE

| บรรทัด | function |
|---|---|
| 5824–5834 | async `loadCategories()` |
| 5835–5854 | async `initCategoryDropdowns()` |
| 5855–5886 | async `loadJobTitles(categorySelectId, titleSelectId)` |

### SKILLS แบบหลายตำแหน่ง (สูงสุด 3)

| บรรทัด | function |
|---|---|
| 5887–5891 | `getSkillList(hiddenInputId)` |
| 5892–5911 | `renderSkillChips(hiddenInputId, containerId, selectId)` |
| 5912–5931 | `syncSkillCode(titleSelectId, hiddenInputId, containerId)` |
| 5932–5942 | `removeSkill(code, hiddenInputId, containerId, selectId)` |

### REVIEWS

| บรรทัด | function |
|---|---|
| 5943–6039 | async `loadMyReviews()` |

### Received reviews

| บรรทัด | function |
|---|---|
| 6040–6053 | async `loadTagsForReview(appId, targetRole)` |
| 6054–6061 | `setStar(appId, val)` |
| 6062–6065 | `toggleTag(appId, tagKey, el)` |
| 6066–6071 | `setRehire(appId, val, btn)` |
| 6072–6111 | async `submitReview(appId, targetRole)` |

### SESSION TIMEOUT

| บรรทัด | function |
|---|---|
| 6112–6128 | `_resetSessionTimers()` |
| 6129–6141 | `_showSessionWarning()` |
| 6142–6235 | `extendSession()` |

### START

| บรรทัด | function |
|---|---|
| 6236–6239 | `openPolicyModal(tab)` |
| 6240–6242 | `closePolicyModal()` |
| 6243–6250 | `switchPolicyTab(tab)` |
| 6251–6286 | `showOnboardModal(role)` |
| 6287–6349 | `closeOnboardModal()` |
| 6350–6355 | `openDeleteAccountModal()` |
| 6356–6363 | `closeDeleteAccountModal()` |
| 6364 | async `doDeleteAccount()` |

## 🌐 Global state

> ตัวแปรพวกนี้อยู่นอก function = ทุกหน้าใช้ร่วมกัน · **แก้ function ที่เขียนตัวไหน ต้องไล่ดูทุกตัวที่อ่านมันด้วย**

| บรรทัด | ตัวแปร | ค่าเริ่มต้น | ถูกอ้างถึง (บรรทัด) |
|---|---|---|---|
| 2329 | `_lang` | `localStorage.getItem('wh_lang') || 'th'` | 2329, 2330, 2332, 2680, 3981, 4167, 4676, 4723, 4776, 5598, 5635, 5706 …(+4) |
| 2378 | `token` | `localStorage.getItem('wh_token') || ''` | 39, 40, 41, 42, 295, 2346, 2378, 2411, 2411, 2562, 2621, 2624 …(+12) |
| 2379 | `userRole` | `localStorage.getItem('wh_role') || ''` | 2379, 2622, 2625, 2627, 2633, 2654, 2654, 2656, 2657, 2658, 3158, 3168 …(+7) |
| 2380 | `userId` | `localStorage.getItem('wh_uid') || ''` | 2380, 2623, 2626, 2633, 2968, 2971, 3606, 6181 |
| 2381 | `callCount` | `0` | 2381, 2456, 2457 |
| 2382 | `debugOpen` | `false` | 2382, 2395, 2396, 2403, 2403, 2404, 2405 |
| 2718 | `myPhone` | `''` | 2718, 2719, 2751, 3415, 3416, 3560, 3633 |
| 2720 | `p` | `null` | 85, 95, 175, 480, 546, 556, 664, 757, 823, 833, 931, 931 …(+246) |
| 3415 | `myPhone` | `''` | 2718, 2719, 2751, 3415, 3416, 3560, 3633 |
| 3758 | `_pendingApplyJobId` | `(() => {` | 3753, 3758, 3764, 3852 |
| 3786 | `permitOk` | `true` | 3786, 3790, 3798 |
| 3868 | `_nearbyMap` | `null` | 3868, 3882, 3882, 3930, 3931, 3948, 3954, 3958, 4040, 4047, 4047, 4049 |
| 3869 | `_nearbyCircle` | `null` | 3869, 3952, 3952, 3957, 3964, 3964 |
| 3870 | `_nearbyMarker` | `null` | 3870, 3951, 3951, 3953 |
| 3871 | `_jobMarkers` | `[]` | 3871, 4029, 4030, 4050 |
| 3872 | `_nearbyScope` | `'related'` | 3872, 3892, 3894, 3895, 4026 |
| 4300 | `startMin` | `sh * 60 + sm, endMin = eh * 60 + em` | 4300, 4301, 4302 |
| 4431 | `_rosterPoll` | `null, _rosterTick = null, _rosterSig = n…` | 4431, 4437, 4437, 4437, 4477, 4509, 4509 |
| 4448 | `s` | `((h2*60+m2) - (h1*60+m1)) * 60` | 1255, 1255, 2215, 3157, 3158, 3160, 3436, 3436, 3438, 3438, 3462, 3463 …(+48) |
| 4456 | `late` | `(now.getHours()*60 + now.getMinutes()) -…` | 4456, 4457, 4457, 4457, 4457, 4458 |
| 4605 | `_asTick` | `null` | 4605, 4606, 4606, 4606, 4640 |
| 4677 | `availOn` | `true` | 4677, 4678, 4692, 4692, 4692 |
| 4694 | `h` | `''` | 2410, 2411, 2412, 4455, 4456, 4694, 4695, 4700, 4705, 4709, 4712, 4716 …(+2) |
| 5007 | `autocompletes` | `{}` | 5007, 5033 |
| 5553 | `_notifTimer` | `null` | 5553, 5641 |
| 5554 | `_notifFilter` | `'all'` | 2705, 5554, 5666, 5683, 5687 |
| 5822 | `_categoriesCache` | `null` | 5822, 5825, 5825, 5827, 5828 |
| 6108 | `_sessionTimer` | `null` | 6108, 6115, 6123, 6163 |
| 6109 | `_sessionWarnTimer` | `null` | 6109, 6116, 6121, 6164 |
| 6110 | `_countdownTimer` | `null` | 6110, 6119, 6132, 6138, 6165 |
| 6131 | `remaining` | `SESSION_WARN_MS / 1000` | 6131, 6133, 6134, 6135, 6138 |

## ⏱️ Timer / Polling

| ตั้งที่บรรทัด | handle | ชนิด | เรียก | เคลียร์ที่บรรทัด |
|---|---|---|---|---|
| 4509 | `_rosterPoll` | setInterval | `loadRoster` | 4437 |
| 4510 | `_rosterTick` | setInterval | `tickRosterTimers` | 4438 |
| 4640 | `_asTick` | setInterval | `tickActiveShiftTimers` | 4606 |
| 5641 | `_notifTimer` | setInterval | `refreshNotifBadge` | **⚠️ ไม่เคยเคลียร์** |
| 6121 | `_sessionWarnTimer` | setTimeout | `_showSessionWarning` | 6116, 6164 |
| 6123 | `_sessionTimer` | setTimeout | `(inline)` | 6115, 6163 |
| 6132 | `_countdownTimer` | setInterval | `(inline)` | 6119, 6138, 6165 |

## 🐒 Function ที่ถูกเขียนทับภายหลัง (monkey patch)

> 🔴 **อ่านก่อนแก้:** ตัวประกาศเดิมกับตัวที่ทำงานจริง**คนละตัว** · แก้ที่ `function foo()` เฉยๆ จะไม่มีผลกับ wrapper

| function | ประกาศเดิม | ถูกเขียนทับที่ |
|---|---|---|
| `saveSession` | 2620 | **6156** |
| `doLogout` | 2630 | **6162** |

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
| POST | `/applications/:x/accept-backup` | 5249 |
| POST | `/applications/:x/auto-confirm` | 5346 |
| POST | `/applications/:x/checkin` | 5267 |
| POST | `/applications/:x/complete` | 5288 |
| POST | `/applications/:x/confirm-payment` | 5470 |
| GET | `/applications/:x/contact` | 5208, 5326 |
| PATCH | `/applications/:x/decide` | 4736, 4976 |
| POST | `/applications/:x/dispute` | 5368 |
| PATCH | `/applications/:x/mark-noshow` | 4594 |
| FETCH | `/applications/:x/pay` | 5447 |
| POST | `/applications/:x/report-payment` | 5485 |
| POST | `/applications/:x/start` | 5301 |
| POST | `/applications/:x/verify` | 4600, 5314 |
| POST | `/auth/google/callback` | 2565 |
| GET | `/auth/google/url?role=:x` | 2542 |
| POST | `/auth/login` | 2583 |
| GET | `/auth/me` | 2719, 3178, 3416, 3776 |
| PATCH | `/auth/phone` | 2798, 3739 |
| POST | `/auth/register` | 2612 |
| POST | `/employers/profile` | 2795, 4284 |
| PATCH | `/employers/profile` | 2797 |
| GET | `/employers/profile/me` | 2721, 3307, 4239 |
| POST | `/employers/verify/request` | 5514 |
| FETCH | `/employers/workplace-photo` | 2813 |
| GET | `/job-categories` | 5827 |
| GET | `/job-categories/:x/titles` | 5865 |
| POST | `/jobs` | 4370 |
| POST | `/jobs/:x/apply` | 4101 |
| GET | `/jobs/:x/candidates` | 3312, 4490, 4887 |
| POST | `/jobs/:x/confirm-backup-wage` | 5233 |
| PATCH | `/jobs/:x/status` | 4871, 4878 |
| GET | `/jobs/mine` | 3308, 4480, 4770 |
| GET | `/jobs/nearby?lat=13.7018&lng=100.6011&radius_km=25&scope=all` | 3223 |
| GET | `/jobs/nearby?lat=:x&lng=:x&radius_km=:x&scope=:x` | 4026 |
| PATCH | `/notifications/:x/read` | 5744, 5763 |
| PATCH | `/notifications/read-all` | 5780 |
| GET | `/notifications/unread-count` | 5646 |
| GET | `/notifications:x` | 5684 |
| FETCH | `/public/stats` | 2511 |
| GET | `/review-tags?target_role=:x` | 6042 |
| POST | `/reviews` | 6094 |
| GET | `/reviews/me` | 5949 |
| GET | `/reviews/pending` | 5948 |
| FETCH | `/users/me` | 6369 |
| POST | `/users/report` | 5539 |
| GET | `/workers/applications` | 3176, 4119, 4621 |
| POST | `/workers/background-check/request` | 5501 |
| GET | `/workers/earnings` | 3177, 4821 |
| FETCH | `/workers/kyc/upload` | 2848 |
| POST | `/workers/profile` | 3699 |
| PATCH | `/workers/profile` | 3728, 4743, 4752 |
| GET | `/workers/profile/me` | 3175, 3418, 3775, 4620, 4678 |
| GET | `/zones` | 5838 |

---

_generated by `tools/gen_map.py` · source sha256 `bbab976b6a96`_
