# INDEX_MAP — แผนที่ `index.html`

> 🤖 **ไฟล์นี้ generate อัตโนมัติ — ห้ามแก้ด้วยมือ**  
> regenerate: `python tools/gen_map.py` · เช็คว่าเก่ายัง: `python tools/gen_map.py --check`  
> ส่วนที่เขียนด้วยมือ (coupling / กับดัก) อยู่ที่ **`COUPLING_MAP.md`** — สคริปต์ไม่แตะไฟล์นั้น

- generated: `2026-07-19 15:09` (BKK)
- source: `index.html` · **6,085 บรรทัด** · sha256 `3a84f52cf83e`
- 158 functions · 19 pages · 62 endpoints

---

## 🗺️ Layout ของไฟล์

| ช่วงบรรทัด | คืออะไร |
|---|---|
| 1–7 | HTML markup |
| 8–8 | JS · 0 บรรทัด |
| 9–9 | HTML markup |
| 10–10 | JS `src="https://maps.googleapis.com/maps/api/js?key=AIzaSyD73zN` · 0 บรรทัด |
| 11–627 | CSS · 616 บรรทัด |
| 628–629 | HTML markup |
| 630–667 | CSS · 37 บรรทัด |
| 668–670 | HTML markup |
| 671–907 | CSS · 236 บรรทัด |
| 908–1866 | HTML markup |
| 1867–5892 | **JS (ก้อนหลัก)** · 4,025 บรรทัด |
| 5893–5906 | HTML markup |
| 5907–5987 | JS · 80 บรรทัด |
| 5988–6044 | HTML markup |
| 6045–6081 | JS · 36 บรรทัด |
| 6082–6085 | HTML markup |

## 📑 Section ใน JS

| บรรทัด | Section |
|---|---|
| 1868 | MULTILANG |
| 2355 | THEME (login page) |
| 2372 | CONSTANTS |
| 2380 | DEBUG |
| 2404 | API |
| 2445 | HTML ESCAPE — ใช้ทุกจุดที่ render user input ใน innerHTML |
| 2456 | LANDING |
| 2476 | AUTH |
| 2600 | INIT |
| 2635 | NAV |
| 2666 | EMPLOYER PROFILE (company + workplace location) |
| 2777 | KYC UPLOAD |
| 2817 | ADMIN DASHBOARD |
| 3094 | SIDEBAR TOGGLE (mobile) |
| 3107 | DASHBOARD |
| 3311 | WORKER PROFILE |
| 3641 | NEARBY MAP INIT |
| 3775 | NEARBY JOBS |
| 3872 | MY APPLICATIONS |
| 3992 | EMPLOYER PROFILE CHECK |
| 4054 | POST JOB |
| 4188 | LIVE ROSTER |
| 4362 | ACTIVE SHIFT (worker — กระจกสะท้อน Roster) |
| 4429 | SETTINGS (role-aware) |
| 4514 | MY JOBS |
| 4764 | GOOGLE MAPS |
| 4887 | POST-JOB: inherit ที่อยู่หน้างานจากโปรไฟล์บริษัท |
| 4985 | JOB LIFECYCLE |
| 5137 | PAYMENT PROOF |
| 5253 | TRUST & SAFETY |
| 5309 | NOTIFICATIONS |
| 5554 | REVIEW SUMMARY |
| 5578 | JOB CATEGORIES CASCADE |
| 5637 | REVIEWS |
| 5650 | Pending reviews |
| 5699 | Received reviews |
| 5799 | SESSION TIMEOUT |
| 5869 | START |

## 📄 หน้า (page) → ตัวโหลด → mount point

`showPage(key)` คือ router · มันซ่อน `.page` ทุกตัวแล้วโชว์ `#page-<key>` จากนั้นเรียก loader ตามตาราง

| page id | บรรทัด | key ที่ส่งให้ showPage | loader | mount point (JS เขียน innerHTML ลงตรงนี้) |
|---|---|---|---|---|
| `page-dashboard` | 1458–1468 | `dashboard` | — | `#dashContent` `#dashHeader` `#dashStats` |
| `page-nearby` | 1469–1512 | `nearby` | `initNearbyMap()` @3695 | `#nearbyResults` `#searchMapPreview` |
| `page-myapps` | 1513–1521 | `myapps` | `loadMyApps()` @3873 | `#myAppsContent` |
| `page-workerprofile` | 1522–1531 | `workerprofile` | `loadWorkerProfile()` @3312 | `#alertWorkerProfile` `#workerProfileContent` |
| `page-postjob` | 1532–1648 | `postjob` | `checkEmployerProfile()` @3993 | `#alertPostJob` `#employerProfileCheck` `#jobHoursSummary` `#jobProfileMapPreview` |
| `page-myjobs` | 1649–1657 | `myjobs` | `loadMyJobs()` @4524 | `#myJobsContent` |
| `page-roster` | 1658–1666 | `roster` | `loadRoster()` @4232 | `#rosterContent` |
| `page-employerprofile` | 1667–1675 | `employerprofile` | `loadEmployerProfile()` @2667 | `#employerProfileContent` |
| `page-activeshift` | 1676–1682 | `activeshift` | `loadActiveShift()` @4372 | `#activeShiftContent` |
| `page-settings` | 1683–1690 | `settings` | `loadSettings()` @4430 | `#settingsContent` |
| `page-admin-stats` | 1691–1699 | `admin-stats` | `loadAdminStats()` @2818 | `#adminStatsContent` |
| `page-admin-users` | 1700–1713 | `admin-users` | `loadAdminUsers()` @2896 | `#adminUsersContent` |
| `page-admin-kyc` | 1714–1722 | `admin-kyc` | `loadAdminKYC()` @2928 | `#adminKYCContent` |
| `page-admin-disputes` | 1723–1731 | `admin-disputes` | `loadAdminDisputes()` @2974 | `#adminDisputesContent` |
| `page-admin-jobs` | 1732–1745 | `admin-jobs` | `loadAdminJobs()` @3005 | `#adminJobsContent` |
| `page-admin-payments` | 1746–1754 | `admin-payments` | `loadAdminPayments()` @3041 | `#adminPaymentsContent` |
| `page-notifications` | 1755–1773 | `notifications` | `setNotifFilter()` @5423 | `#notificationsContent` |
| `page-earnings` | 1774–1781 | `earnings` | — | `#earningsContent` |
| `page-myreviews` | 1782–1866 | `myreviews` | `loadMyReviews()` @5639 | `#alertPay` `#alertReport` `#debugLogs` `#myReviewsContent` |

## 🔧 Functions

### MULTILANG

| บรรทัด | function |
|---|---|
| 2326–2326 | `t(key)` |
| 2327–2355 | `setLang(lang)` |

### THEME (login page)

| บรรทัด | function |
|---|---|
| 2356–2363 | `renderAuthThemeIcon()` |
| 2364–2380 | `toggleAuthTheme()` |

### DEBUG

| บรรทัด | function |
|---|---|
| 2381–2397 | `log(type, msg)` |
| 2398–2404 | `toggleDebug()` |

### API

| บรรทัด | function |
|---|---|
| 2405–2410 | `headers()` |
| 2411–2437 | async `api(method, path, body)` |
| 2438–2445 | `showAlert(id, msg, type='error')` |

### HTML ESCAPE — ใช้ทุกจุดที่ render user input ใน innerHTML

| บรรทัด | function |
|---|---|
| 2446–2456 | `esc(str)` |

### LANDING

| บรรทัด | function |
|---|---|
| 2457–2461 | `showAuthFromLanding()` |
| 2462–2476 | async `loadLandingStats()` |

### AUTH

| บรรทัด | function |
|---|---|
| 2477–2483 | `switchAuthTab(tab)` |
| 2484–2492 | `selectRole(role, el)` |
| 2493–2501 | async `doGoogleLogin(role)` |
| 2502–2530 | async `handleGoogleCallback()` |
| 2531–2548 | async `doLogin()` |
| 2549–2572 | async `doRegister()` |
| 2573–2582 | `saveSession(data)` |
| 2583–2590 | `doLogout()` |
| 2591–2600 | `copyToken()` |

### INIT

| บรรทัด | function |
|---|---|
| 2601–2635 | `initApp()` |

### NAV

| บรรทัด | function |
|---|---|
| 2636–2666 | `showPage(name)` |

### EMPLOYER PROFILE (company + workplace location)

| บรรทัด | function |
|---|---|
| 2667–2726 | async `loadEmployerProfile()` |
| 2727–2756 | async `doSaveEmployerProfile(isNew)` |
| 2757–2777 | async `uploadEmpPhoto(input)` |

### KYC UPLOAD

| บรรทัด | function |
|---|---|
| 2778–2785 | `previewKYCImg(input, previewId)` |
| 2786–2817 | async `submitKYC()` |

### ADMIN DASHBOARD

| บรรทัด | function |
|---|---|
| 2818–2895 | async `loadAdminStats()` |
| 2896–2919 | async `loadAdminUsers(role=null, status=null, page=1)` |
| 2920–2927 | async `adminUpdateUserStatus(userId, status)` |
| 2928–2964 | async `loadAdminKYC()` |
| 2965–2973 | async `adminKYCReview(workerId, decision)` |
| 2974–2995 | async `loadAdminDisputes()` |
| 2996–3004 | async `adminResolveDispute(disputeId, decision)` |
| 3005–3033 | async `loadAdminJobs(status=null, page=1)` |
| 3034–3040 | async `adminUpdateJobStatus(jobId, status)` |
| 3041–3084 | async `loadAdminPayments()` |
| 3085–3094 | async `adminResolvePayment(appId)` |

### SIDEBAR TOGGLE (mobile)

| บรรทัด | function |
|---|---|
| 3095–3098 | `openSidebar()` |
| 3099–3102 | `closeSidebar()` |
| 3103–3107 | `toggleSidebar()` |

### DASHBOARD

| บรรทัด | function |
|---|---|
| 3108–3114 | `dashInitials(name)` |
| 3115–3311 | async `loadDashboard()` |

### WORKER PROFILE

| บรรทัด | function |
|---|---|
| 3312–3579 | async `loadWorkerProfile()` |
| 3580–3585 | `showEditProfile()` |
| 3586–3612 | async `doCreateProfile()` |
| 3613–3649 | async `doUpdateProfile()` |

### NEARBY MAP INIT

| บรรทัด | function |
|---|---|
| 3650–3657 | `sizeNearby()` |
| 3658–3664 | `_onNearbyResize()` |
| 3665–3673 | `setNearbyScope(scope)` |
| 3674–3694 | `_nbPill(lat, lng, label, active, onClick)` |
| 3695–3699 | `initNearbyMap()` |
| 3700–3746 | `buildMap(lat, lng)` |
| 3747–3760 | `onGeoOk(pos)` |
| 3761–3787 | `onGeoFail()` |

### NEARBY JOBS

| บรรทัด | function |
|---|---|
| 3788–3855 | async `searchNearby()` |
| 3856–3872 | async `applyJob(jobId, lat, lng, btn)` |

### MY APPLICATIONS

| บรรทัด | function |
|---|---|
| 3873–3992 | async `loadMyApps()` |

### EMPLOYER PROFILE CHECK

| บรรทัด | function |
|---|---|
| 3993–4039 | async `checkEmployerProfile()` |
| 4040–4054 | async `doCreateEmployerProfile()` |

### POST JOB

| บรรทัด | function |
|---|---|
| 4055–4062 | `calcWorkHours(start, end)` |
| 4063–4082 | `updateHoursSummary()` |
| 4083–4087 | `toggleJobOT()` |
| 4088–4141 | async `doPostJob()` |
| 4142–4190 | `ico(n, sz)` |

### LIVE ROSTER

| บรรทัด | function |
|---|---|
| 4191–4191 | `_elapsedSec(iso)` |
| 4192–4193 | `_hhmmss(s)` |
| 4194–4197 | `stopRosterPolling()` |
| 4198–4202 | `_fmtHM(iso)` |
| 4203–4209 | `_shiftSeconds(ws, we)` |
| 4210–4217 | `_minutesLate(ws)` |
| 4218–4220 | `_rosterRank(kind)` |
| 4221–4231 | `_rosterKind(c)` |
| 4232–4270 | async `loadRoster()` |
| 4271–4336 | `renderRosterRow(r)` |
| 4337–4348 | `tickRosterTimers()` |
| 4349–4355 | async `markNoShow(appId, btn)` |
| 4356–4363 | async `rosterVerifyPay(appId, jobId, jobTitle, amount, btn)` |

### ACTIVE SHIFT (worker — กระจกสะท้อน Roster)

| บรรทัด | function |
|---|---|
| 4364–4364 | `stopActiveShiftTimer()` |
| 4365–4371 | `tickActiveShiftTimers()` |
| 4372–4401 | async `loadActiveShift()` |
| 4402–4429 | `renderShiftCard(a)` |

### SETTINGS (role-aware)

| บรรทัด | function |
|---|---|
| 4430–4480 | async `loadSettings()` |
| 4481–4482 | `toggleLangSetting()` |
| 4483–4491 | `toggleAppTheme()` |
| 4492–4497 | async `dashHire(appId, btn)` |
| 4498–4508 | async `toggleAvailable(elm)` |
| 4509–4514 | async `toggleAvailInput(el)` |

### MY JOBS

| บรรทัด | function |
|---|---|
| 4515–4523 | `autoCloseCountdown(autoCloseAt)` |
| 4524–4574 | async `loadMyJobs()` |
| 4575–4625 | async `loadEarnings()` |
| 4626–4633 | async `closeJob(jobId)` |
| 4634–4640 | async `reopenJob(jobId)` |
| 4641–4729 | async `loadCandidates(jobId, jobTitle, jobWage)` |
| 4730–4766 | async `decide(appId, decision, btn)` |

### GOOGLE MAPS

| บรรทัด | function |
|---|---|
| 4767–4794 | `initPlacesAutocomplete(inputId, latId, lngId, displayId, mapPreviewId)` |
| 4795–4809 | `updatePinLocation(lat, lng, latId, lngId, displayId, inputId)` |
| 4810–4854 | `showMapPreview(containerId, lat, lng, label, latId, lngId, displayId, inputId)` |
| 4855–4885 | `setLocationFromGPS(latId, lngId, displayId, mapPreviewId, inputId)` |
| 4886–4887 | `useMyLocation()` |

### POST-JOB: inherit ที่อยู่หน้างานจากโปรไฟล์บริษัท

| บรรทัด | function |
|---|---|
| 4888–4912 | `applyProfileLocationToPostJob(emp)` |
| 4913–4920 | `toggleProfileLocation(cb)` |
| 4921–4947 | `showStaticMap(containerId, lat, lng, label)` |
| 4948–4954 | `initAllAutocompletes()` |
| 4955–4986 | async `showContact(appId, btn)` |

### JOB LIFECYCLE

| บรรทัด | function |
|---|---|
| 4987–5002 | async `doConfirmBackupWage(jobId, amount, btn)` |
| 5003–5019 | async `doAcceptBackup(appId, btn)` |
| 5020–5041 | async `doCheckin(appId, btn)` |
| 5042–5054 | async `doComplete(appId, btn)` |
| 5055–5067 | async `doStart(appId, btn)` |
| 5068–5080 | async `doVerify(appId, btn)` |
| 5081–5099 | async `showEmployerContact(appId, btn)` |
| 5100–5119 | async `toggleAutoConfirm(appId, btn)` |
| 5120–5138 | async `doDispute(appId, btn)` |

### PAYMENT PROOF

| บรรทัด | function |
|---|---|
| 5139–5143 | `payMethodChanged()` |
| 5144–5173 | `openPayModal(appId, jobId, jobTitle, amount)` |
| 5174–5177 | `closePayModal()` |
| 5178–5222 | async `doPaySubmit()` |
| 5223–5237 | async `doConfirmPayment(appId, btn)` |
| 5238–5254 | async `doReportPayment(appId, btn)` |

### TRUST & SAFETY

| บรรทัด | function |
|---|---|
| 5255–5267 | async `requestBackgroundCheck(btn)` |
| 5268–5280 | async `requestEmployerVerify(btn)` |
| 5281–5287 | `showReportModal(targetUserId)` |
| 5288–5291 | `closeReportModal()` |
| 5292–5326 | async `submitReport()` |

### NOTIFICATIONS

| บรรทัด | function |
|---|---|
| 5327–5354 | `_notifLabelMap(type)` |
| 5355–5385 | `_notifTranslateTitle(title)` |
| 5386–5396 | `_notifDateLabel(dateStr)` |
| 5397–5401 | async `startNotifPolling()` |
| 5402–5422 | async `refreshNotifBadge()` |
| 5423–5436 | `setNotifFilter(filter)` |
| 5437–5499 | async `loadNotifications()` |
| 5500–5515 | async `markNotifRead(notifId, btn)` |
| 5516–5533 | async `notifOpen(notifId, type, cardEl)` |
| 5534–5555 | async `markAllRead()` |

### REVIEW SUMMARY

| บรรทัด | function |
|---|---|
| 5556–5581 | async `loadReviewSummary(userIdForReview, role, containerId)` |

### JOB CATEGORIES CASCADE

| บรรทัด | function |
|---|---|
| 5582–5592 | async `loadCategories()` |
| 5593–5612 | async `initCategoryDropdowns()` |
| 5613–5630 | async `loadJobTitles(categorySelectId, titleSelectId)` |
| 5631–5638 | `syncSkillCode(titleSelectId, hiddenInputId)` |

### REVIEWS

| บรรทัด | function |
|---|---|
| 5639–5735 | async `loadMyReviews()` |

### Received reviews

| บรรทัด | function |
|---|---|
| 5736–5749 | async `loadTagsForReview(appId, targetRole)` |
| 5750–5757 | `setStar(appId, val)` |
| 5758–5761 | `toggleTag(appId, tagKey, el)` |
| 5762–5767 | `setRehire(appId, val, btn)` |
| 5768–5807 | async `submitReview(appId, targetRole)` |

### SESSION TIMEOUT

| บรรทัด | function |
|---|---|
| 5808–5824 | `_resetSessionTimers()` |
| 5825–5837 | `_showSessionWarning()` |
| 5838–5931 | `extendSession()` |

### START

| บรรทัด | function |
|---|---|
| 5932–5935 | `openPolicyModal(tab)` |
| 5936–5938 | `closePolicyModal()` |
| 5939–5946 | `switchPolicyTab(tab)` |
| 5947–5982 | `showOnboardModal(role)` |
| 5983–6045 | `closeOnboardModal()` |
| 6046–6051 | `openDeleteAccountModal()` |
| 6052–6059 | `closeDeleteAccountModal()` |
| 6060 | async `doDeleteAccount()` |

## 🌐 Global state

> ตัวแปรพวกนี้อยู่นอก function = ทุกหน้าใช้ร่วมกัน · **แก้ function ที่เขียนตัวไหน ต้องไล่ดูทุกตัวที่อ่านมันด้วย**

| บรรทัด | ตัวแปร | ค่าเริ่มต้น | ถูกอ้างถึง (บรรทัด) |
|---|---|---|---|
| 2325 | `_lang` | `localStorage.getItem('wh_lang') || 'th'` | 2325, 2326, 2328, 2632, 3755, 3925, 4434, 4481, 4534, 5356, 5393, 5464 …(+3) |
| 2374 | `token` | `localStorage.getItem('wh_token') || ''` | 39, 40, 41, 42, 295, 2342, 2374, 2407, 2407, 2515, 2574, 2577 …(+12) |
| 2375 | `userRole` | `localStorage.getItem('wh_role') || ''` | 2375, 2575, 2578, 2580, 2585, 2606, 2606, 2608, 2609, 2610, 3110, 3120 …(+7) |
| 2376 | `userId` | `localStorage.getItem('wh_uid') || ''` | 2376, 2576, 2579, 2585, 2920, 2923, 3506, 5877 |
| 2377 | `callCount` | `0` | 2377, 2412, 2413 |
| 2378 | `debugOpen` | `false` | 2378, 2391, 2392, 2399, 2399, 2400, 2401 |
| 2670 | `myPhone` | `''` | 2670, 2671, 2703, 3316, 3317, 3461, 3532 |
| 2672 | `p` | `null` | 85, 95, 175, 476, 542, 552, 660, 753, 819, 829, 927, 927 …(+248) |
| 3316 | `myPhone` | `''` | 2670, 2671, 2703, 3316, 3317, 3461, 3532 |
| 3642 | `_nearbyMap` | `null` | 3642, 3656, 3656, 3704, 3705, 3722, 3728, 3732, 3814, 3821, 3821, 3823 |
| 3643 | `_nearbyCircle` | `null` | 3643, 3726, 3726, 3731, 3738, 3738 |
| 3644 | `_nearbyMarker` | `null` | 3644, 3725, 3725, 3727 |
| 3645 | `_jobMarkers` | `[]` | 3645, 3803, 3804, 3824 |
| 3646 | `_nearbyScope` | `'related'` | 3646, 3666, 3668, 3669, 3800 |
| 4058 | `startMin` | `sh * 60 + sm, endMin = eh * 60 + em` | 4058, 4059, 4060 |
| 4189 | `_rosterPoll` | `null, _rosterTick = null, _rosterSig = n…` | 4189, 4195, 4195, 4195, 4235, 4267, 4267 |
| 4206 | `s` | `((h2*60+m2) - (h1*60+m1)) * 60` | 1251, 1251, 2211, 3109, 3110, 3112, 3337, 3337, 3339, 3339, 3363, 3364 …(+46) |
| 4214 | `late` | `(now.getHours()*60 + now.getMinutes()) -…` | 4214, 4215, 4215, 4215, 4215, 4216 |
| 4363 | `_asTick` | `null` | 4363, 4364, 4364, 4364, 4398 |
| 4435 | `availOn` | `true` | 4435, 4436, 4450, 4450, 4450 |
| 4452 | `h` | `''` | 2406, 2407, 2408, 4213, 4214, 4452, 4453, 4458, 4463, 4467, 4470, 4474 …(+2) |
| 4765 | `autocompletes` | `{}` | 4765, 4791 |
| 5311 | `_notifTimer` | `null` | 5311, 5399 |
| 5312 | `_notifFilter` | `'all'` | 2657, 5312, 5424, 5441, 5445 |
| 5580 | `_categoriesCache` | `null` | 5580, 5583, 5583, 5585, 5586 |
| 5804 | `_sessionTimer` | `null` | 5804, 5811, 5819, 5859 |
| 5805 | `_sessionWarnTimer` | `null` | 5805, 5812, 5817, 5860 |
| 5806 | `_countdownTimer` | `null` | 5806, 5815, 5828, 5834, 5861 |
| 5827 | `remaining` | `SESSION_WARN_MS / 1000` | 5827, 5829, 5830, 5831, 5834 |

## ⏱️ Timer / Polling

| ตั้งที่บรรทัด | handle | ชนิด | เรียก | เคลียร์ที่บรรทัด |
|---|---|---|---|---|
| 4267 | `_rosterPoll` | setInterval | `loadRoster` | 4195 |
| 4268 | `_rosterTick` | setInterval | `tickRosterTimers` | 4196 |
| 4398 | `_asTick` | setInterval | `tickActiveShiftTimers` | 4364 |
| 5399 | `_notifTimer` | setInterval | `refreshNotifBadge` | **⚠️ ไม่เคยเคลียร์** |
| 5817 | `_sessionWarnTimer` | setTimeout | `_showSessionWarning` | 5812, 5860 |
| 5819 | `_sessionTimer` | setTimeout | `(inline)` | 5811, 5859 |
| 5828 | `_countdownTimer` | setInterval | `(inline)` | 5815, 5834, 5861 |

## 🐒 Function ที่ถูกเขียนทับภายหลัง (monkey patch)

> 🔴 **อ่านก่อนแก้:** ตัวประกาศเดิมกับตัวที่ทำงานจริง**คนละตัว** · แก้ที่ `function foo()` เฉยๆ จะไม่มีผลกับ wrapper

| function | ประกาศเดิม | ถูกเขียนทับที่ |
|---|---|---|
| `saveSession` | 2573 | **5852** |
| `doLogout` | 2583 | **5858** |

## 🔌 Backend endpoints ที่ frontend เรียก

`:x` = ส่วนที่เป็นตัวแปร (template literal)

| method | path | เรียกที่บรรทัด |
|---|---|---|
| GET | `/admin/disputes` | 2978 |
| PATCH | `/admin/disputes/:x/resolve` | 3000 |
| PATCH | `/admin/jobs/:x/status` | 3036 |
| PATCH | `/admin/kyc/:x/review` | 2969 |
| GET | `/admin/kyc/pending` | 2932 |
| GET | `/admin/payments` | 3045 |
| POST | `/admin/payments/:x/resolve` | 3089 |
| GET | `/admin/stats` | 2822 |
| PATCH | `/admin/users/:x/status` | 2923 |
| POST | `/applications/:x/accept-backup` | 5007 |
| POST | `/applications/:x/auto-confirm` | 5104 |
| POST | `/applications/:x/checkin` | 5025 |
| POST | `/applications/:x/complete` | 5046 |
| POST | `/applications/:x/confirm-payment` | 5228 |
| GET | `/applications/:x/contact` | 4966, 5084 |
| PATCH | `/applications/:x/decide` | 4494, 4734 |
| POST | `/applications/:x/dispute` | 5126 |
| PATCH | `/applications/:x/mark-noshow` | 4352 |
| FETCH | `/applications/:x/pay` | 5205 |
| POST | `/applications/:x/report-payment` | 5243 |
| POST | `/applications/:x/start` | 5059 |
| POST | `/applications/:x/verify` | 4358, 5072 |
| POST | `/auth/google/callback` | 2518 |
| GET | `/auth/google/url?role=:x` | 2495 |
| POST | `/auth/login` | 2536 |
| GET | `/auth/me` | 2671, 3317 |
| PATCH | `/auth/phone` | 2750, 3633 |
| POST | `/auth/register` | 2565 |
| POST | `/employers/profile` | 2747, 4042 |
| PATCH | `/employers/profile` | 2749 |
| GET | `/employers/profile/me` | 2673, 3208, 3997 |
| POST | `/employers/verify/request` | 5272 |
| FETCH | `/employers/workplace-photo` | 2765 |
| GET | `/job-categories` | 5585 |
| GET | `/job-categories/:x/titles` | 5623 |
| POST | `/jobs` | 4128 |
| POST | `/jobs/:x/apply` | 3860 |
| GET | `/jobs/:x/candidates` | 3213, 4248, 4645 |
| POST | `/jobs/:x/confirm-backup-wage` | 4991 |
| PATCH | `/jobs/:x/status` | 4629, 4636 |
| GET | `/jobs/mine` | 3209, 4238, 4528 |
| GET | `/jobs/nearby?lat=13.7018&lng=100.6011&radius_km=25&scope=all` | 3132 |
| GET | `/jobs/nearby?lat=:x&lng=:x&radius_km=:x&scope=:x` | 3800 |
| PATCH | `/notifications/:x/read` | 5502, 5521 |
| PATCH | `/notifications/read-all` | 5538 |
| GET | `/notifications/unread-count` | 5404 |
| GET | `/notifications:x` | 5442 |
| FETCH | `/public/stats` | 2464 |
| GET | `/review-tags?target_role=:x` | 5738 |
| POST | `/reviews` | 5790 |
| GET | `/reviews/me` | 5645 |
| GET | `/reviews/pending` | 5644 |
| FETCH | `/users/me` | 6065 |
| POST | `/users/report` | 5297 |
| GET | `/workers/applications` | 3128, 3877, 4379 |
| POST | `/workers/background-check/request` | 5259 |
| GET | `/workers/earnings` | 3129, 4579 |
| FETCH | `/workers/kyc/upload` | 2800 |
| POST | `/workers/profile` | 3595 |
| PATCH | `/workers/profile` | 3622, 4501, 4510 |
| GET | `/workers/profile/me` | 3127, 3319, 4378, 4436 |
| GET | `/zones` | 5596 |

---

_generated by `tools/gen_map.py` · source sha256 `3a84f52cf83e`_
