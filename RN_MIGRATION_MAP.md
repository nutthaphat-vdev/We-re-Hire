# RN_MIGRATION_MAP — React Native Migration Analysis

> เอกสารนี้ **read-only analysis** — ไม่ใช่แผน implement  
> แหล่งข้อมูล: `INDEX_MAP.md` (auto-gen 169 functions), `COUPLING_MAP.md` (17 กับดัก), `index.html` (6,480 บรรทัด), `main.py` (62 endpoints)  
> เป้าหมาย: ให้พี่เห็นล่วงหน้าก่อนทำ RN จริงว่าอะไรยกไปได้ทันที (logic) และอะไรต้องเขียนใหม่หมด (DOM)  
> วันที่: 2026-07-23

---

## หมวด A — Business Logic (REUSE ได้ใน RN)

> ฟังก์ชันพวกนี้ไม่แตะ DOM, `localStorage`, browser API — ย้ายไป `src/utils/` ใน Expo ได้เลย

### A-1 ฟังก์ชัน Pure (ไม่มี side-effect เลย)

| function | บรรทัด | ทำอะไร | พึ่ง DOM/browser? |
|---|---|---|---|
| `calcWorkHours(start, end)` | 4363 | คำนวณชั่วโมงงานจาก `"HH:MM"` string รองรับข้ามเที่ยงคืน | ❌ ไม่มี |
| `canApplyNow(items)` | 3888 | `items.filter(i=>i.required).every(i=>i.done)` — pure boolean | ❌ ไม่มี |
| `_elapsedSec(iso)` | 4499 | `(Date.now() - new Date(iso)) / 1000` — elapsed seconds | ❌ ไม่มี |
| `_hhmmss(s)` | 4500 | seconds → `"HH:MM:SS"` string | ❌ ไม่มี |
| `_fmtHM(iso)` | 4506 | ISO → `"HH:MM"` (local time) | ❌ ไม่มี |
| `_shiftSeconds(ws, we)` | 4511 | shift duration in seconds รองรับข้ามเที่ยงคืน | ❌ ไม่มี |
| `_minutesLate(ws)` | 4518 | นาทีที่เลย work_start จาก Bangkok local time | ❌ ไม่มี |
| `_rosterRank(kind)` | 4526 | sort key: ghosting→0 … upcoming→5 | ❌ ไม่มี |
| `_rosterKind(c)` | 4529 | candidate status → display kind (`ghosting`/`checked_in`/`working`/`completed`/`unpaid`/`upcoming`) | ❌ ไม่มี |
| `_notifDateLabel(dateStr)` | 5700 | วันนี้/เมื่อวาน/วันที่เต็ม (อ่าน `_lang` global แต่ไม่แตะ DOM) | ❌ ไม่มี |
| `_notifLabelMap(type)` | 5641 | notification type → `{text, color}` (เรียก `t()` แต่ไม่แตะ DOM) | ❌ ไม่มี |
| `_notifNavMap` | 5659 | object: notification type → page route key | ❌ ไม่มี |
| `_autoCloseReasonLabel()` | 4836 | map: `no_applicants/no_hire/manual` → ข้อความ | ❌ ไม่มี |
| `dashInitials(name)` | 3169 | ตัดอักษร 2 ตัวแรก (ไทย/EN) สำหรับ avatar | ❌ ไม่มี |
| `t(key)` | 2330 | `LANG[_lang][key]` — i18n lookup | ❌ ไม่มี |
| `humanizeValidationError(detail)` | 2430 | FastAPI 422 array → ข้อความภาษาคน | ❌ ไม่มี |

### A-2 ข้อมูลคงที่ (Portable as-is)

| object/const | บรรทัด | ทำอะไร | หมายเหตุ RN |
|---|---|---|---|
| `LANG` | 1873 | สตริง TH/EN ทั้งหมด (~100+ keys) | ย้ายเป็น JSON ไฟล์ → ใช้กับ `i18n-js` หรือ `react-i18next` |
| `FIELD_LABEL` | 2419 | FastAPI field name → ป้ายภาษาไทย | ย้ายใน utils พร้อมกับ `humanizeValidationError` |
| `SUPABASE_URL` | 2537 | URL ตายตัว | เหมือนเดิม ย้ายใน `config/env.ts` |

### A-3 Business Logic Functions (มี API call แต่ logic reuse ได้)

> เหล่านี้ต้องการ `api()` helper ซึ่งใน RN จะเป็น `src/services/api.ts` — แต่ตัว logic ไม่ต้องเขียนใหม่

| function | บรรทัด | ทำอะไร | DOM ที่ต้องเปลี่ยน |
|---|---|---|---|
| `workerChecklist(profile, phone)` | 3862 | คำนวณ completeness items array — required/optional, done/not done | ❌ ไม่มี DOM (ใช้ `Date` เท่านั้น) |
| `fetchWorkerStatus()` | 3851 | `Promise.all([GET /workers/profile/me, GET /auth/me])` | ❌ ไม่มี DOM |
| `setPendingApply(v)` | 3841 | เขียน `_pendingApplyJobId` + `sessionStorage` | `sessionStorage` → Zustand + `AsyncStorage` |
| `returnToPendingApply(alertId)` | 3929 | เช็ค canApplyNow → navigate to nearby | `showAlert` → Toast, `showPage` → navigation.navigate |

### A-4 Job Lifecycle Logic (API call ดี — DOM feedback ต้องเปลี่ยน)

> แกนหลักของทุกตัวคือ `await api('POST', ...)` — ย้ายไปเป็น service function ได้เลย  
> ส่วน `btn.disabled`, `btn.outerHTML`, `alert()` ใน RN แทนด้วย loading state + Toast

| function | บรรทัด | API call | DOM ที่ต้องเปลี่ยน |
|---|---|---|---|
| `doCheckin(appId, btn)` | 5334 | `POST /applications/{id}/checkin` + GPS | `navigator.geolocation` → `expo-location` |
| `doComplete(appId, btn)` | 5356 | `POST /applications/{id}/complete` | btn mutation → loading state |
| `doStart(appId, btn)` | 5369 | `POST /applications/{id}/start` | btn mutation → loading state |
| `doVerify(appId, btn)` | 5382 | `POST /applications/{id}/verify` | btn mutation → loading state |
| `doDispute(appId, btn)` | 5434 | `POST /applications/{id}/dispute` | `prompt()` → `Alert.prompt()` |
| `doAcceptBackup(appId, btn)` | 5317 | `POST /applications/{id}/accept-backup` | btn mutation → loading state |
| `doConfirmBackupWage(jobId, amount, btn)` | 5301 | `POST /jobs/{id}/confirm-backup-wage` | btn mutation → loading state |
| `doPostJob()` | 4396 | `POST /jobs` | form reads (getElementById) → useState/useForm; validation logic เหมือนเดิม |
| `markNoShow(appId, btn)` | 4657 | `PATCH /applications/{id}/mark-noshow` | btn mutation → loading state |
| `decide(appId, decision, btn)` | 5044 | `PATCH /applications/{id}/decide` | btn mutation → loading state |
| `closeJob(jobId)` | 4940 | `PATCH /jobs/{id}/status` | setTimeout → navigation |
| `reopenJob(jobId)` | 4948 | `PATCH /jobs/{id}/status` | simple → loadMyJobs() |
| `submitReport()` | 5606 | `POST /users/report` | modal read → Modal state |
| `submitReview(appId, targetRole)` | 6163 | `POST /reviews` | star/tag state → useState |
| `requestBackgroundCheck(btn)` | 5569 | `POST /workers/background-check/request` | btn mutation → loading state |
| `requestEmployerVerify(btn)` | 5582 | `POST /employers/verify/request` | `btn.outerHTML = badge` → Alert + reload |

### A-5 Validation Rules (ยกมา RN ทันที)

กระจายอยู่ใน `doRegister()` และ `doPostJob()` — extract ออกเป็น validators:

```typescript
// src/utils/validators.ts — ย้ายจาก index.html
const PHONE_RE = /^0\d{9}$/;
const POSTAL_RE = /^\d{5}$/;

export function validatePhone(phone: string): string | null {
  const clean = phone.replace(/\D/g, '');
  if (!clean) return 'กรุณากรอกเบอร์โทรศัพท์';
  if (!PHONE_RE.test(clean)) return 'เบอร์โทรไม่ถูกต้อง — ต้องเป็นเลข 10 หลัก ขึ้นต้นด้วย 0';
  return null;
}

export function validateWorkHours(start: string, end: string): string | null {
  // reuse calcWorkHours logic
  const [sh, sm] = start.split(':').map(Number);
  const [eh, em] = end.split(':').map(Number);
  let startMin = sh * 60 + sm, endMin = eh * 60 + em;
  if (endMin <= startMin) endMin += 24 * 60;
  const hrs = (endMin - startMin) / 60;
  if (hrs > 8) return 'ช่วงเวลาทำงานต้องไม่เกิน 8 ชั่วโมง';
  return null;
}
```

---

## หมวด B — DOM/render (ต้องเขียนใหม่ใน RN)

> ทุกจุดที่แตะ `innerHTML`, `getElementById`, `document.*`, `window.*`, `google.maps.*`,  
> `localStorage`/`sessionStorage`, `alert()/prompt()`, `navigator.*`, event handler

### B-1 Router / Navigation

| ของเดิม (web) | ใน RN | หมายเหตุ |
|---|---|---|
| `showPage(name)` line 2684 — toggle `.active` CSS class | `navigation.navigate('ScreenName')` หรือ Bottom Tab | ดู coupling 1: earnings screen ต้องระวังเป็นพิเศษ |
| `initApp()` line 2649 — DOM show/hide + role-based nav setup | Conditional Navigator: `WorkerNavigator`, `EmployerNavigator`, `AdminNavigator` | role มาจาก Zustand auth store |
| `setLang()` re-render branch (~2342–2352) | i18next `changeLanguage()` — RN components re-render อัตโนมัติ | ไม่ต้องมี router ที่สอง |
| `closeSidebar()`, `openSidebar()` | Drawer.openDrawer() / closeDrawer() จาก `@react-navigation/drawer` | |

### B-2 Data-fetching / Render functions → Screens

> ทุกตัวใช้ `innerHTML` เป็นหลัก — ใน RN แทนด้วย Screen component + FlatList/ScrollView

| function | บรรทัด | RN Screen | Component หลัก |
|---|---|---|---|
| `loadDashboard()` | 3176 | `DashboardScreen` | StatCard, QuickActionGrid |
| `loadMyApps()` | 4193 | `MyApplicationsScreen` | FlatList + ApplicationCard |
| `loadMyJobs()` | 4838 | `MyJobsScreen` | FlatList + JobCard + CandidateSheet |
| `loadCandidates(jobId, ...)` | 4955 | Modal/Sheet inside MyJobsScreen | CandidateCard + ActionButtons |
| `loadRoster()` | 4540 | `RosterScreen` | FlatList + RosterRow + live timer |
| `loadActiveShift()` | 4680 | `ActiveShiftScreen` | ShiftCard + elapsed timer |
| `loadWorkerProfile()` | 3481 | `WorkerProfileScreen` | ProfileForm, SkillChips, KYCSection |
| `loadEmployerProfile()` | 2715 | `EmployerProfileScreen` | ProfileForm + MapPicker |
| `loadSettings()` | 4744 | `SettingsScreen` | ToggleRow, LanguagePicker |
| `loadNotifications()` | 5751 | `NotificationsScreen` | FlatList + NotifCard |
| `loadMyReviews()` | 6034 | `MyReviewsScreen` | PendingReviewCard, ReceivedReviewCard |
| `loadEarnings()` | 4889 | `EarningsScreen` | EarningsSummary, JobEarningRow |
| `loadAdminStats()` | 2879 | `AdminStatsScreen` | StatGrid |
| `loadAdminUsers()` | 2957 | `AdminUsersScreen` | UserTable + StatusActions |
| `loadAdminKYC()` | 2989 | `AdminKYCScreen` | KYCCard + ApproveRejectButtons |
| `loadAdminDisputes()` | 3035 | `AdminDisputesScreen` | DisputeCard + ResolveAction |
| `loadAdminJobs()` | 3066 | `AdminJobsScreen` | JobTable |
| `loadAdminPayments()` | 3102 | `AdminPaymentsScreen` | PaymentCard |

### B-3 Map-related functions → react-native-maps

| function (web) | บรรทัด | ใน RN | Package |
|---|---|---|---|
| `initNearbyMap()`, `buildMap()` | 3999, 4004 | `<MapView>` ใน NearbyScreen | `react-native-maps` |
| `sizeNearby()` — viewport height calc | 3954 | ไม่จำเป็น — RN layout engine จัดการเอง | — |
| `initPlacesAutocomplete()` | 5081 | `<GooglePlacesAutocomplete>` | `react-native-google-places-autocomplete` |
| `showMapPreview(containerId, lat, lng, ...)` | 5124 | `<MapView><Marker>` component | `react-native-maps` |
| `updatePinLocation()` | 5109 | `onDragEnd` prop บน `<Marker draggable>` | `react-native-maps` |
| `setLocationFromGPS()` | 5169 | `expo-location.getCurrentPositionAsync()` | `expo-location` |
| `showStaticMap()` | 5235 | Static Maps URL ใน `<Image>` หรือ `<MapView>` ขนาดเล็ก | `react-native-maps` |
| `useMyLocation()` | 5200 | กดปุ่ม → `expo-location` + update map state | `expo-location` |
| `_nbPill(lat, lng, label, ...)` | 3978 | Pressable ข้างบน MapView (location pill) | RN component |
| `searchNearby()` | 4092 | `GET /jobs/nearby?lat=&lng=&radius_km=&scope=` + state update | fetch + useState |

### B-4 Session / Auth functions

| function (web) | บรรทัด | สิ่งที่ต้องเปลี่ยนใน RN |
|---|---|---|
| `doLogin()` | 2578 | `document.getElementById('loginEmail')` → `useState` / TextInput |
| `doRegister()` | 2596 | form reads → useState; `document.getElementById('regTermsConsent')` → Checkbox state |
| `doGoogleLogin(role)` | 2540 | `window.location.href = data.url` → `expo-auth-session` หรือ `expo-web-browser` |
| `handleGoogleCallback()` | 2549 | parse `window.location.hash/search` → `expo-auth-session` callback flow |
| `saveSession(data)` | 2620 | `localStorage.setItem(...)` → `expo-secure-store` + Zustand |
| `doLogout()` | 2630 | `localStorage.clear()` + DOM toggle → SecureStore.clear() + navigate('Login') |
| `copyToken()` | 2639 | `navigator.clipboard` → `expo-clipboard` |

### B-5 Timer / Polling management → useEffect

| ของเดิม (web) | บรรทัด | ใน RN |
|---|---|---|
| `_rosterPoll = setInterval(loadRoster, 30s)` | 4575 | `useEffect(() => { const id = setInterval(refetch, 30000); return () => clearInterval(id); }, [])` ใน RosterScreen |
| `_rosterTick = setInterval(tickRosterTimers, 1s)` | 4576 | `useEffect` 1s interval, update elapsed state |
| `_asTick = setInterval(tickActiveShiftTimers, 1s)` | 4712 | `useEffect` ใน ActiveShiftScreen |
| `_notifTimer = setInterval(refreshNotifBadge, 30s)` | 5713 | NotificationContext — interval เริ่มเมื่อ login, cleanup เมื่อ logout |
| `_sessionTimer`, `_sessionWarnTimer`, `_countdownTimer` | 6212–6214 | AuthContext — ตรวจ JWT `exp` claim เมื่อ app foreground (`AppState.addEventListener`) |
| `stopRosterPolling()` | 4502 | useEffect cleanup (return value) |
| `stopActiveShiftTimer()` | 4672 | useEffect cleanup |

### B-6 UI Components ที่ต้องสร้าง (จาก render functions ปัจจุบัน)

| ของเดิม (web) | บรรทัด | RN Component |
|---|---|---|
| `renderRosterRow(r)` returns HTML string | 4579 | `<RosterRow application={r} />` |
| `renderShiftCard(a)` returns HTML string | 4716 | `<ShiftCard application={a} />` |
| `showProfileGateModal(items)` — innerHTML เข้า onboardModal | 3891 | `<ProfileGateModal items={items} onComplete={...} onSkip={...} />` |
| `showReportModal(targetUserId)` | 5595 | `<ReportModal userId={targetUserId} />` |
| `openPayModal(appId, ...)` | 5458 | `<PaymentModal appId={appId} />` |
| `showOnboardModal(role)` | 6342 | `<OnboardingModal role={role} />` |
| `openPolicyModal(tab)` | 6327 | `<PolicyModal initialTab={tab} />` |
| `renderSkillChips(...)` | 5983 | `<SkillChipList skills={skills} onRemove={...} />` |
| `ico(n, sz)` — SVG string | 4450 | `lucide-react-native` icons หรือ `react-native-svg` | 
| `esc(str)` — XSS escape | 2493 | ไม่จำเป็น — JSX escape อัตโนมัติ |
| `showAlert(id, msg, type)` | 2485 | `Toast.show(...)` จาก `react-native-toast-message` |

### B-7 KYC / File Upload

| function (web) | บรรทัด | ใน RN |
|---|---|---|
| `previewKYCImg(input, previewId)` | 2839 | `expo-image-picker` → `<Image source={{uri}}/>` |
| `submitKYC()` | 2847 | `expo-file-system` + FormData → `POST /workers/kyc/upload` (multipart) |
| `uploadEmpPhoto(input)` | 2818 | `expo-image-picker` → `POST /employers/workplace-photo` (multipart) |

### B-8 I18n / Theme

| function (web) | บรรทัด | ใน RN |
|---|---|---|
| `setLang(lang)` — re-renders หน้าด้วย innerHTML | 2331 | `i18next.changeLanguage(lang)` — RN re-renders อัตโนมัติ |
| `toggleAuthTheme()`, `toggleAppTheme()` | 2368, 4797 | Theme Context + `useColorScheme()` |

---

## หมวด C — API Contract (RN ใช้ซ้ำได้ 100%)

> Backend endpoint เดิมทุกตัว — RN เรียกผ่าน `src/services/api.ts` เหมือนกัน  
> Base URL: `https://we-re-hire.onrender.com`  
> Auth header: `Authorization: Bearer <token>`

### C-1 Auth

| method | path | body หลัก | response ที่ใช้ |
|---|---|---|---|
| `GET` | `/auth/google/url?role=worker\|employer` | — | `{url}` → InAppBrowser |
| `POST` | `/auth/google/callback` | `{access_token, role}` | `{access_token, role, user_id}` |
| `POST` | `/auth/register` | `{email, password, role, phone, terms_accepted}` | `{access_token, role, user_id}` |
| `POST` | `/auth/login` | `{email, password}` | `{access_token, role, user_id}` |
| `GET` | `/auth/me` | — | `{phone, full_name, ...}` |
| `PATCH` | `/auth/phone` | `{phone}` | — |
| `DELETE` | `/users/me` | — | — |

### C-2 Worker Profile & KYC

| method | path | body / notes | response หลัก |
|---|---|---|---|
| `GET` | `/workers/profile/me` | — | profile object |
| `POST` | `/workers/profile` | `{full_name, skills[], daily_rate_expected, ...}` | profile |
| `PATCH` | `/workers/profile` | ฟิลด์ที่ต้องการแก้ | profile |
| `POST` | `/workers/kyc/upload` | **multipart** — profile_photo, id_card_front/back หรือ passport/work_permit, selfie | `{status}` |
| `POST` | `/workers/background-check/request` | — | — |
| `GET` | `/workers/earnings` | — | earnings array |
| `GET` | `/workers/applications` | — | applications array |

### C-3 Employer Profile

| method | path | body / notes | response หลัก |
|---|---|---|---|
| `GET` | `/employers/profile/me` | — | employer profile |
| `POST` | `/employers/profile` | `{company_name, business_type, contact_person, phone, lat, lng, location_name}` | profile |
| `PATCH` | `/employers/profile` | ฟิลด์ที่ต้องการแก้ | profile |
| `POST` | `/employers/workplace-photo` | **multipart** | `{url}` |
| `POST` | `/employers/verify/request` | — | — |

### C-4 Jobs

| method | path | body / notes | response หลัก |
|---|---|---|---|
| `POST` | `/jobs` | `{title, required_skills[], daily_wage_rate, duration_days, slots_available, pay_method, work_start, work_end, start_date, ...}` | job |
| `GET` | `/jobs/mine` | — | jobs array |
| `PATCH` | `/jobs/{id}/status` | `{status: 'closed'\|'open'}` | — |
| `GET` | `/jobs/nearby` | `?lat=&lng=&radius_km=&scope=related\|all` | jobs array with match_score |
| `POST` | `/jobs/{id}/apply` | `{lat, lng}` (GPS ณ วันสมัคร) | application |
| `GET` | `/jobs/{id}/candidates` | — | candidates array |
| `POST` | `/jobs/{id}/confirm-backup-wage` | — | — |

### C-5 Job Lifecycle

| method | path | body / notes | response หลัก |
|---|---|---|---|
| `PATCH` | `/applications/{id}/decide` | `{decision: 'hired'\|'rejected'}` | — |
| `POST` | `/applications/{id}/checkin` | `{lat, lng}` | — |
| `POST` | `/applications/{id}/auto-confirm` | — | `{auto_confirm_start, status}` |
| `POST` | `/applications/{id}/start` | — | — |
| `POST` | `/applications/{id}/complete` | — | — |
| `POST` | `/applications/{id}/verify` | — | — |
| `POST` | `/applications/{id}/dispute` | `{reason}` | — |
| `PATCH` | `/applications/{id}/mark-noshow` | — | — |
| `GET` | `/applications/{id}/contact` | — | `{contact_name, company_name, phone}` |

### C-6 Anti-Ghosting

| method | path | body / notes | response หลัก |
|---|---|---|---|
| `GET` | `/jobs/{id}/backup-workers` | — | top-10 candidates |
| `POST` | `/applications/{id}/send-backup` | — | — |
| `POST` | `/applications/{id}/accept-backup` | — | — |

### C-7 Payment

| method | path | body / notes | response หลัก |
|---|---|---|---|
| `POST` | `/applications/{id}/pay` | multipart: `{pay_method, amount, slip_image?}` | — |
| `POST` | `/applications/{id}/confirm-payment` | — | — |
| `POST` | `/applications/{id}/report-payment` | `{reason}` | — |

### C-8 Notifications

| method | path | response หลัก |
|---|---|---|
| `GET` | `/notifications?filter=all\|unread` | notifications array |
| `GET` | `/notifications/unread-count` | `{count}` |
| `PATCH` | `/notifications/{id}/read` | — |
| `PATCH` | `/notifications/read-all` | — |

### C-9 Reviews & Trust & Safety

| method | path | body / notes | response หลัก |
|---|---|---|---|
| `GET` | `/reviews/pending` | — | pending reviews |
| `GET` | `/reviews/me` | — | received reviews |
| `POST` | `/reviews` | `{application_id, target_role, stars, tags[], would_rehire}` | — |
| `GET` | `/review-tags?target_role=worker\|employer` | — | tags array |
| `POST` | `/users/report` | `{target_user_id, reason, details}` | — |
| `GET` | `/workers/{uid}/review-summary` | — | `{avg_stars, count, tag_freq[]}` |
| `GET` | `/employers/{uid}/review-summary` | — | `{avg_stars, count, tag_freq[]}` |

### C-10 Master Data & Public

| method | path | response หลัก |
|---|---|---|
| `GET` | `/job-categories` | `[{code, name_th, name_en, icon, is_special}]` |
| `GET` | `/job-categories/{code}/titles` | `[{code, name_th, name_en}]` |
| `GET` | `/zones` | zones array |
| `GET` | `/public/stats` | `{worker_count, employer_count, job_count, zone_count}` |
| `GET` | `/health` | `{status:'ok'}` |

---

## หมวด D — Global State ที่ต้องออกแบบใหม่ใน RN

> ปัจจุบัน: ตัวแปร global ระดับไฟล์ + localStorage/sessionStorage  
> RN: Zustand stores + expo-secure-store (token) + AsyncStorage (non-sensitive)

### D-1 AuthStore (Zustand + expo-secure-store)

```typescript
// แทน: var token, userRole, userId + localStorage.setItem(...)
interface AuthStore {
  token: string | null;
  userRole: 'worker' | 'employer' | 'admin' | null;
  userId: string | null;
  saveSession: (data: SessionData) => Promise<void>;  // → SecureStore
  logout: () => Promise<void>;                         // → SecureStore.clear + navigate
}
```

**เดิม:** `saveSession()` line 2620 + monkey-patch wrapper line 6247  
**RN:** ไม่มี monkey-patch — `AuthStore.logout()` รับผิดชอบ clear timer ด้วยเลย (ดู coupling 2)

### D-2 I18nStore (Zustand + expo-localization)

```typescript
// แทน: var _lang = localStorage.getItem('wh_lang') || 'th'
interface I18nStore {
  lang: 'th' | 'en';
  setLang: (lang: 'th' | 'en') => void;
}
// ใช้ร่วมกับ i18next — ไม่ต้อง re-render ทั้งหน้าเหมือน setLang() เดิม
```

### D-3 PendingJobStore (Zustand + AsyncStorage)

```typescript
// แทน: _pendingApplyJobId + sessionStorage ('wh_pending_apply')
interface PendingJobStore {
  pendingJobId: string | null;
  setPendingJob: (id: string | null) => void;  // write-through to AsyncStorage
}
// เคลียร์เมื่อ: apply สำเร็จ, กด "ไว้ทีหลัง", logout
// เหตุผลที่ต้อง persist: user อาจ background app ระหว่างกรอกโปรไฟล์
```

### D-4 MasterDataStore (React Query — cache ระดับ session)

```typescript
// แทน: _categoriesCache + _titleLabels + _titleLabelsLang
// React Query ที่ staleTime: Infinity จำลอง "cache ตลอด session" แบบเดิมได้พอดี
// invalidate ด้วย queryClient.invalidateQueries(['categories']) เมื่อ admin เพิ่มหมวดใหม่
const { data: categories } = useQuery(['categories'], fetchCategories, { staleTime: Infinity });
```

### D-5 NotificationStore (Context — interval ระดับ app)

```typescript
// แทน: _notifTimer + _notifFilter
// Context ระดับ App (ไม่ใช่ screen) เพราะ badge ต้องอัปเดตทุกหน้า
interface NotifContext {
  unreadCount: number;
  filter: 'all' | 'unread';
  setFilter: (f: 'all' | 'unread') => void;
}
// interval เริ่มเมื่อ login (AuthStore ทำ), cleanup เมื่อ logout → ไม่มี 401 spam
```

### D-6 Screen-local state (ไม่ต้องเป็น global)

| global เดิม | บรรทัด | RN → local state |
|---|---|---|
| `_nearbyMap`, `_nearbyCircle`, `_nearbyMarker`, `_jobMarkers[]` | 3946–3949 | `useRef<MapView>()` + `useState<Marker[]>()` ใน NearbyScreen |
| `_nearbyScope` | 3950 | `useState('related')` ใน NearbyScreen |
| `_rosterPoll`, `_rosterTick`, `_rosterSig` | 4497 | `useEffect` cleanup ใน RosterScreen |
| `_asTick` | 4671 | `useEffect` cleanup ใน ActiveShiftScreen |
| `_notifFilter` | 5626 | `useState('all')` ใน NotificationsScreen |
| `autocompletes{}` | 5079 | `useRef` ใน PlacesInput component |
| `callCount`, `debugOpen` | 2381–2382 | __DEV__ debug panel (ลบใน production build) |
| `myPhone`, `p` | 2718, 2720 | fetched data จาก API ใน component ตามปกติ |

### D-7 Session Timeout (AuthContext)

```typescript
// แทน: _sessionTimer, _sessionWarnTimer, _countdownTimer (line 6199–6201)
// ไม่ต้องใช้ 3 timer — JWT มี exp claim อยู่แล้ว
// AuthContext.useEffect:
//   ฟัง AppState 'active' → decode token → เช็ค exp
//   ถ้า exp < now+5min → แสดง warning modal
//   ถ้า exp < now → logout()
```

---

## หมวด E — กับดักจาก COUPLING_MAP ที่ตามไป RN ด้วย (ต้องแก้ตอน migrate)

> พวกนี้ **ไม่ใช่ DOM bug** — เป็น logic bug ที่จะโผล่ใน RN เหมือนกันถ้าไม่แก้

### E-1 ⚠️ Earnings Screen ไม่ load ข้อมูล (COUPLING 1, page-earnings bug)

**สาเหตุ:** `loadEarnings()` ไม่ได้อยู่ใน `showPage()` — อยู่แค่ใน `setLang()` ทำให้กด nav ครั้งแรกเห็นหน้าว่าง  
**ใน RN:** `EarningsScreen` ต้องมี `useFocusEffect(() => { loadEarnings(); })` หรือ query ที่ trigger ตอน mount  
**แก้ web ด้วยได้เลย:** เพิ่ม `if (name === 'earnings') loadEarnings();` ใน `showPage()` (1 บรรทัด — ดู coupling 1)

### E-2 ⚠️ Notification polling ไม่หยุดหลัง logout (COUPLING 3)

**สาเหตุ:** `_notifTimer` (setInterval ทุก 30s) ไม่มีใครเคลียร์เมื่อ logout → 401 ทุก 30 วินาที  
**ใน RN:** NotificationContext ต้องมี cleanup:
```typescript
useEffect(() => {
  if (!token) return;  // ไม่ polling ถ้าไม่มี token
  const id = setInterval(refreshBadge, 30000);
  return () => clearInterval(id);  // cleanup เมื่อ token หมดหรือ unmount
}, [token]);
```

### E-3 ⚠️ `_pendingApplyJobId` ต้อง survive ออกจาก app (COUPLING 11)

**สาเหตุ:** flow คือ "กดสมัคร → ไปกรอกโปรไฟล์ → กลับมาสมัครต่อ" — ถ้า user ออกแล้วกลับมา state หาย  
**ใน RN:** ต้องใช้ `AsyncStorage` (ไม่ใช่แค่ Zustand in-memory) เพื่อ survive backgrounding  
**เคลียร์ใน 4 ทางออก:** apply สำเร็จ / กด skip / logout / WorkerProfileScreen unmount ที่ครบเงื่อนไข

### E-4 ⚠️ `workerChecklist()` ต้องตรงกับ backend เสมอ (COUPLING 12)

**สาเหตุ:** `POST /jobs/{id}/apply` บน main.py บล็อก: ไม่มีโปรไฟล์ (404), ไม่มีเบอร์ (400), work_permit หมดอายุ (403)  
**ใน RN:** ย้าย `workerChecklist()` เป็น `src/utils/workerChecklist.ts` — ต้องเขียน test ยืนยันว่าตรงกับ backend  
เมื่อ backend เพิ่ม validation ใหม่ **ต้องแก้ทั้งสองที่**

### E-5 ⚠️ GPS ไม่ได้เก็บในโปรไฟล์ — design เจตนา (COUPLING 13)

**สาเหตุ:** `worker_profiles.location` ไม่ถูกเขียนจาก frontend (ใช้ GPS ปัจจุบันตอนหางาน)  
**ผลข้างเคียงที่ยังค้าง:** anti-ghosting backup filter (`AND wp.location IS NOT NULL` ใน main.py ~2934) ทำให้ worker ทุกคนไม่โผล่ใน backup list  
**ใน RN:** เมื่อทำ "toggle available" ต้องส่ง GPS ปัจจุบันไปพร้อม `PATCH /workers/profile {is_available, lat, lng}` — ต้องทำ PDPA consent ก่อน (policies/02_PRIVACY_POLICY_PDPA.md ข้อ 2.1 + 9.1)

### E-6 ⚠️ SkillPicker มี 2 โหมดต่างกัน (COUPLING 15)

**สาเหตุ:** `syncSkillCode(titleSelectId, hiddenId)` vs `syncSkillCode(titleSelectId, hiddenId, containerId)`  
**ใน RN:** ต้องสร้าง 2 components แยกกัน:
- `<SingleSkillPicker>` — สำหรับ employer post job (เลือกได้ 1 ตำแหน่ง)
- `<MultiSkillPicker maxItems={3}>` — สำหรับ worker profile (สูงสุด 3 ตำแหน่ง, แสดง chips)

### E-7 ⚠️ Categories cascade ต้อง init ก่อน render form (COUPLING 6)

**สาเหตุ:** `initCategoryDropdowns()` ต้องเรียกหลัง form render เพราะ dropdown ถูกสร้างด้วย innerHTML ทีหลัง  
**ใน RN:** ไม่มีปัญหานี้ — React component render เมื่อ data พร้อม อัตโนมัติ  
แต่ต้องระวัง: ต้อง fetch categories ให้เสร็จ **ก่อน** render form (ใช้ loading state)

### E-8 ⚠️ `saveSession` / `doLogout` มี wrapper ซ้อน (COUPLING 2)

**สาเหตุ:** ฟังก์ชันเดิมถูก monkey-patch ที่ท้ายไฟล์ — timer cleanup อยู่ใน wrapper ไม่ใช่ใน original  
**ใน RN:** ไม่มีปัญหาถ้า AuthStore รับผิดชอบ timer cleanup ทั้งหมดเอง ไม่ต้องมี wrapper

---

## สิ่งที่ควรทำก่อนเริ่ม RN (เรียงตามความสำคัญ)

### 1. แก้ Earnings routing bug ใน web ก่อน (1 บรรทัด)
เพิ่ม `if (name === 'earnings') loadEarnings();` ใน `showPage()` ที่บรรทัดประมาณ 2710  
**เหตุผล:** ถ้าไม่แก้ตอนนี้ bug นี้จะถูกย้ายไป RN ด้วย และเป็นจุดที่ง่ายมาก

### 2. แก้ anti-ghosting backup filter ใน main.py (~2934)
เปลี่ยน `AND wp.location IS NOT NULL` เป็น optional หรือ fallback — ปัจจุบัน worker ทุกคนไม่โผล่ใน backup  
**เหตุผล:** กระทบทั้ง web และ RN เท่ากัน แก้ที่ backend ครั้งเดียวได้ทั้งสองแพลตฟอร์ม

### 3. Extract `workerChecklist()` เป็น TypeScript module + เขียน test
`src/utils/workerChecklist.ts` พร้อม Jest test ที่ตรวจว่าตรงกับ backend validation  
**เหตุผล:** นี่คือ logic เดียวที่ frontend กับ backend ต้อง sync กัน — ถ้าพัง ผู้ใช้จะสมัครงานไม่ได้โดยไม่รู้สาเหตุ

### 4. ตัดสินใจ GPS consent flow ก่อนเริ่ม ToggleAvailable feature ใน RN
ต้องออกแบบ PDPA consent modal สำหรับ "เปิดรับงาน" ที่ขอ GPS — ถ้าทำก่อน RN จะเขียน feature ได้ตรงตั้งแต่แรก

### 5. เลือก state management library ก่อนเริ่มโค้ด RN
CLAUDE.md บอกว่า "Zustand หรือ Context API" — ยิ่งใหญ่ขึ้นจะ migrate ยาก  
แนะนำ: Zustand สำหรับ global (Auth, PendingJob, I18n) + React Query สำหรับ server state (jobs, applications, categories)  
ไม่แนะนำ: Context API อย่างเดียวสำหรับ server state — จะ re-render มากเกินไป

---

## สรุปตัวเลข

| หมวด | จำนวน functions / items | สถานะ |
|---|---|---|
| A: Logic ที่ reuse ได้ทันที | 16 pure functions + 4 constants + 16 lifecycle functions | ✅ พร้อมย้าย |
| B: DOM/render ที่ต้องเขียนใหม่ | ~50 functions → ~20 screens + ~15 components | 🔴 ต้องเขียนใหม่ทั้งหมด |
| C: API endpoints | 62 endpoints ทุกตัว | ✅ ใช้ซ้ำได้ 100% |
| D: Global state variables | 24 globals → 5 Zustand stores + screen-local state | 🟡 redesign ก่อน code |
| E: Logic bugs ที่ต้องแก้ตอน migrate | 8 ข้อ | ⚠️ ถ้าไม่แก้ไปซ้ำใน RN |

---

_วิเคราะห์โดย Claude Code · 2026-07-23_  
_อ้างอิง: `INDEX_MAP.md` (sha `a9a129a19c28`), `COUPLING_MAP.md` (อัปเดต 2026-07-19), `index.html` 6,480 บรรทัด_
