-- ============================================================
-- Daily Wage Matchmaking Platform — Review System
-- Migration: 003_review_system.sql
-- ต่อจาก 001_init_schema.sql + 002_seed_zones.sql
-- ============================================================

-- ============================================================
-- ENUM-style reference: tag definitions
-- แยก table ไว้ เพื่อง่ายต่อการเพิ่ม tag ในอนาคต
-- ============================================================

CREATE TABLE review_tags (
    id          SMALLSERIAL PRIMARY KEY,
    target_role VARCHAR(10)  NOT NULL CHECK (target_role IN ('worker', 'employer')),
    tag_key     VARCHAR(50)  NOT NULL UNIQUE,   -- machine key  e.g. 'on_time'
    tag_label   VARCHAR(100) NOT NULL,          -- display text e.g. 'ตรงเวลา'
    is_positive BOOLEAN      NOT NULL DEFAULT TRUE,
    sort_order  SMALLINT     NOT NULL DEFAULT 0
);

-- Tags สำหรับประเมิน Worker (hirer ใช้)
INSERT INTO review_tags (target_role, tag_key, tag_label, is_positive, sort_order) VALUES
  ('worker', 'on_time',       'ตรงเวลา',          TRUE,  1),
  ('worker', 'hardworking',   'ขยัน',              TRUE,  2),
  ('worker', 'follows_instr', 'ทำตามคำสั่ง',       TRUE,  3),
  ('worker', 'skilled',       'ทักษะตรงงาน',       TRUE,  4),
  ('worker', 'communicates',  'สื่อสารดี',          TRUE,  5),
  ('worker', 'responsible',   'รับผิดชอบ',          TRUE,  6),
  ('worker', 'late',          'มาสาย',             FALSE, 7),
  ('worker', 'slow',          'ทำงานช้า',           FALSE, 8),
  ('worker', 'needs_reteach', 'ต้องสอนซ้ำ',         FALSE, 9);

-- Tags สำหรับประเมิน Employer (worker ใช้)
INSERT INTO review_tags (target_role, tag_key, tag_label, is_positive, sort_order) VALUES
  ('employer', 'pays_on_time',  'จ่ายตรงเวลา',     TRUE,  1),
  ('employer', 'good_env',      'สภาพแวดล้อมดี',   TRUE,  2),
  ('employer', 'has_equipment', 'อุปกรณ์ครบ',       TRUE,  3),
  ('employer', 'clear_comms',   'สื่อสารชัดเจน',    TRUE,  4),
  ('employer', 'has_shelter',   'มีที่พัก',          TRUE,  5),
  ('employer', 'safe',          'ปลอดภัย',          TRUE,  6),
  ('employer', 'late_payment',  'จ่ายช้า',          FALSE, 7),
  ('employer', 'overwork',      'งานเกินที่ตกลง',   FALSE, 8),
  ('employer', 'bad_env',       'สภาพแวดล้อมแย่',   FALSE, 9);

-- ============================================================
-- REVIEWS table
-- ============================================================

CREATE TABLE reviews (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- ผูกกับ application (1 งาน = max 2 reviews: worker→employer, employer→worker)
    application_id   UUID        NOT NULL REFERENCES job_applications(id) ON DELETE CASCADE,

    reviewer_id      UUID        NOT NULL REFERENCES users(id),
    reviewee_id      UUID        NOT NULL REFERENCES users(id),

    -- reviewer คือใคร
    reviewer_role    VARCHAR(10) NOT NULL CHECK (reviewer_role IN ('worker', 'employer')),

    -- Blind review: ซ่อนจนกว่าทั้งคู่ส่งแล้ว หรือครบ 7 วัน
    is_visible       BOOLEAN     NOT NULL DEFAULT FALSE,

    -- "จะรับอีกไหม?" — hirer ตอบ, worker ไม่มีช่องนี้
    would_rehire     BOOLEAN,

    comment          TEXT,                          -- optional, max enforce ใน app layer
    submitted_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    revealed_at      TIMESTAMPTZ,                  -- เวลาที่ระบบเปิดเผย

    UNIQUE (application_id, reviewer_id)           -- 1 คน = 1 review ต่องาน
);

-- ============================================================
-- REVIEW_TAG_SELECTIONS — junction: review ↔ tags ที่เลือก
-- ============================================================

CREATE TABLE review_tag_selections (
    review_id  UUID     NOT NULL REFERENCES reviews(id) ON DELETE CASCADE,
    tag_id     SMALLINT NOT NULL REFERENCES review_tags(id),
    PRIMARY KEY (review_id, tag_id)
);

-- ============================================================
-- WORKER_REVIEW_SUMMARY — denormalized cache สำหรับแสดงบน profile
-- อัปเดตด้วย trigger ทุกครั้งที่ review ถูก reveal
-- ============================================================

CREATE TABLE worker_review_summary (
    worker_id        UUID PRIMARY KEY REFERENCES worker_profiles(id) ON DELETE CASCADE,
    total_reviews    INT          NOT NULL DEFAULT 0,
    would_rehire_pct DECIMAL(5,2),              -- % ที่บอก "รับอีกแน่นอน"
    avg_score        DECIMAL(4,2),              -- คำนวณจาก positive_tags / total_tags
    top_tags         TEXT[]       NOT NULL DEFAULT '{}',  -- top 3 tag_key
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- ============================================================
-- EMPLOYER_REVIEW_SUMMARY — เช่นเดียวกันสำหรับ employer
-- ============================================================

CREATE TABLE employer_review_summary (
    employer_id      UUID PRIMARY KEY REFERENCES employer_profiles(id) ON DELETE CASCADE,
    total_reviews    INT          NOT NULL DEFAULT 0,
    avg_score        DECIMAL(4,2),
    top_tags         TEXT[]       NOT NULL DEFAULT '{}',
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- ============================================================
-- INDEXES
-- ============================================================

CREATE INDEX idx_reviews_application  ON reviews (application_id);
CREATE INDEX idx_reviews_reviewee     ON reviews (reviewee_id);
CREATE INDEX idx_reviews_visible      ON reviews (is_visible, revealed_at);
CREATE INDEX idx_tag_selections_tag   ON review_tag_selections (tag_id);

-- ============================================================
-- FUNCTION: reveal reviews เมื่อทั้งคู่ส่งแล้ว หรือ timeout
-- เรียกจาก cron job / Supabase pg_cron ทุก 1 ชั่วโมง
-- ============================================================

CREATE OR REPLACE FUNCTION reveal_completed_reviews()
RETURNS void AS $$
DECLARE
    app_rec RECORD;
BEGIN
    -- หา application ที่ review ยังไม่ถูกเปิดเผย
    FOR app_rec IN
        SELECT DISTINCT r.application_id
        FROM   reviews r
        WHERE  r.is_visible = FALSE
          AND  (
                  -- ทั้งสองฝั่งส่งแล้ว
                  (SELECT COUNT(*) FROM reviews r2
                   WHERE r2.application_id = r.application_id) >= 2
                  OR
                  -- ครบ 7 วันแล้ว ส่งแค่ฝั่งเดียวก็เปิด
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

-- ============================================================
-- FUNCTION: คำนวณ summary score จาก positive tags
-- score = positive_tag_count / total_tag_count * 5  (scale 0–5)
-- ============================================================

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
    WHERE r.reviewee_id = p_worker_user_id
      AND r.is_visible  = TRUE
      AND r.reviewer_role = 'employer';

    IF v_total = 0 THEN RETURN; END IF;

    -- positive tag ratio → score 0–5
    SELECT
        COUNT(*) FILTER (WHERE rt.is_positive = TRUE),
        COUNT(*)
    INTO v_positive_tags, v_total_tags
    FROM   review_tag_selections rts
    JOIN   reviews     r  ON r.id  = rts.review_id
    JOIN   review_tags rt ON rt.id = rts.tag_id
    WHERE  r.reviewee_id    = p_worker_user_id
      AND  r.is_visible     = TRUE
      AND  r.reviewer_role  = 'employer';

    v_avg_score  := CASE WHEN v_total_tags > 0
                         THEN ROUND((v_positive_tags::DECIMAL / v_total_tags) * 5, 2)
                         ELSE NULL END;
    v_rehire_pct := ROUND((v_rehire_count::DECIMAL / v_total) * 100, 2);

    -- top 3 tags ที่ถูกเลือกบ่อยที่สุด
    SELECT ARRAY_AGG(tag_key ORDER BY cnt DESC)
    INTO   v_top_tags
    FROM (
        SELECT rt.tag_key, COUNT(*) AS cnt
        FROM   review_tag_selections rts
        JOIN   reviews     r  ON r.id  = rts.review_id
        JOIN   review_tags rt ON rt.id = rts.tag_id
        WHERE  r.reviewee_id   = p_worker_user_id
          AND  r.is_visible    = TRUE
          AND  rt.is_positive  = TRUE
        GROUP  BY rt.tag_key
        LIMIT  3
    ) t;

    INSERT INTO worker_review_summary
        (worker_id, total_reviews, would_rehire_pct, avg_score, top_tags, updated_at)
    VALUES
        (v_worker_id, v_total, v_rehire_pct, v_avg_score, COALESCE(v_top_tags, '{}'), NOW())
    ON CONFLICT (worker_id) DO UPDATE SET
        total_reviews    = EXCLUDED.total_reviews,
        would_rehire_pct = EXCLUDED.would_rehire_pct,
        avg_score        = EXCLUDED.avg_score,
        top_tags         = EXCLUDED.top_tags,
        updated_at       = EXCLUDED.updated_at;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- TRIGGER: หลัง reveal → refresh summary อัตโนมัติ
-- ============================================================

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
-- pg_cron: ตั้ง job reveal ทุก 1 ชั่วโมง (Supabase รองรับ)
-- uncomment เมื่อ enable pg_cron extension บน Supabase dashboard
-- ============================================================

-- SELECT cron.schedule(
--     'reveal-reviews-hourly',
--     '0 * * * *',
--     'SELECT reveal_completed_reviews()'
-- );

COMMENT ON TABLE reviews IS
    'Blind review system: is_visible=FALSE จนกว่าทั้งคู่ส่ง หรือครบ 7 วัน';
COMMENT ON COLUMN reviews.would_rehire IS
    'เฉพาะ reviewer_role=employer เท่านั้นที่ตอบช่องนี้';
COMMENT ON TABLE worker_review_summary IS
    'Denormalized cache — อย่า query ตรงจาก reviews table สำหรับแสดงบน profile';
