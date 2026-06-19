-- Migration 014: Soft Delete Account
-- เพิ่ม column สำหรับ track การขอลบบัญชี

ALTER TABLE users
  ADD COLUMN IF NOT EXISTS deletion_requested_at TIMESTAMPTZ;

-- Index สำหรับ cron job ที่จะ hard delete หลัง 7 วัน
CREATE INDEX IF NOT EXISTS idx_users_deletion_requested
  ON users(deletion_requested_at)
  WHERE deletion_requested_at IS NOT NULL;

COMMENT ON COLUMN users.deletion_requested_at IS
  'Set when user requests account deletion. Hard delete runs 7 days later via cron.';
