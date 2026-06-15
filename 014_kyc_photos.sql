-- Migration 014: KYC Photo columns
-- Run in Supabase SQL Editor

ALTER TABLE worker_profiles
  ADD COLUMN IF NOT EXISTS face_photo_url     TEXT,
  ADD COLUMN IF NOT EXISTS id_card_photo_url  TEXT,
  ADD COLUMN IF NOT EXISTS kyc_submitted_at   TIMESTAMPTZ;  -- already exists from 010, IF NOT EXISTS safe
