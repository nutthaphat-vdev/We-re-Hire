-- ============================================================
-- We're Hired Migration: 010_kyc.sql
-- KYC Phase 2A — รองรับทั้งคนไทยและต่างด้าว
-- ============================================================
-- background_check_status (none/pending/approved/rejected) มีอยู่แล้ว
-- ไม่ต้องสร้างใหม่
-- ============================================================

-- Step 1: ประเภทเอกสาร (กำหนดว่าต้องอัปโหลดชุดไหน)
ALTER TABLE worker_profiles
  ADD COLUMN IF NOT EXISTS nationality_type VARCHAR(10) NOT NULL DEFAULT 'thai'
    CONSTRAINT chk_nationality_type CHECK (nationality_type IN ('thai', 'foreign'));

-- Step 2: รูปโปรไฟล์ (ทุกคน)
ALTER TABLE worker_profiles
  ADD COLUMN IF NOT EXISTS profile_photo_url TEXT;

-- Step 3: เอกสาร — คนไทย (บัตรประชาชน หน้า-หลัง)
ALTER TABLE worker_profiles
  ADD COLUMN IF NOT EXISTS id_card_front_url TEXT,
  ADD COLUMN IF NOT EXISTS id_card_back_url  TEXT;

-- Step 4: เอกสาร — ต่างด้าว (Passport + Work Permit)
ALTER TABLE worker_profiles
  ADD COLUMN IF NOT EXISTS passport_url         TEXT,
  ADD COLUMN IF NOT EXISTS work_permit_url      TEXT,
  ADD COLUMN IF NOT EXISTS work_permit_expiry   DATE;   -- แจ้งเตือนใกล้หมดอายุได้

-- Step 5: Selfie คู่เอกสาร (ทุกคน)
ALTER TABLE worker_profiles
  ADD COLUMN IF NOT EXISTS selfie_url TEXT;

-- Step 6: KYC metadata
ALTER TABLE worker_profiles
  ADD COLUMN IF NOT EXISTS kyc_submitted_at  TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS kyc_reviewed_at   TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS kyc_reviewed_by   UUID REFERENCES users(id),
  ADD COLUMN IF NOT EXISTS kyc_note          TEXT;       -- เหตุผล reject หรือ note จาก admin

-- Step 7: Index สำหรับ Admin dashboard โหลดเคส pending เร็ว
CREATE INDEX IF NOT EXISTS idx_worker_kyc_status
  ON worker_profiles (background_check_status)
  WHERE background_check_status = 'pending';

-- ============================================================
-- ตรวจสอบ: ดู columns ที่เพิ่งเพิ่ม
-- ============================================================
SELECT column_name, data_type, column_default, is_nullable
FROM   information_schema.columns
WHERE  table_name = 'worker_profiles'
  AND  column_name IN (
    'nationality_type',
    'profile_photo_url',
    'id_card_front_url', 'id_card_back_url',
    'passport_url', 'work_permit_url', 'work_permit_expiry',
    'selfie_url',
    'kyc_submitted_at', 'kyc_reviewed_at', 'kyc_reviewed_by', 'kyc_note'
  )
ORDER  BY column_name;
