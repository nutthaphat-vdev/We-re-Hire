-- ============================================================
-- We're Hired Migration: 012_anti_ghosting.sql
-- Active Anti-Ghosting System
-- ============================================================

-- Step 1: เพิ่ม columns ใน job_applications
ALTER TABLE job_applications
  ADD COLUMN IF NOT EXISTS noshow_marked_at    TIMESTAMPTZ,  -- เมื่อถูก mark no-show
  ADD COLUMN IF NOT EXISTS noshow_alerted_at   TIMESTAMPTZ,  -- cron ส่ง alert ครั้งแรก (กัน spam)
  ADD COLUMN IF NOT EXISTS backup_priority     INTEGER,      -- 1,2,3 = ลำดับ backup; NULL = ไม่ใช่
  ADD COLUMN IF NOT EXISTS backup_offered_at   TIMESTAMPTZ,  -- เมื่อ employer ส่ง backup offer
  ADD COLUMN IF NOT EXISTS backup_accepted_at  TIMESTAMPTZ;  -- เมื่อ worker ตอบรับ backup offer

-- Step 2: อัปเดต status CHECK constraint ให้รองรับ no_show
-- (DROP ชื่อ constraint เก่าที่อาจมีอยู่ก่อน)
ALTER TABLE job_applications DROP CONSTRAINT IF EXISTS job_applications_status_check;
ALTER TABLE job_applications DROP CONSTRAINT IF EXISTS chk_application_status;

ALTER TABLE job_applications ADD CONSTRAINT chk_application_status
  CHECK (status IN (
    'applied', 'shortlisted', 'hired', 'rejected', 'withdrawn',
    'checked_in', 'working', 'completed', 'verified', 'disputed', 'no_show'
  ));

-- Step 3: Index เร่ง cron เช็ค no-show (scan เฉพาะ hired rows)
CREATE INDEX IF NOT EXISTS idx_app_hired_noshow
  ON job_applications (status, noshow_alerted_at, noshow_marked_at)
  WHERE status = 'hired';

-- Step 4: Index lookup backup candidates ตาม job
CREATE INDEX IF NOT EXISTS idx_app_backup_priority
  ON job_applications (job_id, backup_priority)
  WHERE backup_priority IS NOT NULL;

-- ============================================================
-- ตรวจสอบ
-- ============================================================
SELECT column_name, data_type
FROM   information_schema.columns
WHERE  table_name = 'job_applications'
  AND  column_name IN (
    'noshow_marked_at', 'noshow_alerted_at',
    'backup_priority', 'backup_offered_at', 'backup_accepted_at'
  )
ORDER BY column_name;
