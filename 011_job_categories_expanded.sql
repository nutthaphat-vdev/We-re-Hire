-- ============================================================
-- We're Hired Migration: 011_job_categories_expanded.sql
-- เพิ่ม 4 categories ใหม่ + titles เพิ่มเติมใน category เดิม
-- ============================================================

-- Step 1: เพิ่ม is_special column (สำหรับ category ที่ต้องการ NDID verify)
ALTER TABLE job_categories
  ADD COLUMN IF NOT EXISTS is_special BOOLEAN NOT NULL DEFAULT FALSE;

-- ============================================================
-- Step 2: Categories ใหม่
-- ============================================================
INSERT INTO job_categories (code, name_th, icon, sort_order, is_special) VALUES
  ('factory',     'โรงงานและการผลิต',      '🏭', 5, FALSE),
  ('event',       'งาน Event และ Seasonal', '🎪', 6, FALSE),
  ('interpreter', 'ล่ามภาษา',              '🗣️', 7, FALSE),
  ('caregiver',   'งานดูแลบุคคล',          '⚠️', 8, TRUE)  -- NDID required (Phase 3.5)
ON CONFLICT (code) DO NOTHING;

-- ============================================================
-- Step 3: Job Titles ใหม่
-- ============================================================

-- factory (ใหม่ทั้งหมด)
INSERT INTO job_titles (category_id, code, name_th, sort_order) VALUES
  ((SELECT id FROM job_categories WHERE code='factory'), 'welder',          'ช่างเชื่อม',              1),
  ((SELECT id FROM job_categories WHERE code='factory'), 'machinist',       'ช่างกลึง',                2),
  ((SELECT id FROM job_categories WHERE code='factory'), 'machine_repair',  'ช่างซ่อมเครื่องจักร',    3),
  ((SELECT id FROM job_categories WHERE code='factory'), 'qc_inspector',    'พนักงาน QC',              4),
  ((SELECT id FROM job_categories WHERE code='factory'), 'line_supervisor', 'ผู้ควบคุมสายพาน',         5),
  ((SELECT id FROM job_categories WHERE code='factory'), 'packer_factory',  'พนักงานแพ็คสินค้า',       6)
ON CONFLICT (code) DO NOTHING;

-- warehouse (เพิ่มเติม — ต่อจาก sort_order 4 เดิม)
INSERT INTO job_titles (category_id, code, name_th, sort_order) VALUES
  ((SELECT id FROM job_categories WHERE code='warehouse'), 'delivery_driver',  'คนขับรถส่งของ',         5),
  ((SELECT id FROM job_categories WHERE code='warehouse'), 'receiving_clerk',  'พนักงานรับ-ส่งสินค้า',  6)
ON CONFLICT (code) DO NOTHING;

-- fnb (เพิ่มเติม — ต่อจาก sort_order 3 เดิม)
INSERT INTO job_titles (category_id, code, name_th, sort_order) VALUES
  ((SELECT id FROM job_categories WHERE code='fnb'), 'cashier',    'แคชเชียร์',        4),
  ((SELECT id FROM job_categories WHERE code='fnb'), 'store_crew', 'พนักงานดูแลร้าน',  5)
ON CONFLICT (code) DO NOTHING;

-- maintenance (เพิ่มเติม — ต่อจาก sort_order 5 เดิม)
INSERT INTO job_titles (category_id, code, name_th, sort_order) VALUES
  ((SELECT id FROM job_categories WHERE code='maintenance'), 'general_repair', 'ช่างซ่อมทั่วไป', 6),
  ((SELECT id FROM job_categories WHERE code='maintenance'), 'tile_worker',    'ช่างกระเบื้อง',   7)
ON CONFLICT (code) DO NOTHING;

-- event (ใหม่ทั้งหมด)
INSERT INTO job_titles (category_id, code, name_th, sort_order) VALUES
  ((SELECT id FROM job_categories WHERE code='event'), 'event_staff',     'พนักงาน event/คอนเสิร์ต', 1),
  ((SELECT id FROM job_categories WHERE code='event'), 'pretty_mc',       'พริตตี้/MC',               2),
  ((SELECT id FROM job_categories WHERE code='event'), 'fair_sales',      'พนักงานขายงานแฟร์',        3),
  ((SELECT id FROM job_categories WHERE code='event'), 'data_entry_temp', 'Data entry ชั่วคราว',      4),
  ((SELECT id FROM job_categories WHERE code='event'), 'event_photo',     'ช่างภาพ event',             5)
ON CONFLICT (code) DO NOTHING;

-- interpreter (ใหม่ทั้งหมด)
INSERT INTO job_titles (category_id, code, name_th, sort_order) VALUES
  ((SELECT id FROM job_categories WHERE code='interpreter'), 'interp_th_my', 'ล่ามไทย-พม่า',    1),
  ((SELECT id FROM job_categories WHERE code='interpreter'), 'interp_th_la', 'ล่ามไทย-ลาว',     2),
  ((SELECT id FROM job_categories WHERE code='interpreter'), 'interp_th_kh', 'ล่ามไทย-กัมพูชา', 3),
  ((SELECT id FROM job_categories WHERE code='interpreter'), 'interp_th_en', 'ล่ามไทย-อังกฤษ',  4)
ON CONFLICT (code) DO NOTHING;

-- caregiver (ใหม่ทั้งหมด — is_special=true ดู Phase 3.5 NDID)
INSERT INTO job_titles (category_id, code, name_th, sort_order) VALUES
  ((SELECT id FROM job_categories WHERE code='caregiver'), 'elderly_care',   'ผู้ช่วยดูแลผู้สูงอายุรายวัน', 1),
  ((SELECT id FROM job_categories WHERE code='caregiver'), 'temp_nanny',     'พี่เลี้ยงเด็กชั่วคราว',        2),
  ((SELECT id FROM job_categories WHERE code='caregiver'), 'patient_assist', 'ผู้ช่วยดูแลผู้ป่วยระยะสั้น',  3)
ON CONFLICT (code) DO NOTHING;

-- ============================================================
-- ตรวจสอบผลลัพธ์
-- ============================================================
SELECT
  c.code,
  c.name_th       AS category,
  c.icon,
  c.is_special,
  COUNT(j.id)     AS title_count
FROM   job_categories c
LEFT   JOIN job_titles j ON j.category_id = c.id
GROUP  BY c.id, c.code, c.name_th, c.icon, c.is_special
ORDER  BY c.sort_order;
