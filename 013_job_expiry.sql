-- Migration 013: Job Auto-Close
-- Run in Supabase SQL Editor

ALTER TABLE job_postings
  ADD COLUMN IF NOT EXISTS auto_close_at       TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS auto_closed_reason  VARCHAR(20)
    CHECK (auto_closed_reason IN ('no_applicants', 'no_hire', 'manual'));

CREATE INDEX IF NOT EXISTS idx_job_auto_close
  ON job_postings (auto_close_at, status)
  WHERE status = 'open';
