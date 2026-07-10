-- Migration 022: Add text-based address fields to worker_profiles
-- Replaces map/pin location input with simpler text fields for daily workers.
-- location column (GEOGRAPHY) left intact — still used for Find Jobs GPS matching.

ALTER TABLE worker_profiles
  ADD COLUMN IF NOT EXISTS address_text TEXT,
  ADD COLUMN IF NOT EXISTS province     VARCHAR(50),
  ADD COLUMN IF NOT EXISTS postal_code  VARCHAR(10);
