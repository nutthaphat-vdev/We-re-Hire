-- ============================================================
-- WeHire Migration: 026_hotel_category.sql
-- เพิ่มหมวด "โรงแรมและที่พัก" (hotel) + 8 titles เฉพาะโรงแรม
-- สำหรับ Hotel Pilot · idempotent (ON CONFLICT DO NOTHING รันซ้ำได้)
--
-- icon = '' (เว้นว่าง ไม่ใช้ emoji — ตามที่ founder เลือก)
--   หมายเหตุ: ต้องเป็น '' ไม่ใช่ NULL เพราะ frontend render `${c.icon} ${name}`
--             ถ้า NULL จะโชว์คำว่า "null" หน้าชื่อหมวด
--
-- REUSE จากหมวด cleaning (ไม่ทำซ้ำ): maid (แม่บ้าน/housekeeping), gardener (คนสวน)
--   → โรงแรมเลือก 2 ตำแหน่งนี้จากหมวด cleaning ได้ตามเดิม
-- เพิ่มเฉพาะตำแหน่งที่โรงแรมใช้แต่ยังไม่มีในระบบ
-- ============================================================

INSERT INTO job_categories (code, name_th, icon, sort_order, is_special) VALUES
  ('hotel', 'โรงแรมและที่พัก', '', 5, FALSE)
ON CONFLICT (code) DO NOTHING;

INSERT INTO job_titles (category_id, code, name_th, sort_order) VALUES
  ((SELECT id FROM job_categories WHERE code='hotel'), 'room_attendant',    'พนักงานทำความสะอาดห้องพัก (housekeeping)', 1),
  ((SELECT id FROM job_categories WHERE code='hotel'), 'laundry_attendant', 'พนักงานซักรีด',                          2),
  ((SELECT id FROM job_categories WHERE code='hotel'), 'bellboy',           'พนักงานยกกระเป๋า (เบลบอย)',              3),
  ((SELECT id FROM job_categories WHERE code='hotel'), 'concierge',         'พนักงานต้อนรับ/คอนเซียร์จ',              4),
  ((SELECT id FROM job_categories WHERE code='hotel'), 'doorman',           'พนักงานเปิดประตู',                       5),
  ((SELECT id FROM job_categories WHERE code='hotel'), 'room_service',      'พนักงานรูมเซอร์วิส',                     6),
  ((SELECT id FROM job_categories WHERE code='hotel'), 'steward',           'สจ๊วต/พนักงานล้างครัวโรงแรม',            7),
  ((SELECT id FROM job_categories WHERE code='hotel'), 'banquet_staff',     'พนักงานจัดเลี้ยง',                       8),
  ((SELECT id FROM job_categories WHERE code='hotel'), 'pool_attendant',    'พนักงานดูแลสระว่ายน้ำ',                  9)
ON CONFLICT (code) DO NOTHING;

-- ตรวจสอบ
SELECT c.code, c.name_th AS category, c.icon AS icon, COUNT(j.id) AS titles
FROM   job_categories c
LEFT   JOIN job_titles j ON j.category_id = c.id
WHERE  c.code = 'hotel'
GROUP  BY c.id, c.code, c.name_th, c.icon;
