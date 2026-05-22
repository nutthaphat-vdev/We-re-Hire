-- ============================================================
-- WeHire Migration: 006_trust_safety.sql
-- Report & Block system
-- ============================================================

-- รายงานผู้ใช้
CREATE TABLE IF NOT EXISTS user_reports (
    id               UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    reporter_id      UUID         NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reported_user_id UUID         NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reason           VARCHAR(30)  NOT NULL
                     CHECK (reason IN ('spam','fake','harassment','payment_fraud','other')),
    detail           TEXT,
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (reporter_id, reported_user_id, reason)
);

-- บล็อคผู้ใช้
CREATE TABLE IF NOT EXISTS user_blocks (
    blocker_id      UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    blocked_user_id UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (blocker_id, blocked_user_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_reports_reported  ON user_reports (reported_user_id);
CREATE INDEX IF NOT EXISTS idx_reports_reporter  ON user_reports (reporter_id);
CREATE INDEX IF NOT EXISTS idx_blocks_blocker    ON user_blocks  (blocker_id);
CREATE INDEX IF NOT EXISTS idx_blocks_blocked    ON user_blocks  (blocked_user_id);

-- Filter blocked users ออกจาก job nearby query (RLS-style)
-- เอาไปใช้ใน app layer ได้เลย:
-- WHERE jp.employer_id NOT IN (SELECT ep.id FROM employer_profiles ep
--   JOIN user_blocks ub ON ub.blocked_user_id = ep.user_id
--   WHERE ub.blocker_id = $current_user_id)

-- ตรวจสอบ
SELECT 'user_reports' AS tbl, COUNT(*) FROM user_reports
UNION ALL
SELECT 'user_blocks',          COUNT(*) FROM user_blocks;
