-- ============================================================
--  Daily Wage Matchmaking Platform — BKK MVP
--  วิธีใช้: ก๊อปทั้งหมด → วางใน Supabase SQL Editor → Run
-- ============================================================


-- ============================================================
--  PART 1: EXTENSIONS
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS postgis;


-- ============================================================
--  PART 2: CORE TABLES
-- ============================================================

CREATE TABLE users (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email         VARCHAR(255) UNIQUE NOT NULL,
    phone         VARCHAR(20)  UNIQUE,
    password_hash TEXT         NOT NULL,
    role          VARCHAR(20)  NOT NULL CHECK (role IN ('worker', 'employer', 'admin')),
    is_active     BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE worker_profiles (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id                 UUID         NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    full_name               VARCHAR(100) NOT NULL,
    national_id             VARCHAR(20)  UNIQUE,
    skills                  TEXT[]       NOT NULL DEFAULT '{}',
    experience_years        INT          NOT NULL DEFAULT 0 CHECK (experience_years >= 0),
    daily_rate_expected     DECIMAL(10,2),
    background_check_status VARCHAR(20)  NOT NULL DEFAULT 'pending'
                            CHECK (background_check_status IN ('pending','verified','failed','expired')),
    background_checked_at   TIMESTAMPTZ,
    location                GEOGRAPHY(POINT, 4326),
    location_name           VARCHAR(255),
    profile_image_url       TEXT,
    is_available            BOOLEAN      NOT NULL DEFAULT TRUE,
    updated_at              TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE employer_profiles (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID         NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    company_name    VARCHAR(200) NOT NULL,
    business_type   VARCHAR(100),
    contact_person  VARCHAR(100) NOT NULL,
    verified_status VARCHAR(20)  NOT NULL DEFAULT 'unverified'
                    CHECK (verified_status IN ('unverified','verified','suspended')),
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE zones (
    code        VARCHAR(30)    PRIMARY KEY,
    name_th     VARCHAR(100)   NOT NULL,
    name_en     VARCHAR(100)   NOT NULL,
    center_lat  DECIMAL(10,7)  NOT NULL,
    center_lng  DECIMAL(10,7)  NOT NULL,
    is_active   BOOLEAN        NOT NULL DEFAULT TRUE
);

CREATE TABLE job_postings (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employer_id     UUID          NOT NULL REFERENCES employer_profiles(id) ON DELETE CASCADE,
    title           VARCHAR(200)  NOT NULL,
    description     TEXT,
    required_skills TEXT[]        NOT NULL DEFAULT '{}',
    daily_wage_rate DECIMAL(10,2) NOT NULL CHECK (daily_wage_rate > 0),
    duration_days   INT           NOT NULL CHECK (duration_days > 0),
    slots_available INT           NOT NULL DEFAULT 1 CHECK (slots_available > 0),
    slots_filled    INT           NOT NULL DEFAULT 0,
    status          VARCHAR(20)   NOT NULL DEFAULT 'open'
                    CHECK (status IN ('draft','open','filled','closed','expired')),
    location        GEOGRAPHY(POINT, 4326) NOT NULL,
    location_name   VARCHAR(255),
    zone_name       VARCHAR(30)   REFERENCES zones(code),
    start_date      DATE,
    expires_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    CONSTRAINT slots_check CHECK (slots_filled <= slots_available)
);

CREATE TABLE job_applications (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id         UUID          NOT NULL REFERENCES job_postings(id) ON DELETE CASCADE,
    worker_id      UUID          NOT NULL REFERENCES worker_profiles(id) ON DELETE CASCADE,
    status         VARCHAR(20)   NOT NULL DEFAULT 'matched'
                   CHECK (status IN ('matched','applied','shortlisted','hired','rejected','withdrawn')),
    match_score    DECIMAL(5,2),
    distance_km    DECIMAL(6,2),
    matched_skills TEXT[],
    employer_note  TEXT,
    applied_at     TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    decided_at     TIMESTAMPTZ,
    UNIQUE (job_id, worker_id)
);

CREATE TABLE notifications (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id    UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type       VARCHAR(50) NOT NULL,
    title      VARCHAR(200) NOT NULL,
    body       TEXT,
    is_read    BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ============================================================
--  PART 3: REVIEW SYSTEM
-- ============================================================

CREATE TABLE review_tags (
    id          SMALLSERIAL  PRIMARY KEY,
    target_role VARCHAR(10)  NOT NULL CHECK (target_role IN ('worker','employer')),
    tag_key     VARCHAR(50)  NOT NULL UNIQUE,
    tag_label   VARCHAR(100) NOT NULL,
    is_positive BOOLEAN      NOT NULL DEFAULT TRUE,
    sort_order  SMALLINT     NOT NULL DEFAULT 0
);

CREATE TABLE reviews (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id UUID        NOT NULL REFERENCES job_applications(id) ON DELETE CASCADE,
    reviewer_id    UUID        NOT NULL REFERENCES users(id),
    reviewee_id    UUID        NOT NULL REFERENCES users(id),
    reviewer_role  VARCHAR(10) NOT NULL CHECK (reviewer_role IN ('worker','employer')),
    is_visible     BOOLEAN     NOT NULL DEFAULT FALSE,
    would_rehire   BOOLEAN,
    comment        TEXT,
    submitted_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    revealed_at    TIMESTAMPTZ,
    UNIQUE (application_id, reviewer_id)
);

CREATE TABLE review_tag_selections (
    review_id UUID     NOT NULL REFERENCES reviews(id) ON DELETE CASCADE,
    tag_id    SMALLINT NOT NULL REFERENCES review_tags(id),
    PRIMARY KEY (review_id, tag_id)
);

CREATE TABLE worker_review_summary (
    worker_id        UUID         PRIMARY KEY REFERENCES worker_profiles(id) ON DELETE CASCADE,
    total_reviews    INT          NOT NULL DEFAULT 0,
    would_rehire_pct DECIMAL(5,2),
    avg_score        DECIMAL(4,2),
    top_tags         TEXT[]       NOT NULL DEFAULT '{}',
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE employer_review_summary (
    employer_id   UUID         PRIMARY KEY REFERENCES employer_profiles(id) ON DELETE CASCADE,
    total_reviews INT          NOT NULL DEFAULT 0,
    avg_score     DECIMAL(4,2),
    top_tags      TEXT[]       NOT NULL DEFAULT '{}',
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);


-- ============================================================
--  PART 4: INDEXES
-- ============================================================

CREATE INDEX idx_job_postings_location    ON job_postings     USING GIST (location);
CREATE INDEX idx_worker_location          ON worker_profiles  USING GIST (location);
CREATE INDEX idx_job_status               ON job_postings     (status);
CREATE INDEX idx_job_zone                 ON job_postings     (zone_name);
CREATE INDEX idx_job_employer             ON job_postings     (employer_id);
CREATE INDEX idx_worker_skills            ON worker_profiles  USING GIN  (skills);
CREATE INDEX idx_job_required_skills      ON job_postings     USING GIN  (required_skills);
CREATE INDEX idx_applications_job         ON job_applications (job_id);
CREATE INDEX idx_applications_worker      ON job_applications (worker_id);
CREATE INDEX idx_applications_status      ON job_applications (status);
CREATE INDEX idx_notifications_user       ON notifications    (user_id, is_read);
CREATE INDEX idx_reviews_application      ON reviews          (application_id);
CREATE INDEX idx_reviews_reviewee         ON reviews          (reviewee_id);
CREATE INDEX idx_reviews_visible          ON reviews          (is_visible, revealed_at);
CREATE INDEX idx_tag_selections_tag       ON review_tag_selections (tag_id);


-- ============================================================
--  PART 5: FUNCTIONS & TRIGGERS
-- ============================================================

-- auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_worker_profile_updated
    BEFORE UPDATE ON worker_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- reveal reviews เมื่อทั้งคู่ส่งแล้ว หรือครบ 7 วัน
CREATE OR REPLACE FUNCTION reveal_completed_reviews()
RETURNS void AS $$
DECLARE
    app_rec RECORD;
BEGIN
    FOR app_rec IN
        SELECT DISTINCT r.application_id
        FROM   reviews r
        WHERE  r.is_visible = FALSE
          AND  (
                  (SELECT COUNT(*) FROM reviews r2
                   WHERE r2.application_id = r.application_id) >= 2
                  OR
                  r.submitted_at < NOW() - INTERVAL '7 days'
               )
    LOOP
        UPDATE reviews
        SET    is_visible  = TRUE,
               revealed_at = NOW()
        WHERE  application_id = app_rec.application_id
          AND  is_visible = FALSE;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- คำนวณ summary ของ worker
CREATE OR REPLACE FUNCTION refresh_worker_summary(p_worker_user_id UUID)
RETURNS void AS $$
DECLARE
    v_worker_id      UUID;
    v_total          INT;
    v_rehire_count   INT;
    v_positive_tags  INT;
    v_total_tags     INT;
    v_avg_score      DECIMAL(4,2);
    v_rehire_pct     DECIMAL(5,2);
    v_top_tags       TEXT[];
BEGIN
    SELECT id INTO v_worker_id
    FROM   worker_profiles WHERE user_id = p_worker_user_id;
    IF v_worker_id IS NULL THEN RETURN; END IF;

    SELECT
        COUNT(DISTINCT r.id),
        COUNT(DISTINCT r.id) FILTER (WHERE r.would_rehire = TRUE)
    INTO v_total, v_rehire_count
    FROM reviews r
    WHERE r.reviewee_id   = p_worker_user_id
      AND r.is_visible    = TRUE
      AND r.reviewer_role = 'employer';

    IF v_total = 0 THEN RETURN; END IF;

    SELECT
        COUNT(*) FILTER (WHERE rt.is_positive = TRUE),
        COUNT(*)
    INTO v_positive_tags, v_total_tags
    FROM   review_tag_selections rts
    JOIN   reviews     r  ON r.id  = rts.review_id
    JOIN   review_tags rt ON rt.id = rts.tag_id
    WHERE  r.reviewee_id   = p_worker_user_id
      AND  r.is_visible    = TRUE
      AND  r.reviewer_role = 'employer';

    v_avg_score  := CASE WHEN v_total_tags > 0
                         THEN ROUND((v_positive_tags::DECIMAL / v_total_tags) * 5, 2)
                         ELSE NULL END;
    v_rehire_pct := ROUND((v_rehire_count::DECIMAL / v_total) * 100, 2);

    SELECT ARRAY_AGG(tag_key ORDER BY cnt DESC)
    INTO   v_top_tags
    FROM (
        SELECT rt.tag_key, COUNT(*) AS cnt
        FROM   review_tag_selections rts
        JOIN   reviews     r  ON r.id  = rts.review_id
        JOIN   review_tags rt ON rt.id = rts.tag_id
        WHERE  r.reviewee_id  = p_worker_user_id
          AND  r.is_visible   = TRUE
          AND  rt.is_positive = TRUE
        GROUP  BY rt.tag_key
        LIMIT  3
    ) t;

    INSERT INTO worker_review_summary
        (worker_id, total_reviews, would_rehire_pct, avg_score, top_tags, updated_at)
    VALUES
        (v_worker_id, v_total, v_rehire_pct, v_avg_score, COALESCE(v_top_tags,'{}'), NOW())
    ON CONFLICT (worker_id) DO UPDATE SET
        total_reviews    = EXCLUDED.total_reviews,
        would_rehire_pct = EXCLUDED.would_rehire_pct,
        avg_score        = EXCLUDED.avg_score,
        top_tags         = EXCLUDED.top_tags,
        updated_at       = EXCLUDED.updated_at;
END;
$$ LANGUAGE plpgsql;

-- trigger: หลัง reveal → refresh summary อัตโนมัติ
CREATE OR REPLACE FUNCTION trg_after_reveal()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.is_visible = TRUE AND OLD.is_visible = FALSE THEN
        PERFORM refresh_worker_summary(NEW.reviewee_id);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_review_revealed
    AFTER UPDATE OF is_visible ON reviews
    FOR EACH ROW EXECUTE FUNCTION trg_after_reveal();


-- ============================================================
--  PART 6: SEED DATA
-- ============================================================

-- Zones (BKK MVP)
INSERT INTO zones (code, name_th, name_en, center_lat, center_lng) VALUES
  ('TH-BKK-LATKRABANG', 'ลาดกระบัง',  'Lat Krabang', 13.7244, 100.7501),
  ('TH-BKK-BANGPLEE',   'บางพลี',      'Bang Phli',   13.6127, 100.7018),
  ('TH-BKK-BANGCHAN',   'บางชัน',      'Bang Chan',   13.7822, 100.8122),
  ('TH-BKK-MINBURI',    'มีนบุรี',      'Min Buri',    13.8059, 100.8473),
  ('TH-BKK-BANGNA',     'บางนา',       'Bang Na',     13.6672, 100.6011),
  ('TH-BKK-PRAWET',     'ประเวศ',       'Prawet',      13.7200, 100.6600),
  ('TH-BKK-ONNUT',      'อ่อนนุช',      'On Nut',      13.7018, 100.6011);

-- Review tags — worker
INSERT INTO review_tags (target_role, tag_key, tag_label, is_positive, sort_order) VALUES
  ('worker', 'on_time',       'ตรงเวลา',        TRUE,  1),
  ('worker', 'hardworking',   'ขยัน',            TRUE,  2),
  ('worker', 'follows_instr', 'ทำตามคำสั่ง',     TRUE,  3),
  ('worker', 'skilled',       'ทักษะตรงงาน',     TRUE,  4),
  ('worker', 'communicates',  'สื่อสารดี',        TRUE,  5),
  ('worker', 'responsible',   'รับผิดชอบ',        TRUE,  6),
  ('worker', 'late',          'มาสาย',           FALSE, 7),
  ('worker', 'slow',          'ทำงานช้า',         FALSE, 8),
  ('worker', 'needs_reteach', 'ต้องสอนซ้ำ',       FALSE, 9);

-- Review tags — employer
INSERT INTO review_tags (target_role, tag_key, tag_label, is_positive, sort_order) VALUES
  ('employer', 'pays_on_time',  'จ่ายตรงเวลา',   TRUE,  1),
  ('employer', 'good_env',      'สภาพแวดล้อมดี', TRUE,  2),
  ('employer', 'has_equipment', 'อุปกรณ์ครบ',     TRUE,  3),
  ('employer', 'clear_comms',   'สื่อสารชัดเจน',  TRUE,  4),
  ('employer', 'has_shelter',   'มีที่พัก',        TRUE,  5),
  ('employer', 'safe',          'ปลอดภัย',        TRUE,  6),
  ('employer', 'late_payment',  'จ่ายช้า',        FALSE, 7),
  ('employer', 'overwork',      'งานเกินที่ตกลง', FALSE, 8),
  ('employer', 'bad_env',       'สภาพแวดล้อมแย่', FALSE, 9);


-- ============================================================
--  เสร็จแล้ว — ตรวจสอบด้วย query นี้
-- ============================================================

SELECT table_name
FROM   information_schema.tables
WHERE  table_schema = 'public'
ORDER  BY table_name;
