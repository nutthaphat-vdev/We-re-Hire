# 05 — Angel One-Pager (ร่างดึงนักลงทุน)

> **ไฟล์นี้ใช้ยังไง:** ร่างนี้คือ one-pager ส่ง angel/incubator (pre-seed) **เติมตัวเลขจริงจากไฟล์ 03 หลังครบ 30 วันก่อนส่ง** ช่อง [...] คือที่ต้องกรอก ส่วนล่างบอกว่าต้องมี traction แค่ไหนถึง pitch ได้ไม่เขิน
> ตอนนี้ใช้เป็นโครงไว้ก่อน อย่าเพิ่งส่งถ้ายังไม่มี repeat employer

---

## WeHire — แพลตฟอร์มจ้างงานรายวันสำหรับกรุงเทพฯ
*จับคู่ Worker ↔ Employer งานรายวัน · ยืนยันตัวตน · จ่ายผ่านระบบ*

🔗 https://wearehiredmvp.vi-nutthaphat.workers.dev
👤 Founder: Nutthaphat Vichitasutanun · 📧 vi.nutthaphat@gmail.com

---

### 🔴 ปัญหา (Problem)
ตลาดแรงงานรายวันใน กทม. ยังวิ่งบน **Facebook group + ปากต่อปาก** ซึ่ง:
- **Employer** (ร้านอาหาร/โกดัง/โรงงาน) หาคนแทนกะทันหันยาก เจอคนหนีงาน (ghosting) ไม่มีรีวิว ไม่รู้จะไว้ใจใคร
- **Worker** หางานทีต้องวิ่งทีละที่ ไม่รู้ค่าแรงล่วงหน้า โดนเบี้ยว ไม่มีหลักฐานว่าตัวเองทำงานดี
- ไม่มีตัวกลางที่ **ยืนยันตัวตน + การันตีการจ่าย + มีระบบความน่าเชื่อถือ**

แรงงานนอกระบบไทยมีหลายล้านคน ส่วนใหญ่เป็น daily wage — ตลาดใหญ่ แต่ infrastructure ยังเป็นศูนย์

---

### 🟢 ทางออก (Solution)
แอพจับคู่งานรายวันที่:
- **Geo-matching** หางานใกล้ตัว (PostGIS) + match จากทักษะ/ค่าแรง
- **เช็คอิน GPS หน้างาน** กันโกหกว่ามาทำงาน
- **Anti-ghosting** auto-detect คนไม่มา + หา backup ให้อัตโนมัติ
- **Blind review 2 ฝั่ง** สร้าง trust score จริง
- **Lifecycle เต็ม:** โพสต์ → จ้าง → เช็คอิน → ทำงาน → verify → จ่าย/รีวิว

---

### 🏰 Moat (ทำไมคนอื่นลอกยาก)
1. **NDID Integration** — ยืนยันตัวตนระดับชาติผ่านแอพธนาคาร + ดึงประวัติอาชญากรรมจากสำนักงานตำรวจ ทำได้เฉพาะ NDID Member · เปิดงาน high-trust (รปภ./ดูแลเด็ก-ผู้สูงอายุ) ที่ platform ทั่วไปทำไม่ได้
2. **Work Permit Service** — บริการทำใบอนุญาตทำงานต่างด้าว (เมียนมา/ลาว/กัมพูชา) ขาย ฿10,000/คน (margin ~75%) · **ผูก employer กับ platform แน่นกว่าสัญญาใดๆ** — ทำ work permit ผ่านเราแล้วไม่มีวัน bypass
3. **Wallet Escrow** (Phase 3) — เงินอยู่ในระบบ pro-rata settlement = ไม่มีใครอยากออกนอกแอพ

---

### 💰 Business Model & Unit Economics
- **Stream 1 — Matching Fee 6%/transaction** (live แล้ว) · Gross margin **~90%**
  - งาน ฿400-600 → fee ฿24-36/งาน · หักฝั่ง worker (default), employer จ่าย flat
  - **Daily wage = rotation market** → employer ต้องกลับมาใช้ซ้ำเสมอ (worker ไม่ว่างตลอด)
- Stream 2 — Work Permit (฿10k/คน, recurring ต่ออายุทุก 2 ปี)
- Stream 3-5 — Job board / Premium subscription / Headhunter (ขึ้น ladder จากฐาน employer เดิม CAC = 0)
- **Blended gross margin เป้า >80%**

---

### 📈 Traction *(กรอกจริงหลัง 30 วัน — ไฟล์ 03)*
> เริ่มจากศูนย์ ทำ organic ใน 1 โซน ไม่ยิงแอด:
- ✅ Completed jobs จริง: **[__] งาน**
- ✅ Active employers: **[__] ร้าน** · **Repeat employer: [__] ราย ([__]%)** ⭐
- ✅ Active workers: **[__] คน**
- ✅ Fill rate: **[__]%** · GMV: **฿[____]**
- 💬 Quote จริง: *"[ก็อปคำพูด employer/worker ตัวจริง เช่น 'หาคนแทนได้ภายในวันเดียว ไม่เคยเจอแบบนี้']"*

> Insight: **[__]% ของร้านกลับมาจ้างซ้ำ** ใน 1 โซนเดียว ด้วย playbook ที่ทำซ้ำได้ → พร้อมขยาย

---

### 🎯 The Ask
ระดมทุน **Pre-seed ฿5,000,000** ใช้เพื่อ:
- ขยายจาก 1 โซน → 5 โซนใน กทม. ด้วย playbook เดิม (worker supply + employer outreach)
- พัฒนา **React Native mobile app** (Expo) — ลด friction การใช้งานจริง
- เปิด **Wallet Escrow + PromptPay** (Phase 3) ปิด loop การจ่ายเงิน = ล็อก moat
- เริ่ม pilot **Work Permit Service** (revenue stream margin สูง)
- Runway ~[12-18] เดือน ถึงเป้า [X] completed jobs/เดือน + revenue เริ่มเข้า

---

## 📋 เกณฑ์ "พร้อม pitch" — ต้องมี traction แค่ไหนถึงน่าเชื่อ

ก่อนส่ง one-pager นี้ออกไป พี่ควรมีอย่างน้อย:

| ระดับ | Traction | pitch ได้ไหม |
|-------|----------|-------------|
| ❌ ยังไม่พร้อม | signup เยอะ แต่ completed 0-2, ไม่มี repeat | อย่าเพิ่ง — ไม่มี story |
| 🟡 พอ pitch incubator/angel ใจดี | ~15-20 completed, repeat 2-3 ราย, organic, 1 zone | ได้ — เล่า "loop ทำงาน + คนกลับมา" |
| 🟢 แข็งแรง | 50+ completed/เดือน, repeat rate >30%, growth WoW ชัด, 2+ zone | ได้เต็มปาก — ต่อรอง valuation ดีขึ้น |

**สิ่งที่ angel pre-seed ดูจริง** (เรียงน้ำหนัก):
1. **Repeat / retention** — คนกลับมาซ้ำ = มี value จริง (สำคัญกว่าจำนวนดิบ)
2. **Founder ทำเองได้** — สร้าง+deploy เองทั้งระบบ = execution แข็ง (จุดแข็งพี่)
3. **Loop ทำงานจริง** — มี transaction คนแปลกหน้า ไม่ใช่แค่เพื่อน
4. **ขยายได้** — playbook ทำซ้ำในโซนใหม่ได้
5. **Moat ชัด** — NDID + work permit ที่คนอื่นลอกยาก

> **กฎ:** อย่า pitch ด้วยตัวเลข 0 จริง · มี repeat employer แค่ 2-3 ราย ก็เล่าได้น่าเชื่อกว่า signup 1,000 คนที่ไม่มีใครทำงาน · ความจริงเล็กๆ ชนะ vanity ใหญ่ๆ เสมอในสายตา angel ที่เก่ง

---

### 🇹🇭 ช่องทาง angel/incubator ไทยที่ควรลอง (เมื่อพร้อม)
- **500 TukTuks** (pre-seed, เน้น early) · **SCB10X** · **Beacon VC** (KBank, สาย fintech/แรงงาน)
- **Techsauce** ecosystem · **AngelList / Angel Thailand**
- Incubator/accelerator: **dtac accelerate, AIS the StartUp, True Digital Park**
- เริ่มจาก angel รายบุคคล/incubator ที่เข้าใจ labor/SME ก่อน VC ใหญ่
