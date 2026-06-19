-- Migration 015: Auto-Confirm Check-in
-- ถ้า employer กด Auto-Confirm ล่วงหน้า → ระบบ start งานทันทีที่ worker check-in
-- ถ้าไม่กด → cron auto-start หลัง 30 นาที

ALTER TABLE job_applications
  ADD COLUMN IF NOT EXISTS auto_confirm_start  BOOLEAN     NOT NULL DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS auto_confirmed_at   TIMESTAMPTZ;

-- index สำหรับ cron query
CREATE INDEX IF NOT EXISTS idx_job_applications_checkin_pending
  ON job_applications(checkin_at)
  WHERE status = 'checked_in' AND auto_confirmed_at IS NULL;
