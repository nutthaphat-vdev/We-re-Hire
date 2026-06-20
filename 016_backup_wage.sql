-- Migration 016: Backup Wage Confirmation
-- เพิ่ม pro-rata wage lock สำหรับ backup worker flow

-- job_postings: เก็บ pending wage confirmation ฝั่ง employer
ALTER TABLE job_postings
  ADD COLUMN IF NOT EXISTS backup_wage_pending      BOOLEAN      NOT NULL DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS backup_wage_amount       DECIMAL(10,2),
  ADD COLUMN IF NOT EXISTS backup_wage_hours        DECIMAL(5,2),   -- remaining work hours
  ADD COLUMN IF NOT EXISTS backup_wage_confirmed_at TIMESTAMPTZ;

-- job_applications: เก็บ confirmed wage ที่ backup worker จะเห็นก่อนรับงาน
ALTER TABLE job_applications
  ADD COLUMN IF NOT EXISTS backup_confirmed_wage DECIMAL(10,2);

-- Index สำหรับ cron auto-confirm (job ที่รอ employer confirm อยู่)
CREATE INDEX IF NOT EXISTS idx_job_postings_backup_wage_pending
  ON job_postings(id)
  WHERE backup_wage_pending = TRUE AND backup_wage_confirmed_at IS NULL;

COMMENT ON COLUMN job_postings.backup_wage_pending      IS 'TRUE = รอ employer confirm wage ก่อนส่ง backup offer';
COMMENT ON COLUMN job_postings.backup_wage_amount       IS 'ค่าจ้าง pro-rata ที่คำนวณไว้ (฿)';
COMMENT ON COLUMN job_postings.backup_wage_hours        IS 'ชั่วโมงที่เหลือสำหรับ backup worker';
COMMENT ON COLUMN job_applications.backup_confirmed_wage IS 'ค่าจ้างที่ employer lock ไว้สำหรับ backup — แสดงให้ worker เห็นก่อนกด รับงาน';
