# INDEX_MAP — แผนที่ `index.html`

> 🤖 **ไฟล์นี้ generate อัตโนมัติ — ห้ามแก้ด้วยมือ**  
> regenerate: `python tools/gen_map.py` · เช็คว่าเก่ายัง: `python tools/gen_map.py --check`  
> ส่วนที่เขียนด้วยมือ (coupling / กับดัก) อยู่ที่ **`COUPLING_MAP.md`** — สคริปต์ไม่แตะไฟล์นั้น

- generated: `2026-07-21 16:46` (BKK)
- source: `index.html` · **6,480 บรรทัด** · sha256 `a9a129a19c28`
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
| 1871–6287 | **JS (ก้อนหลัก)** · 4,416 บรรทัด |
| 6288–6301 | HTML markup |
| 6302–6382 | JS · 80 บรรทัด |
| 6383–6439 | HTML markup |
| 6440–6476 | JS · 36 บรรทัด |
| 6477–6480 | HTML markup |

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
| 3480 | WORKER PROFILE |
| 3826 | PROFILE COMPLETENESS (gate ก่อนสมัครงาน) |
| 3945 | NEARBY MAP INIT |
| 4079 | NEARBY JOBS |
| 4192 | MY APPLICATIONS |
| 4312 | EMPLOYER PROFILE CHECK |
| 4362 | POST JOB |
| 4496 | LIVE ROSTER |
| 4670 | ACTIVE SHIFT (worker — กระจกสะท้อน Roster) |
| 4743 | SETTINGS (role-aware) |
| 4828 | MY JOBS |
| 5078 | GOOGLE MAPS |
| 5201 | POST-JOB: inherit ที่อยู่หน้างานจากโปรไฟล์บริษัท |
| 5299 | JOB LIFECYCLE |
| 5451 | PAYMENT PROOF |
| 5567 | TRUST & SAFETY |
| 5623 | NOTIFICATIONS |
| 5868 | REVIEW SUMMARY |
| 5892 | JOB CATEGORIES CASCADE |
| 5947 | SKILLS แบบหลายตำแหน่ง (สูงสุด 3) |
| 6032 | REVIEWS |
| 6045 | Pending reviews |
| 6094 | Received reviews |
| 6194 | SESSION TIMEOUT |
| 6264 | START |

## 📄 หน้า (page) → ตัวโหลด → mount point

`showPage(key)` คือ router · มันซ่อน `.page` ทุกตัวแล้วโชว์ `#page-<key>` จากนั้นเรียก loader ตามตาราง

| page id | บรรทัด | key ที่ส่งให้ showPage | loader | mount point (JS เขียน innerHTML ลงตรงนี้) |
|---|---|---|---|---|
| `page-dashboard` | 1462–1472 | `dashboard` | — | `#dashContent` `#dashHeader` `#dashStats` |
| `page-nearby` | 1473–1516 | `nearby` | `initNearbyMap()` @3999 | `#nearbyResults` `#searchMapPreview` |
| `page-myapps` | 1517–1525 | `myapps` | `loadMyApps()` @4193 | `#myAppsContent` |
| `page-workerprofile` | 1526–1535 | `workerprofile` | `loadWorkerProfile()` @3481 | `#alertWorkerProfile` `#workerProfileContent` |
| `page-postjob` | 1536–1652 | `postjob` | `checkEmployerProfile()` @4313 | `#alertPostJob` `#employerProfileCheck` `#jobHoursSummary` `#jobProfileMapPreview` |
| `page-myjobs` | 1653–1661 | `myjobs` | `loadMyJobs()` @4838 | `#myJobsContent` |
| `page-roster` | 1662–1670 | `roster` | `loadRoster()` @4540 | `#rosterContent` |
| `page-employerprofile` | 1671–1679 | `employerprofile` | `loadEmployerProfile()` @2715 | `#employerProfileContent` |
| `page-activeshift` | 1680–1686 | `activeshift` | `loadActiveShift()` @4680 | `#activeShiftContent` |
| `page-settings` | 1687–1694 | `settings` | `loadSettings()` @4744 | `#settingsContent` |
| `page-admin-stats` | 1695–1703 | `admin-stats` | `loadAdminStats()` @2879 | `#adminStatsContent` |
| `page-admin-users` | 1704–1717 | `admin-users` | `loadAdminUsers()` @2957 | `#adminUsersContent` |
| `page-admin-kyc` | 1718–1726 | `admin-kyc` | `loadAdminKYC()` @2989 | `#adminKYCContent` |
| `page-admin-disputes` | 1727–1735 | `admin-disputes` | `loadAdminDisputes()` @3035 | `#adminDisputesContent` |
| `page-admin-jobs` | 1736–1749 | `admin-jobs` | `loadAdminJobs()` @3066 | `#adminJobsContent` |
| `page-admin-payments` | 1750–1758 | `admin-payments` | `loadAdminPayments()` @3102 | `#adminPaymentsContent` |
| `page-notifications` | 1759–1777 | `notifications` | `setNotifFilter()` @5737 | `#notificationsContent` |
| `page-earnings` | 1778–1785 | `earnings` | — | `#earningsContent` |
| `page-myreviews` | 1786–1870 | `myreviews` | `loadMyReviews()` @6034 | `#alertPay` `#alertReport` `#debugLogs` `#myReviewsContent` |

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
| 3176–3480 | async `loadDashboard()` |

### WORKER PROFILE

| บรรทัด | function |
|---|---|
| 3481–3760 | async `loadWorkerProfile()` |
| 3761–3766 | `showEditProfile()` |
| 3767–3795 | async `doCreateProfile()` |
| 3796–3840 | async `doUpdateProfile()` |

### PROFILE COMPLETENESS (gate ก่อนสมัครงาน)

| บรรทัด | function |
|---|---|
| 3841–3850 | `setPendingApply(v)` |
| 3851–3861 | async `fetchWorkerStatus()` |
| 3862–3890 | `workerChecklist(profile, phone)` |
| 3891–3920 | `showProfileGateModal(items)` |
| 3921–3928 | `goCompleteProfile()` |
| 3929–3953 | async `returnToPendingApply(alertId)` |

### NEARBY MAP INIT

| บรรทัด | function |
|---|---|
| 3954–3961 | `sizeNearby()` |
| 3962–3968 | `_onNearbyResize()` |
| 3969–3977 | `setNearbyScope(scope)` |
| 3978–3998 | `_nbPill(lat, lng, label, active, onClick)` |
| 3999–4003 | `initNearbyMap()` |
| 4004–4050 | `buildMap(lat, lng)` |
| 4051–4064 | `onGeoOk(pos)` |
| 4065–4091 | `onGeoFail()` |

### NEARBY JOBS

| บรรทัด | function |
|---|---|
| 4092–4159 | async `searchNearby()` |
| 4160–4192 | async `applyJob(jobId, lat, lng, btn)` |

### MY APPLICATIONS

| บรรทัด | function |
|---|---|
| 4193–4312 | async `loadMyApps()` |

### EMPLOYER PROFILE CHECK

| บรรทัด | function |
|---|---|
| 4313–4356 | async `checkEmployerProfile()` |
| 4357–4362 | `goCreateEmployerProfile()` |

### POST JOB

| บรรทัด | function |
|---|---|
| 4363–4370 | `calcWorkHours(start, end)` |
| 4371–4390 | `updateHoursSummary()` |
| 4391–4395 | `toggleJobOT()` |
| 4396–4449 | async `doPostJob()` |
| 4450–4498 | `ico(n, sz)` |

### LIVE ROSTER

| บรรทัด | function |
|---|---|
| 4499–4499 | `_elapsedSec(iso)` |
| 4500–4501 | `_hhmmss(s)` |
| 4502–4505 | `stopRosterPolling()` |
| 4506–4510 | `_fmtHM(iso)` |
| 4511–4517 | `_shiftSeconds(ws, we)` |
| 4518–4525 | `_minutesLate(ws)` |
| 4526–4528 | `_rosterRank(kind)` |
| 4529–4539 | `_rosterKind(c)` |
| 4540–4578 | async `loadRoster()` |
| 4579–4644 | `renderRosterRow(r)` |
| 4645–4656 | `tickRosterTimers()` |
| 4657–4663 | async `markNoShow(appId, btn)` |
| 4664–4671 | async `rosterVerifyPay(appId, jobId, jobTitle, amount, btn)` |

### ACTIVE SHIFT (worker — กระจกสะท้อน Roster)

| บรรทัด | function |
|---|---|
| 4672–4672 | `stopActiveShiftTimer()` |
| 4673–4679 | `tickActiveShiftTimers()` |
| 4680–4715 | async `loadActiveShift()` |
| 4716–4743 | `renderShiftCard(a)` |

### SETTINGS (role-aware)

| บรรทัด | function |
|---|---|
| 4744–4794 | async `loadSettings()` |
| 4795–4796 | `toggleLangSetting()` |
| 4797–4805 | `toggleAppTheme()` |
| 4806–4811 | async `dashHire(appId, btn)` |
| 4812–4822 | async `toggleAvailable(elm)` |
| 4823–4828 | async `toggleAvailInput(el)` |

### MY JOBS

| บรรทัด | function |
|---|---|
| 4829–4837 | `autoCloseCountdown(autoCloseAt)` |
| 4838–4888 | async `loadMyJobs()` |
| 4889–4939 | async `loadEarnings()` |
| 4940–4947 | async `closeJob(jobId)` |
| 4948–4954 | async `reopenJob(jobId)` |
| 4955–5043 | async `loadCandidates(jobId, jobTitle, jobWage)` |
| 5044–5080 | async `decide(appId, decision, btn)` |

### GOOGLE MAPS

| บรรทัด | function |
|---|---|
| 5081–5108 | `initPlacesAutocomplete(inputId, latId, lngId, displayId, mapPreviewId)` |
| 5109–5123 | `updatePinLocation(lat, lng, latId, lngId, displayId, inputId)` |
| 5124–5168 | `showMapPreview(containerId, lat, lng, label, latId, lngId, displayId, inputId)` |
| 5169–5199 | `setLocationFromGPS(latId, lngId, displayId, mapPreviewId, inputId)` |
| 5200–5201 | `useMyLocation()` |

### POST-JOB: inherit ที่อยู่หน้างานจากโปรไฟล์บริษัท

| บรรทัด | function |
|---|---|
| 5202–5226 | `applyProfileLocationToPostJob(emp)` |
| 5227–5234 | `toggleProfileLocation(cb)` |
| 5235–5261 | `showStaticMap(containerId, lat, lng, label)` |
| 5262–5268 | `initAllAutocompletes()` |
| 5269–5300 | async `showContact(appId, btn)` |

### JOB LIFECYCLE

| บรรทัด | function |
|---|---|
| 5301–5316 | async `doConfirmBackupWage(jobId, amount, btn)` |
| 5317–5333 | async `doAcceptBackup(appId, btn)` |
| 5334–5355 | async `doCheckin(appId, btn)` |
| 5356–5368 | async `doComplete(appId, btn)` |
| 5369–5381 | async `doStart(appId, btn)` |
| 5382–5394 | async `doVerify(appId, btn)` |
| 5395–5413 | async `showEmployerContact(appId, btn)` |
| 5414–5433 | async `toggleAutoConfirm(appId, btn)` |
| 5434–5452 | async `doDispute(appId, btn)` |

### PAYMENT PROOF

| บรรทัด | function |
|---|---|
| 5453–5457 | `payMethodChanged()` |
| 5458–5487 | `openPayModal(appId, jobId, jobTitle, amount)` |
| 5488–5491 | `closePayModal()` |
| 5492–5536 | async `doPaySubmit()` |
| 5537–5551 | async `doConfirmPayment(appId, btn)` |
| 5552–5568 | async `doReportPayment(appId, btn)` |

### TRUST & SAFETY

| บรรทัด | function |
|---|---|
| 5569–5581 | async `requestBackgroundCheck(btn)` |
| 5582–5594 | async `requestEmployerVerify(btn)` |
| 5595–5601 | `showReportModal(targetUserId)` |
| 5602–5605 | `closeReportModal()` |
| 5606–5640 | async `submitReport()` |

### NOTIFICATIONS

| บรรทัด | function |
|---|---|
| 5641–5668 | `_notifLabelMap(type)` |
| 5669–5699 | `_notifTranslateTitle(title)` |
| 5700–5710 | `_notifDateLabel(dateStr)` |
| 5711–5715 | async `startNotifPolling()` |
| 5716–5736 | async `refreshNotifBadge()` |
| 5737–5750 | `setNotifFilter(filter)` |
| 5751–5813 | async `loadNotifications()` |
| 5814–5829 | async `markNotifRead(notifId, btn)` |
| 5830–5847 | async `notifOpen(notifId, type, cardEl)` |
| 5848–5869 | async `markAllRead()` |

### REVIEW SUMMARY

| บรรทัด | function |
|---|---|
| 5870–5895 | async `loadReviewSummary(userIdForReview, role, containerId)` |

### JOB CATEGORIES CASCADE

| บรรทัด | function |
|---|---|
| 5896–5906 | async `loadCategories()` |
| 5907–5926 | async `initCategoryDropdowns()` |
| 5927–5962 | async `loadJobTitles(categorySelectId, titleSelectId)` |

### SKILLS แบบหลายตำแหน่ง (สูงสุด 3)

| บรรทัด | function |
|---|---|
| 5963–5977 | async `ensureTitleLabels()` |
| 5978–5982 | `getSkillList(hiddenInputId)` |
| 5983–6002 | `renderSkillChips(hiddenInputId, containerId, selectId)` |
| 6003–6022 | `syncSkillCode(titleSelectId, hiddenInputId, containerId)` |
| 6023–6033 | `removeSkill(code, hiddenInputId, containerId, selectId)` |

### REVIEWS

| บรรทัด | function |
|---|---|
| 6034–6130 | async `loadMyReviews()` |

### Received reviews

| บรรทัด | function |
|---|---|
| 6131–6144 | async `loadTagsForReview(appId, targetRole)` |
| 6145–6152 | `setStar(appId, val)` |
| 6153–6156 | `toggleTag(appId, tagKey, el)` |
| 6157–6162 | `setRehire(appId, val, btn)` |
| 6163–6202 | async `submitReview(appId, targetRole)` |

### SESSION TIMEOUT

| บรรทัด | function |
|---|---|
| 6203–6219 | `_resetSessionTimers()` |
| 6220–6232 | `_showSessionWarning()` |
| 6233–6326 | `extendSession()` |

### START

| บรรทัด | function |
|---|---|
| 6327–6330 | `openPolicyModal(tab)` |
| 6331–6333 | `closePolicyModal()` |
| 6334–6341 | `switchPolicyTab(tab)` |
| 6342–6377 | `showOnboardModal(role)` |
| 6378–6440 | `closeOnboardModal()` |
| 6441–6446 | `openDeleteAccountModal()` |
| 6447–6454 | `closeDeleteAccountModal()` |
| 6455 | async `doDeleteAccount()` |

## 🌐 Global state

> ตัวแปรพวกนี้อยู่นอก function = ทุกหน้าใช้ร่วมกัน · **แก้ function ที่เขียนตัวไหน ต้องไล่ดูทุกตัวที่อ่านมันด้วย**

| บรรทัด | ตัวแปร | ค่าเริ่มต้น | ถูกอ้างถึง (บรรทัด) |
|---|---|---|---|
| 2329 | `_lang` | `localStorage.getItem('wh_lang') || 'th'` | 2329, 2330, 2332, 2680, 4059, 4245, 4748, 4795, 4848, 5670, 5707, 5778 …(+7) |
| 2378 | `token` | `localStorage.getItem('wh_token') || ''` | 39, 40, 41, 42, 295, 2346, 2378, 2411, 2411, 2562, 2621, 2624 …(+12) |
| 2379 | `userRole` | `localStorage.getItem('wh_role') || ''` | 2379, 2622, 2625, 2627, 2633, 2654, 2654, 2656, 2657, 2658, 3171, 3181 …(+7) |
| 2380 | `userId` | `localStorage.getItem('wh_uid') || ''` | 2380, 2623, 2626, 2633, 2981, 2984, 3676, 6272 |
| 2381 | `callCount` | `0` | 2381, 2456, 2457 |
| 2382 | `debugOpen` | `false` | 2382, 2395, 2396, 2403, 2403, 2404, 2405 |
| 2718 | `myPhone` | `''` | 2718, 2719, 2751, 3485, 3486, 3630, 3711 |
| 2720 | `p` | `null` | 85, 95, 175, 480, 546, 556, 664, 757, 823, 833, 931, 931 …(+248) |
| 3485 | `myPhone` | `''` | 2718, 2719, 2751, 3485, 3486, 3630, 3711 |
| 3836 | `_pendingApplyJobId` | `(() => {` | 3831, 3836, 3842, 3930 |
| 3864 | `permitOk` | `true` | 3864, 3868, 3876 |
| 3946 | `_nearbyMap` | `null` | 3946, 3960, 3960, 4008, 4009, 4026, 4032, 4036, 4118, 4125, 4125, 4127 |
| 3947 | `_nearbyCircle` | `null` | 3947, 4030, 4030, 4035, 4042, 4042 |
| 3948 | `_nearbyMarker` | `null` | 3948, 4029, 4029, 4031 |
| 3949 | `_jobMarkers` | `[]` | 3949, 4107, 4108, 4128 |
| 3950 | `_nearbyScope` | `'related'` | 3950, 3970, 3972, 3973, 4104 |
| 4366 | `startMin` | `sh * 60 + sm, endMin = eh * 60 + em` | 4366, 4367, 4368 |
| 4497 | `_rosterPoll` | `null, _rosterTick = null, _rosterSig = n…` | 4497, 4503, 4503, 4503, 4543, 4575, 4575 |
| 4514 | `s` | `((h2*60+m2) - (h1*60+m1)) * 60` | 1255, 1255, 2215, 3170, 3171, 3173, 3506, 3506, 3508, 3508, 3532, 3533 …(+50) |
| 4522 | `late` | `(now.getHours()*60 + now.getMinutes()) -…` | 4522, 4523, 4523, 4523, 4523, 4524 |
| 4671 | `_asTick` | `null` | 4671, 4672, 4672, 4672, 4712 |
| 4749 | `availOn` | `true` | 4749, 4750, 4764, 4764, 4764 |
| 4766 | `h` | `''` | 2410, 2411, 2412, 4521, 4522, 4766, 4767, 4772, 4777, 4781, 4784, 4788 …(+2) |
| 5079 | `autocompletes` | `{}` | 5079, 5105 |
| 5625 | `_notifTimer` | `null` | 5625, 5713 |
| 5626 | `_notifFilter` | `'all'` | 2705, 5626, 5738, 5755, 5759 |
| 5894 | `_categoriesCache` | `null` | 5894, 5897, 5897, 5899, 5900 |
| 5962 | `_titleLabelsLang` | `null` | 5962, 5964, 5974 |
| 6199 | `_sessionTimer` | `null` | 6199, 6206, 6214, 6254 |
| 6200 | `_sessionWarnTimer` | `null` | 6200, 6207, 6212, 6255 |
| 6201 | `_countdownTimer` | `null` | 6201, 6210, 6223, 6229, 6256 |
| 6222 | `remaining` | `SESSION_WARN_MS / 1000` | 6222, 6224, 6225, 6226, 6229 |

## ⏱️ Timer / Polling

| ตั้งที่บรรทัด | handle | ชนิด | เรียก | เคลียร์ที่บรรทัด |
|---|---|---|---|---|
| 4575 | `_rosterPoll` | setInterval | `loadRoster` | 4503 |
| 4576 | `_rosterTick` | setInterval | `tickRosterTimers` | 4504 |
| 4712 | `_asTick` | setInterval | `tickActiveShiftTimers` | 4672 |
| 5713 | `_notifTimer` | setInterval | `refreshNotifBadge` | **⚠️ ไม่เคยเคลียร์** |
| 6212 | `_sessionWarnTimer` | setTimeout | `_showSessionWarning` | 6207, 6255 |
| 6214 | `_sessionTimer` | setTimeout | `(inline)` | 6206, 6254 |
| 6223 | `_countdownTimer` | setInterval | `(inline)` | 6210, 6229, 6256 |

## 🐒 Function ที่ถูกเขียนทับภายหลัง (monkey patch)

> 🔴 **อ่านก่อนแก้:** ตัวประกาศเดิมกับตัวที่ทำงานจริง**คนละตัว** · แก้ที่ `function foo()` เฉยๆ จะไม่มีผลกับ wrapper

| function | ประกาศเดิม | ถูกเขียนทับที่ |
|---|---|---|
| `saveSession` | 2620 | **6247** |
| `doLogout` | 2630 | **6253** |

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
| POST | `/applications/:x/accept-backup` | 5321 |
| POST | `/applications/:x/auto-confirm` | 5418 |
| POST | `/applications/:x/checkin` | 5339 |
| POST | `/applications/:x/complete` | 5360 |
| POST | `/applications/:x/confirm-payment` | 5542 |
| GET | `/applications/:x/contact` | 5280, 5398 |
| PATCH | `/applications/:x/decide` | 4808, 5048 |
| POST | `/applications/:x/dispute` | 5440 |
| PATCH | `/applications/:x/mark-noshow` | 4660 |
| FETCH | `/applications/:x/pay` | 5519 |
| POST | `/applications/:x/report-payment` | 5557 |
| POST | `/applications/:x/start` | 5373 |
| POST | `/applications/:x/verify` | 4666, 5386 |
| POST | `/auth/google/callback` | 2565 |
| GET | `/auth/google/url?role=:x` | 2542 |
| POST | `/auth/login` | 2583 |
| GET | `/auth/me` | 2719, 3191, 3486, 3854 |
| PATCH | `/auth/phone` | 2798, 3817 |
| POST | `/auth/register` | 2612 |
| POST | `/employers/profile` | 2795 |
| PATCH | `/employers/profile` | 2797 |
| GET | `/employers/profile/me` | 2721, 3326, 4317 |
| POST | `/employers/verify/request` | 5586 |
| FETCH | `/employers/workplace-photo` | 2826 |
| GET | `/job-categories` | 5899 |
| GET | `/job-categories/:x/titles` | 5937, 5968 |
| POST | `/jobs` | 4436 |
| POST | `/jobs/:x/apply` | 4179 |
| GET | `/jobs/:x/candidates` | 3331, 4556, 4959 |
| POST | `/jobs/:x/confirm-backup-wage` | 5305 |
| PATCH | `/jobs/:x/status` | 4943, 4950 |
| GET | `/jobs/mine` | 3327, 4546, 4842 |
| GET | `/jobs/nearby?lat=13.7018&lng=100.6011&radius_km=25&scope=all` | 3236 |
| GET | `/jobs/nearby?lat=:x&lng=:x&radius_km=:x&scope=:x` | 4104 |
| PATCH | `/notifications/:x/read` | 5816, 5835 |
| PATCH | `/notifications/read-all` | 5852 |
| GET | `/notifications/unread-count` | 5718 |
| GET | `/notifications:x` | 5756 |
| FETCH | `/public/stats` | 2511 |
| GET | `/review-tags?target_role=:x` | 6133 |
| POST | `/reviews` | 6185 |
| GET | `/reviews/me` | 6040 |
| GET | `/reviews/pending` | 6039 |
| FETCH | `/users/me` | 6460 |
| POST | `/users/report` | 5611 |
| GET | `/workers/applications` | 3189, 4197, 4687 |
| POST | `/workers/background-check/request` | 5573 |
| GET | `/workers/earnings` | 3190, 4893 |
| FETCH | `/workers/kyc/upload` | 2861 |
| POST | `/workers/profile` | 3777 |
| PATCH | `/workers/profile` | 3806, 4815, 4824 |
| GET | `/workers/profile/me` | 3188, 3488, 3853, 4686, 4750 |
| GET | `/zones` | 5910 |

---

_generated by `tools/gen_map.py` · source sha256 `a9a129a19c28`_
