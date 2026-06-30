-- ============================================================
-- We're Hired Migration: 019_policy_consent.sql
-- PDPA consent audit trail — เก็บหลักฐานว่า user ยอมรับ policy
-- ตอนไหน และเวอร์ชันใด
-- ============================================================

ALTER TABLE users
  ADD COLUMN IF NOT EXISTS terms_accepted_at  TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS policy_version     VARCHAR(20);

-- ============================================================
-- ตรวจสอบ
-- ============================================================
SELECT column_name, data_type, is_nullable
FROM   information_schema.columns
WHERE  table_name = 'users'
  AND  column_name IN ('terms_accepted_at', 'policy_version')
ORDER  BY column_name;
