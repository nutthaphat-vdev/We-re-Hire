-- ============================================================
-- 023_job_time_range.sql
-- Central helper: แปลง "งาน" เป็นช่วงเวลาจริง (tsrange) เพื่อตรวจการทับซ้อน
-- ใช้ร่วมกันทุกที่: decide (guard + withdraw), apply-guard, matching filter
-- ------------------------------------------------------------
-- นิยาม "ช่วงที่งานกินเวลา" (occupied interval):
--   • งานหลายวัน (duration > 1)      → ล็อกทั้งสแปน (ทุกวัน) ไม่สนเวลา  = exclusive
--   • งานวันเดียว ข้ามเที่ยงคืน       → end เลื่อนไปวันถัดไป (+1 วัน)
--   • งานวันเดียว ปกติ                → [start+work_start, start+work_end]
--
-- tsrange เป็น [ ) : ต้นชน / ปลายไม่นับ → งาน 09-12 กับ 12-15 = ไม่ทับ (back-to-back รับได้)
-- IMMUTABLE : ปลอดภัยกับ PgBouncer + prepared-statement-off (statement_cache_size=0)
-- ============================================================

CREATE OR REPLACE FUNCTION job_occupied_range(
    p_start_date  DATE,
    p_duration    INT,
    p_work_start  TIME,
    p_work_end    TIME
) RETURNS tsrange
LANGUAGE sql
IMMUTABLE
AS $$
    SELECT CASE
        -- หลายวัน: บล็อกทั้งช่วง (00:00 วันแรก → 00:00 วันถัดจากวันสุดท้าย)
        WHEN COALESCE(p_duration, 1) > 1 THEN
            tsrange(
                p_start_date::timestamp,
                (p_start_date + COALESCE(p_duration, 1))::timestamp
            )
        -- วันเดียว + ข้ามเที่ยงคืน (work_end <= work_start): จบวันถัดไป
        WHEN COALESCE(p_work_end, TIME '23:59:59') <= COALESCE(p_work_start, TIME '00:00') THEN
            tsrange(
                p_start_date + COALESCE(p_work_start, TIME '00:00'),
                (p_start_date + 1) + COALESCE(p_work_end, TIME '23:59:59')
            )
        -- วันเดียว + ปกติ
        ELSE
            tsrange(
                p_start_date + COALESCE(p_work_start, TIME '00:00'),
                p_start_date + COALESCE(p_work_end, TIME '23:59:59')
            )
    END;
$$;

COMMENT ON FUNCTION job_occupied_range(DATE, INT, TIME, TIME) IS
    'ช่วงเวลาจริงที่งานกินเวลา (tsrange). หลายวัน=เต็มสแปน, ข้ามคืน=+1วัน, วันเดียว=ตามเวลา. ใช้ && ตรวจการทับ.';


-- ============================================================
-- ✅ VERIFICATION — run แล้วผลควรตรงคอมเมนต์ (ไม่กระทบข้อมูล ลบทิ้งได้)
-- ============================================================

-- 1) วันเดียวปกติ: A(08-12) vs B(09-13) → ควรทับ = t
SELECT 'A08-12 vs B09-13 (ควร t)' AS test,
       job_occupied_range(DATE '2026-07-20', 1, TIME '08:00', TIME '12:00')
    && job_occupied_range(DATE '2026-07-20', 1, TIME '09:00', TIME '13:00') AS overlaps;

-- 2) back-to-back: 09-12 vs 12-15 → ไม่ควรทับ = f
SELECT 'B2B 09-12 vs 12-15 (ควร f)' AS test,
       job_occupied_range(DATE '2026-07-20', 1, TIME '09:00', TIME '12:00')
    && job_occupied_range(DATE '2026-07-20', 1, TIME '12:00', TIME '15:00') AS overlaps;

-- 3) คนละวัน วันเดียว: 09-13 (20 ก.ค.) vs 09-13 (21 ก.ค.) → ไม่ทับ = f
SELECT 'คนละวัน (ควร f)' AS test,
       job_occupied_range(DATE '2026-07-20', 1, TIME '09:00', TIME '13:00')
    && job_occupied_range(DATE '2026-07-21', 1, TIME '09:00', TIME '13:00') AS overlaps;

-- 4) ข้ามเที่ยงคืน: X 22:00-02:00 (20 ก.ค.) vs Y 01:00-05:00 (21 ก.ค.) → ควรทับ = t
SELECT 'ข้ามคืน X22-02 vs Y01-05 (ควร t)' AS test,
       job_occupied_range(DATE '2026-07-20', 1, TIME '22:00', TIME '02:00')
    && job_occupied_range(DATE '2026-07-21', 1, TIME '01:00', TIME '05:00') AS overlaps;

-- 5) ข้ามคืนไม่ชน: X 22:00-02:00 (20 ก.ค.) vs Z 06:00-10:00 (21 ก.ค.) → ไม่ทับ = f
SELECT 'ข้ามคืน X22-02 vs Z06-10 (ควร f)' AS test,
       job_occupied_range(DATE '2026-07-20', 1, TIME '22:00', TIME '02:00')
    && job_occupied_range(DATE '2026-07-21', 1, TIME '06:00', TIME '10:00') AS overlaps;

-- 6) หลายวันบล็อกทั้งสแปน: งาน 3 วัน 09-13 (20-22 ก.ค.) vs งานวันเดียว 15-18 (21 ก.ค.)
--    เวลาไม่ชน แต่หลายวัน = ล็อกทั้งวัน → ควรทับ = t
SELECT 'หลายวัน 3วัน vs วันเดียวแทรก (ควร t)' AS test,
       job_occupied_range(DATE '2026-07-20', 3, TIME '09:00', TIME '13:00')
    && job_occupied_range(DATE '2026-07-21', 1, TIME '15:00', TIME '18:00') AS overlaps;

-- 7) หลายวัน vs งานนอกสแปน: งาน 3 วัน (20-22) vs วันเดียว (25 ก.ค.) → ไม่ทับ = f
SELECT 'หลายวัน vs นอกสแปน (ควร f)' AS test,
       job_occupied_range(DATE '2026-07-20', 3, TIME '09:00', TIME '13:00')
    && job_occupied_range(DATE '2026-07-25', 1, TIME '09:00', TIME '13:00') AS overlaps;


-- ============================================================
-- ROLLBACK (ถ้าต้องถอน):
--   DROP FUNCTION IF EXISTS job_occupied_range(DATE, INT, TIME, TIME);
-- ============================================================
