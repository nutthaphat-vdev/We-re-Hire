## Job Lifecycle Flow (008_job_lifecycle)

### States
hired → checked_in → working → completed → verified → (review)

### Migration: 008_job_lifecycle.sql
```sql
ALTER TABLE job_applications
  ADD COLUMN IF NOT EXISTS checkin_at           TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS checkin_lat          DECIMAL(10,7),
  ADD COLUMN IF NOT EXISTS checkin_lng          DECIMAL(10,7),
  ADD COLUMN IF NOT EXISTS work_started_at      TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS work_ended_at        TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS employer_verified_at TIMESTAMPTZ;
```

### API Endpoints
- POST /applications/{id}/checkin   — Worker กด "มาถึงแล้ว"
  → เช็ค GPS ≤ 150m จาก job location (PostGIS — ไม่มี cost)
  → ถ้าไกลกว่า → 400 error บอก distance จริง
  → notify Employer

- POST /applications/{id}/start     — Employer กด confirm เริ่มงาน
  → เช็ค time window ±30 นาที จาก work_start
  → set work_started_at = NOW()

- POST /applications/{id}/complete  — Worker กด "งานเสร็จ"
  → set work_ended_at = NOW()
  → notify Employer

- POST /applications/{id}/verify    — Employer กด verify จบงาน
  → set employer_verified_at = NOW()
  → trigger notification ให้ทั้งคู่ไป review

### Auto-verify Logic (Cron ทุก 30 นาที)
ถ้า work_ended_at - work_started_at >= duration_hours * 90%
AND Employer ไม่กด verify ภายใน 2 ชม. หลัง Worker กด complete
→ Auto-verify
→ notify ทั้งคู่
→ trigger review flow

### < 90% Duration Logic (Dispute Flow)
Worker กด complete แต่ชม. ไม่ครบ 90%
→ แจ้ง Employer ทันที "งานอาจไม่ครบ กรุณาตรวจสอบ"
→ Employer มี 2 ชม. ตัดสิน:
   - กด verify ปกติ → จ่ายเต็ม (Employer ยอมรับเอง)
   - กด dispute → ส่ง admin พร้อม evidence
→ ถ้าไม่กดอะไรใน 2 ชม. → auto escalate admin
→ Admin ตัดสิน → จ่ายตามชั่วโมงจริง หรือ dismiss
(Phase 3 Escrow จะ handle การจ่ายเงินอัตโนมัติตาม admin decision)

### Security Notes
- GPS check ใช้ PostGIS ST_Distance — ฟรี ไม่เรียก Google API
- GPS Spoofing: ยอมรับ risk ใน MVP, Phase ถัดไปเพิ่ม Selfie checkin
- Checkin แทนกัน: Phase ถัดไปเพิ่ม Selfie checkin
- Escrow (Phase 3) คือ fix ทุกช่องโหว่เรื่องเงินได้ในก้าวเดียว

---

## Pro-rata Settlement System (Phase 3 — Escrow)

### Escrow States
locked → disputed → settled_by_admin / released / refunded

### Tables Required
- escrow_locks (amount, status, worker_pct, worker_amount, employer_amount, settled_by, admin_note)
- wallets (available, locked per user)
- wallet_transactions (audit log ทุก movement)

### Auto-dispute Trigger
ถ้า duration < 90% AND ครบกำหนด 2 ชม.
→ escrow status: locked → disputed
→ ทั้ง Employer และ Worker ถอนไม่ได้จนกว่า Admin เคาะ

### Admin Settlement Flow (atomic transaction)
1. Admin กรอก worker_pct (0-100) + note
2. validate: 0 <= worker_pct <= 100, status = 'disputed'
3. worker_amount = escrow.amount * worker_pct / 100
4. employer_amount = escrow.amount - worker_amount - platform_fee
5. ยิงเงินเข้า Worker wallet (available)
6. คืนเงิน Employer wallet (available)
7. status → settled_by_admin + log admin user id
8. Notify ทั้งคู่

### Dispute Form (ทั้ง 2 ฝั่งต้องระบุเหตุผล)
Worker เลือก:
- ทำงานครบแล้ว (นับเวลาผิด)
- Employer สั่งให้หยุดก่อน
- เจ็บป่วยฉุกเฉิน
- อื่นๆ

Employer เลือก:
- Worker ออกเองโดยไม่แจ้ง
- งานไม่ผ่านมาตรฐาน
- อื่นๆ

### กรณี Worker ทำไม่ครบ
- Worker ออกเองโดยไม่มีเหตุผล → หักตามเวลาจริง + อาจมี penalty
- Worker ออกเพราะ Employer (สั่งหยุด/อันตราย) → ได้ 100% ไม่ใช่ความผิด Worker
- Admin เห็น evidence ทั้งสองฝั่งก่อนเคาะ % เสมอ

### Edge Cases
- worker_pct > 100 → reject ทันที
- Double settlement → เช็ค status = 'disputed' ก่อนทุกครั้ง
- Platform fee → หักจาก worker_amount ก่อน split
- settled_by → เก็บ admin user id ทุกครั้ง (audit trail)

---

## KYC System (Level 1 — Free)

### แนวทาง
Admin verify เอง manual — ฟรี 100% ใช้ Supabase Storage

### Flow
1. Worker upload รูปบัตรประชาชน (หน้า-หลัง) + Selfie คู่บัตร
2. เก็บใน Supabase Storage (free 1GB)
3. Admin เปิดดูแล้วกด Approve / Reject
4. background_check_status: pending → verified / failed

### Migration: 009_kyc.sql
```sql
ALTER TABLE worker_profiles
  ADD COLUMN IF NOT EXISTS id_card_front_url TEXT,
  ADD COLUMN IF NOT EXISTS id_card_back_url  TEXT,
  ADD COLUMN IF NOT EXISTS selfie_url        TEXT,
  ADD COLUMN IF NOT EXISTS kyc_submitted_at  TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS kyc_reviewed_by   UUID REFERENCES users(id),
  ADD COLUMN IF NOT EXISTS kyc_note          TEXT;
```

### หมายเหตุ
- background_check_status ที่มีอยู่แล้วใช้ได้เลย ไม่ต้องเพิ่ม
- Scale ได้ถึง ~1,000 workers โดยไม่มีปัญหา
- ถ้า volume เกิน → upgrade Level 2 (iDenfy ~$0.5/verification)
- OTP verify เบอร์โทร → ใช้ Supabase Auth SMS (free tier)

---

## Pro-rata Settlement — Final Logic (v2 with Platform Fee)

### สูตรคำนวณ (ยอดรวม balance เสมอ)
```
total_locked     = 600 บาท
actual_work_ratio = 0.70 (70% ของเวลาที่ตกลงไว้)

worker_gross     = total_locked × actual_work_ratio
                 = 600 × 0.70 = 420

platform_penalty = worker_gross × 10%
                 = 420 × 0.10 = 42

worker_payout_net  = worker_gross - platform_penalty
                   = 420 - 42 = 378

employer_refund_net = total_locked × (1 - actual_work_ratio)
                    = 600 × 0.30 = 180

✅ Balance check: 378 + 180 + 42 = 600 (เงินไม่รั่วไหล)
```

### Fields ที่ต้องเพิ่มใน escrow_locks
```sql
ALTER TABLE escrow_locks
  ADD COLUMN IF NOT EXISTS actual_work_ratio    DECIMAL(5,4),  -- 0.7000
  ADD COLUMN IF NOT EXISTS worker_payout_net    DECIMAL(10,2), -- 378
  ADD COLUMN IF NOT EXISTS employer_refund_net  DECIMAL(10,2), -- 180
  ADD COLUMN IF NOT EXISTS platform_penalty_fee DECIMAL(10,2); -- 42
```

### Backend Flow (Admin กดอนุมัติ)
```
Cron ทุก 30 นาที:
  ตรวจพบ duration < 90% AND ครบ 2 ชม.
  → escrow status: locked → disputed
  → ส่งเข้า Admin Dashboard

Admin ตรวจสอบ:
  → ดู evidence ทั้งสองฝั่ง (Worker + Employer)
  → กรอก actual_work_ratio (เช่น 0.70)
  → กด Confirm Settlement

ระบบคำนวณ atomic transaction:
  worker_gross          = total_locked × ratio
  platform_penalty_fee  = worker_gross × 0.10
  worker_payout_net     = worker_gross - platform_penalty_fee
  employer_refund_net   = total_locked × (1 - ratio)

  ✅ Validate: worker_payout_net + employer_refund_net + platform_penalty_fee = total_locked

สับท่อเงิน 3 ทาง (atomic):
  1. Worker wallet available  += worker_payout_net    (378)
  2. Employer wallet available += employer_refund_net  (180)
  3. WeHire platform wallet   += platform_penalty_fee  (42)

  escrow status → settled_by_admin
  log: admin_id, timestamp, ratio, amounts ทั้งหมด
  notify: Worker + Employer พร้อมรายละเอียด
```

### Edge Cases
- ratio > 1.0 → reject ทันที
- ratio = 1.0 → Worker ได้เต็ม (หัก fee ปกติ), Employer คืน 0
- ratio = 0.0 → Worker ได้ 0, Employer คืนเต็ม, platform fee = 0
- Double settlement → เช็ค status = 'disputed' ก่อนทุกครั้ง
- Balance ไม่ลงตัว → reject พร้อม alert admin

### Platform Fee Policy
- หัก 10% จาก worker_gross เท่านั้น (ไม่หักจาก employer_refund)
- เป็น penalty สำหรับ worker ที่ทำงานไม่ครบ
- ถ้า worker ออกเพราะ employer → admin กำหนด ratio = 1.0
  (worker ได้เต็ม, platform fee = 0, employer แบกรับเอง)
