-- ============================================================
-- WeHire Migration: 005_job_categories.sql
-- ============================================================

CREATE TABLE IF NOT EXISTS job_categories (
    id         SMALLSERIAL  PRIMARY KEY,
    code       VARCHAR(30)  NOT NULL UNIQUE,
    name_th    VARCHAR(100) NOT NULL,
    icon       VARCHAR(10)  NOT NULL DEFAULT '💼',
    sort_order SMALLINT     NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS job_titles (
    id          SMALLSERIAL  PRIMARY KEY,
    category_id SMALLINT     NOT NULL REFERENCES job_categories(id) ON DELETE CASCADE,
    code        VARCHAR(50)  NOT NULL UNIQUE,
    name_th     VARCHAR(100) NOT NULL,
    sort_order  SMALLINT     NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_job_titles_category ON job_titles (category_id);

-- Categories
INSERT INTO job_categories (code, name_th, icon, sort_order) VALUES
  ('warehouse',   'คลังสินค้า โลจิสติกส์ และขนส่ง', '📦', 1),
  ('fnb',         'ร้านอาหาร คาเฟ่ และบริการอาหาร',  '🍽️', 2),
  ('cleaning',    'งานบ้านและทำความสะอาด',            '🧹', 3),
  ('maintenance', 'งานช่าง และเทคนิค',                '🏗️', 4);

-- Jobs (ไม่ใช้ JOIN เพื่อหลีกเลี่ยง ambiguous column)
INSERT INTO job_titles (category_id, code, name_th, sort_order) VALUES
  ((SELECT id FROM job_categories WHERE code='warehouse'), 'loader',           'พนักงานยก/ย้ายสินค้า',                1),
  ((SELECT id FROM job_categories WHERE code='warehouse'), 'stocker',          'พนักงานจัดสต็อก/แพ็กของ',              2),
  ((SELECT id FROM job_categories WHERE code='warehouse'), 'forklift',         'พนักงานขับรถโฟล์คลิฟท์',               3),
  ((SELECT id FROM job_categories WHERE code='warehouse'), 'delivery_helper',  'ผู้ช่วยคนขับรถส่งของ (เด็กติดรถ)',      4),

  ((SELECT id FROM job_categories WHERE code='fnb'), 'waiter',     'พนักงานเสิร์ฟ',                          1),
  ((SELECT id FROM job_categories WHERE code='fnb'), 'dishwasher', 'พนักงานล้างจาน/ทำความสะอาดครัว',          2),
  ((SELECT id FROM job_categories WHERE code='fnb'), 'barista',    'พนักงานชงเครื่องดื่ม/บาริสต้าพาร์ทไทม์',  3),

  ((SELECT id FROM job_categories WHERE code='cleaning'), 'maid',       'พนักงานทำความสะอาด/แม่บ้านรายวัน', 1),
  ((SELECT id FROM job_categories WHERE code='cleaning'), 'gardener',   'คนงานดูแลสวน/ตัดหญ้า',             2),
  ((SELECT id FROM job_categories WHERE code='cleaning'), 'babysitter', 'พนักงานเลี้ยงเด็ก',                 3),

  ((SELECT id FROM job_categories WHERE code='maintenance'), 'construction_helper', 'ผู้ช่วยช่าง/กรรมกรก่อสร้างรายวัน', 1),
  ((SELECT id FROM job_categories WHERE code='maintenance'), 'painter',             'ช่างทาสี',                           2),
  ((SELECT id FROM job_categories WHERE code='maintenance'), 'electrician',         'ช่างซ่อมไฟฟ้าเบื้องต้น',             3),
  ((SELECT id FROM job_categories WHERE code='maintenance'), 'plumber',             'ช่างประปา/แก้น้ำรั่ว/ท่อตัน',        4),
  ((SELECT id FROM job_categories WHERE code='maintenance'), 'ac_technician',       'ช่างแอร์',                           5);

-- ตรวจสอบ
SELECT c.name_th AS category, j.name_th AS job
FROM   job_titles j
JOIN   job_categories c ON c.id = j.category_id
ORDER  BY c.sort_order, j.sort_order;
