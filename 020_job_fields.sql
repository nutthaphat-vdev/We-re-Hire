-- Migration 020: Employer job fields — pay method, contact, dress code
-- Idempotent: ADD COLUMN IF NOT EXISTS (safe to re-run)

ALTER TABLE job_postings
  ADD COLUMN IF NOT EXISTS pay_method   VARCHAR(30),
  ADD COLUMN IF NOT EXISTS contact_info TEXT,
  ADD COLUMN IF NOT EXISTS dress_code   VARCHAR(200);

COMMENT ON COLUMN job_postings.pay_method   IS 'วิธีจ่ายเงิน เช่น cash_shift / transfer_daily / other';
COMMENT ON COLUMN job_postings.contact_info IS 'ผู้ติดต่อหน้างาน + จุดสังเกต — แสดงเฉพาะ hired+ (contact lock)';
COMMENT ON COLUMN job_postings.dress_code   IS 'ข้อกำหนดการแต่งกาย เช่น smart_casual / work_clothes / uniform_provided';
