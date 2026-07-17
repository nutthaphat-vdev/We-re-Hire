-- ============================================================
-- 025_employer_province.sql
-- เพิ่ม จังหวัด + รหัสไปรษณีย์ ให้ employer_profiles (ต่อจาก 024)
-- (worker_profiles มีอยู่แล้วจาก 022 — อันนี้ทำให้ employer เท่ากัน)
-- ============================================================

ALTER TABLE employer_profiles
  ADD COLUMN IF NOT EXISTS province    VARCHAR(50),   -- จังหวัด
  ADD COLUMN IF NOT EXISTS postal_code VARCHAR(10);   -- รหัสไปรษณีย์

-- ROLLBACK:
--   ALTER TABLE employer_profiles
--     DROP COLUMN IF EXISTS province,
--     DROP COLUMN IF EXISTS postal_code;
