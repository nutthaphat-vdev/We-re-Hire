-- Migration 017: Behavioral Score System
-- วัดความน่าเชื่อถือของ worker จากพฤติกรรมจริง

ALTER TABLE worker_profiles
  ADD COLUMN IF NOT EXISTS reliability_score  DECIMAL(4,2)  DEFAULT 5.00,
  ADD COLUMN IF NOT EXISTS jobs_completed     INTEGER       DEFAULT 0,
  ADD COLUMN IF NOT EXISTS jobs_noshow        INTEGER       DEFAULT 0,
  ADD COLUMN IF NOT EXISTS jobs_hired         INTEGER       DEFAULT 0,
  ADD COLUMN IF NOT EXISTS score_updated_at   TIMESTAMPTZ;

-- สูตร: (completion_rate×5) + ((1-noshow_rate)×3) + (review_avg×2) → 0–10
CREATE OR REPLACE FUNCTION compute_reliability_score(
    p_completed INTEGER,
    p_noshow    INTEGER,
    p_hired     INTEGER,
    p_review_avg DECIMAL
) RETURNS DECIMAL(4,2) AS $$
DECLARE
    total           INTEGER;
    completion_rate DECIMAL;
    noshow_rate     DECIMAL;
    review_norm     DECIMAL;
BEGIN
    total := GREATEST(p_hired, 1);
    completion_rate := LEAST(p_completed::DECIMAL / total, 1.0);
    noshow_rate     := LEAST(p_noshow::DECIMAL    / total, 1.0);
    review_norm     := COALESCE(p_review_avg, 5.0) / 5.0;
    RETURN ROUND(
        (completion_rate * 5.0) +
        ((1.0 - noshow_rate) * 3.0) +
        (review_norm * 2.0),
    2);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

CREATE INDEX IF NOT EXISTS idx_worker_profiles_reliability
  ON worker_profiles(reliability_score DESC)
  WHERE reliability_score IS NOT NULL;

COMMENT ON COLUMN worker_profiles.reliability_score IS '0–10: (completion×5)+(no_noshow×3)+(review×2)';
COMMENT ON COLUMN worker_profiles.jobs_completed    IS 'นับเมื่อ status→verified';
COMMENT ON COLUMN worker_profiles.jobs_noshow       IS 'นับเมื่อ cron auto no-show';
COMMENT ON COLUMN worker_profiles.jobs_hired        IS 'นับเมื่อ decided_at SET (hired)';
