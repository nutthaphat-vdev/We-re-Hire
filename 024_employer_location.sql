-- ============================================================
-- 024_employer_location.sql
-- ย้าย "ที่อยู่/พิกัดหน้างาน" ไปไว้ที่ employer_profiles (กรอกครั้งเดียว)
-- → post_job ไม่ต้องกรอกที่อยู่ทุกครั้ง (inherit จาก profile)
-- เหมาะกับ beachhead โรงแรม/ร้าน = สถานที่ fixed
--   (site ก่อสร้าง/หลายสาขา = เฟสหลัง ค่อยเพิ่ม override ต่อ job)
-- ------------------------------------------------------------
-- matching engine ไม่ต้องแตะ — ยังใช้ job_postings.location เหมือนเดิม
-- (post_job แค่เปลี่ยนที่มาของ location: form → employer profile)
-- ============================================================

ALTER TABLE employer_profiles
  ADD COLUMN IF NOT EXISTS location            GEOGRAPHY(POINT, 4326),  -- พิกัดหน้างาน
  ADD COLUMN IF NOT EXISTS location_name       VARCHAR(255),            -- ชื่อสถานที่ (เช่น "โรงแรม X ประตูน้ำ")
  ADD COLUMN IF NOT EXISTS address_text        TEXT,                    -- ที่อยู่เต็ม
  ADD COLUMN IF NOT EXISTS workplace_photo_url TEXT;                    -- รูปหน้างาน (โชว์ให้ worker เห็นตอนดูงาน)

-- index สำหรับ geo query (เผื่ออนาคต query employer ตามพิกัด)
CREATE INDEX IF NOT EXISTS idx_employer_location
  ON employer_profiles USING GIST (location);

-- ============================================================
-- ROLLBACK:
--   DROP INDEX IF EXISTS idx_employer_location;
--   ALTER TABLE employer_profiles
--     DROP COLUMN IF EXISTS location,
--     DROP COLUMN IF EXISTS location_name,
--     DROP COLUMN IF EXISTS address_text,
--     DROP COLUMN IF EXISTS workplace_photo_url;
-- ============================================================
