-- Migration 009: Add disputed status for incomplete jobs
ALTER TABLE job_applications
  DROP CONSTRAINT IF EXISTS job_applications_status_check;

ALTER TABLE job_applications
  ADD CONSTRAINT job_applications_status_check
    CHECK (status IN (
      'matched','applied','shortlisted',
      'hired','checked_in','working','completed','verified',
      'disputed','rejected','withdrawn'
    ));
