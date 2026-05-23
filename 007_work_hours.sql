-- Migration 007: เพิ่มช่วงเวลาทำงาน + OT ใน job_postings
ALTER TABLE job_postings
  ADD COLUMN IF NOT EXISTS work_start TIME,
  ADD COLUMN IF NOT EXISTS work_end   TIME,
  ADD COLUMN IF NOT EXISTS ot_rate    DECIMAL(8,2);
