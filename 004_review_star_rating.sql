-- ============================================================
-- WeHire Migration: 004_review_star_rating.sql
-- เพิ่ม star_rating ใน reviews + อัปเดต tags ให้ตรง design
-- ============================================================

-- เพิ่ม star_rating column (1-5)
ALTER TABLE reviews ADD COLUMN IF NOT EXISTS star_rating SMALLINT
    CHECK (star_rating BETWEEN 1 AND 5);

-- ล้าง tags เดิมแล้วใส่ใหม่ให้ตรง UI
TRUNCATE review_tags RESTART IDENTITY CASCADE;

-- Tags สำหรับ Employer ประเมิน Worker
INSERT INTO review_tags (target_role, tag_key, tag_label, is_positive, sort_order) VALUES
  ('worker', 'on_time',       'ตรงเวลา',          TRUE, 1),
  ('worker', 'hardworking',   'ขยัน',              TRUE, 2),
  ('worker', 'follows_instr', 'ทำตามคำสั่ง',       TRUE, 3),
  ('worker', 'skilled',       'ทักษะตรงงาน',       TRUE, 4),
  ('worker', 'polite',        'สุภาพเรียบร้อย',     TRUE, 5),
  ('worker', 'responsible',   'รับผิดชอบ',          TRUE, 6);

-- Tags สำหรับ Worker ประเมิน Employer
INSERT INTO review_tags (target_role, tag_key, tag_label, is_positive, sort_order) VALUES
  ('employer', 'good_env',       'สภาพแวดล้อมดี',   TRUE, 1),
  ('employer', 'good_boss',      'เจ้านายดี',        TRUE, 2),
  ('employer', 'good_coworkers', 'เพื่อนร่วมงานดี',  TRUE, 3),
  ('employer', 'friendly',       'เป็นกันเอง',        TRUE, 4),
  ('employer', 'clean',          'สะอาด',            TRUE, 5),
  ('employer', 'pays_on_time',   'จ่ายตรงเวลา',      TRUE, 6),
  ('employer', 'has_equipment',  'อุปกรณ์ครบ',        TRUE, 7),
  ('employer', 'safe',           'ปลอดภัย',           TRUE, 8);
