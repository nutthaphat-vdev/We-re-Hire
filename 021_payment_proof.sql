-- Migration 021: Payment Proof Flow
-- Run in Supabase SQL Editor BEFORE deploying backend changes

ALTER TABLE job_applications
  ADD COLUMN IF NOT EXISTS paid_amount              DECIMAL(10,2),
  ADD COLUMN IF NOT EXISTS pay_method_actual        VARCHAR(20),   -- cash | transfer
  ADD COLUMN IF NOT EXISTS slip_url                 TEXT,
  ADD COLUMN IF NOT EXISTS employer_paid_at         TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS worker_paid_confirmed_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS payment_status           VARCHAR(20) DEFAULT 'unpaid';

-- payment_status: unpaid | paid_pending | paid_confirmed | payment_disputed
-- pay_method_actual = วิธีที่จ่ายจริง (job_postings.pay_method = วิธีที่ตั้งใจ)

COMMENT ON COLUMN job_applications.payment_status       IS 'unpaid | paid_pending | paid_confirmed | payment_disputed';
COMMENT ON COLUMN job_applications.pay_method_actual    IS 'cash | transfer — actual method used at settlement';
