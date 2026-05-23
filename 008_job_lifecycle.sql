-- Migration 008: Job Lifecycle Flow
-- hired → checked_in → working → completed → verified → (review)

-- ขยาย status CHECK constraint
ALTER TABLE job_applications
  DROP CONSTRAINT IF EXISTS job_applications_status_check;

ALTER TABLE job_applications
  ADD CONSTRAINT job_applications_status_check
    CHECK (status IN (
      'matched','applied','shortlisted',
      'hired','checked_in','working','completed','verified',
      'rejected','withdrawn'
    ));

-- เพิ่ม lifecycle columns
ALTER TABLE job_applications
  ADD COLUMN IF NOT EXISTS checkin_at           TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS checkin_lat          DECIMAL(10,7),
  ADD COLUMN IF NOT EXISTS checkin_lng          DECIMAL(10,7),
  ADD COLUMN IF NOT EXISTS work_started_at      TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS work_ended_at        TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS employer_verified_at TIMESTAMPTZ;
