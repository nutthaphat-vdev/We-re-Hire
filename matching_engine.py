"""
Daily Wage Matchmaking Platform — Matching Engine
Step 3: Core matching logic (geo-radius + skill filtering + scoring)

Stack: FastAPI + asyncpg (Supabase/PostgreSQL + PostGIS)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
import asyncpg

router = APIRouter()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DEFAULT_RADIUS_KM = 10.0
MAX_RADIUS_KM     = 30.0

# Scoring weights (must sum to 1.0)
W_SKILLS   = 0.60   # Skill match is the most important signal
W_DISTANCE = 0.25   # Closer = better
W_RATE     = 0.15   # Worker's expected rate vs job rate


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class ApplyRequest(BaseModel):
    lat: float = Field(..., ge=-90,  le=90)
    lng: float = Field(..., ge=-180, le=180)

class CandidateOut(BaseModel):
    application_id: UUID
    worker_id:      UUID
    full_name:      str
    matched_skills: list[str]
    missing_skills: list[str]
    match_score:    float           # 0–100
    distance_km:    float
    background_check_status: str
    daily_rate_expected: Optional[float]
    status:         str


# ---------------------------------------------------------------------------
# Dependency: DB connection
# ---------------------------------------------------------------------------

async def get_db() -> asyncpg.Connection:
    """
    In production: use a connection pool (asyncpg.create_pool).
    Supabase connection string from environment variable.
    """
    import os
    conn = await asyncpg.connect(os.environ["DATABASE_URL"])
    try:
        yield conn
    finally:
        await conn.close()


# ---------------------------------------------------------------------------
# Core matching function
# ---------------------------------------------------------------------------

def compute_match_score(
    worker_skills:    list[str],
    required_skills:  list[str],
    distance_km:      float,
    radius_km:        float,
    worker_rate:      Optional[float],
    job_rate:         float,
) -> tuple[float, list[str], list[str]]:
    """
    Returns (score_0_to_100, matched_skills, missing_skills)

    Scoring breakdown:
      - Skill score  (60%): what fraction of required skills worker has
      - Distance score (25%): linear decay — closer is better
      - Rate score   (15%): worker's expected rate vs job's offered rate
    """

    # --- Skill score ---
    required_set = set(s.lower() for s in required_skills)
    worker_set   = set(s.lower() for s in worker_skills)

    matched  = list(worker_set & required_set)
    missing  = list(required_set - worker_set)

    if required_set:
        skill_score = len(matched) / len(required_set)
    else:
        skill_score = 1.0   # No skills required = open to all

    # --- Distance score ---
    # Linear decay: 0 km → 1.0, radius_km → 0.0
    distance_score = max(0.0, 1.0 - (distance_km / radius_km))

    # --- Rate compatibility score ---
    if worker_rate and job_rate > 0:
        ratio = worker_rate / job_rate
        if ratio <= 1.0:
            rate_score = 1.0        # Worker expects ≤ job rate → perfect fit
        elif ratio <= 1.2:
            rate_score = 1.0 - ((ratio - 1.0) / 0.2)  # Slight premium → partial
        else:
            rate_score = 0.0        # Worker expects >20% above job rate
    else:
        rate_score = 0.5            # Unknown rate → neutral

    # --- Weighted total ---
    raw_score = (
        W_SKILLS   * skill_score   +
        W_DISTANCE * distance_score +
        W_RATE     * rate_score
    )

    final_score = round(raw_score * 100, 2)

    return final_score, [s.title() for s in matched], [s.title() for s in missing]


# ---------------------------------------------------------------------------
# POST /jobs/{job_id}/apply  — Worker applies
# ---------------------------------------------------------------------------

@router.post(
    "/jobs/{job_id}/apply",
    status_code=status.HTTP_201_CREATED,
    summary="Worker applies to a job (computes match score on the fly)",
)
async def apply_to_job(
    job_id:  UUID,
    body:    ApplyRequest,
    db:      asyncpg.Connection = Depends(get_db),
    # In production: current_user = Depends(get_current_worker)
    worker_id: UUID = None,   # Replace with auth dependency
):
    # 1. Fetch job (must be open, not expired, has slots)
    job = await db.fetchrow(
        """
        SELECT id, required_skills, daily_wage_rate, slots_available, slots_filled,
               status, expires_at,
               ST_X(location::geometry) AS lng,
               ST_Y(location::geometry) AS lat
        FROM   job_postings
        WHERE  id = $1
        """,
        job_id,
    )
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] != "open":
        raise HTTPException(status_code=409, detail="Job is no longer accepting applications")
    if job["slots_filled"] >= job["slots_available"]:
        raise HTTPException(status_code=409, detail="Job slots are full")

    # 2. Fetch worker profile
    worker = await db.fetchrow(
        """
        SELECT id, skills, daily_rate_expected, background_check_status
        FROM   worker_profiles
        WHERE  user_id = $1
        """,
        worker_id,
    )
    if not worker:
        raise HTTPException(status_code=404, detail="Worker profile not found")

    # 3. Compute distance (PostGIS, server-side — most accurate)
    distance_row = await db.fetchrow(
        """
        SELECT ST_Distance(
            ST_MakePoint($1, $2)::geography,
            location
        ) / 1000.0 AS distance_km
        FROM job_postings WHERE id = $3
        """,
        body.lng, body.lat, job_id,
    )
    distance_km = float(distance_row["distance_km"])

    if distance_km > MAX_RADIUS_KM:
        raise HTTPException(
            status_code=400,
            detail=f"Job is {distance_km:.1f} km away — exceeds {MAX_RADIUS_KM} km limit",
        )

    # 4. Compute match score
    score, matched_skills, missing_skills = compute_match_score(
        worker_skills   = worker["skills"] or [],
        required_skills = job["required_skills"] or [],
        distance_km     = distance_km,
        radius_km       = DEFAULT_RADIUS_KM,
        worker_rate     = worker["daily_rate_expected"],
        job_rate        = float(job["daily_wage_rate"]),
    )

    # 5. Upsert application record (idempotent — prevents duplicates)
    app = await db.fetchrow(
        """
        INSERT INTO job_applications
            (job_id, worker_id, status, match_score, distance_km, matched_skills)
        VALUES
            ($1, $2, 'applied', $3, $4, $5)
        ON CONFLICT (job_id, worker_id)
            DO UPDATE SET
                status        = 'applied',
                match_score   = EXCLUDED.match_score,
                distance_km   = EXCLUDED.distance_km,
                matched_skills= EXCLUDED.matched_skills,
                applied_at    = NOW()
        RETURNING id, status
        """,
        job_id,
        worker["id"],
        score,
        round(distance_km, 2),
        matched_skills,
    )

    # 6. Notify employer (insert notification row)
    await db.execute(
        """
        INSERT INTO notifications (user_id, type, title, body)
        SELECT ep.user_id, 'new_applicant',
               'มีผู้สมัครงานใหม่',
               'มีคนสมัครตำแหน่งที่คุณโพสต์ — คะแนน Match ' || $1 || '/100'
        FROM   job_postings jp
        JOIN   employer_profiles ep ON ep.id = jp.employer_id
        WHERE  jp.id = $2
        """,
        str(int(score)),
        job_id,
    )

    return {
        "application_id":  app["id"],
        "status":          app["status"],
        "match_score":     score,
        "distance_km":     round(distance_km, 2),
        "matched_skills":  matched_skills,
        "missing_skills":  missing_skills,
    }


# ---------------------------------------------------------------------------
# GET /jobs/nearby  — Worker scans jobs within radius
# ---------------------------------------------------------------------------

@router.get(
    "/jobs/nearby",
    summary="Find open jobs within radius, pre-filtered by worker skills",
)
async def get_nearby_jobs(
    lat:       float,
    lng:       float,
    radius_km: float = DEFAULT_RADIUS_KM,
    db:        asyncpg.Connection = Depends(get_db),
    worker_id: UUID  = None,   # Replace with auth dependency
):
    radius_km = min(radius_km, MAX_RADIUS_KM)

    # Fetch worker skills once
    worker = await db.fetchrow(
        "SELECT skills, daily_rate_expected FROM worker_profiles WHERE user_id = $1",
        worker_id,
    )
    worker_skills = worker["skills"] if worker else []
    worker_rate   = worker["daily_rate_expected"] if worker else None

    # Geo query: jobs within radius, ordered by distance
    # required_skills && $4 = "has at least one skill in common" (array overlap)
    rows = await db.fetch(
        """
        SELECT
            jp.id,
            jp.title,
            jp.required_skills,
            jp.daily_wage_rate,
            jp.duration_days,
            jp.slots_available - jp.slots_filled AS slots_remaining,
            jp.location_name,
            jp.start_date,
            ST_Distance(
                ST_MakePoint($1, $2)::geography,
                jp.location
            ) / 1000.0 AS distance_km
        FROM   job_postings jp
        WHERE  jp.status = 'open'
          AND  (jp.expires_at IS NULL OR jp.expires_at > NOW())
          AND  jp.slots_filled < jp.slots_available
          AND  ST_DWithin(
                   jp.location,
                   ST_MakePoint($1, $2)::geography,
                   $3 * 1000   -- metres
               )
          AND  (
                   jp.required_skills = '{}'          -- No skills required
                   OR jp.required_skills && $4        -- At least 1 skill matches
               )
        ORDER  BY distance_km ASC
        LIMIT  50
        """,
        lng, lat,
        radius_km,
        worker_skills,
    )

    results = []
    for row in rows:
        score, matched, missing = compute_match_score(
            worker_skills   = worker_skills,
            required_skills = row["required_skills"] or [],
            distance_km     = float(row["distance_km"]),
            radius_km       = radius_km,
            worker_rate     = worker_rate,
            job_rate        = float(row["daily_wage_rate"]),
        )
        results.append({
            "job_id":           row["id"],
            "title":            row["title"],
            "daily_wage_rate":  float(row["daily_wage_rate"]),
            "duration_days":    row["duration_days"],
            "slots_remaining":  row["slots_remaining"],
            "location_name":    row["location_name"],
            "start_date":       str(row["start_date"]) if row["start_date"] else None,
            "distance_km":      round(float(row["distance_km"]), 2),
            "match_score":      score,
            "matched_skills":   matched,
            "missing_skills":   missing,
        })

    # Sort by match score (desc), then distance (asc)
    results.sort(key=lambda x: (-x["match_score"], x["distance_km"]))
    return {"count": len(results), "jobs": results}


# ---------------------------------------------------------------------------
# GET /jobs/{job_id}/candidates  — Employer views ranked candidate list
# ---------------------------------------------------------------------------

@router.get(
    "/jobs/{job_id}/candidates",
    response_model=list[CandidateOut],
    summary="Employer sees ranked candidates for a job (human-in-the-loop)",
)
async def get_candidates(
    job_id: UUID,
    db:     asyncpg.Connection = Depends(get_db),
):
    rows = await db.fetch(
        """
        SELECT
            ja.id              AS application_id,
            wp.id              AS worker_id,
            wp.full_name,
            wp.background_check_status,
            wp.daily_rate_expected,
            ja.match_score,
            ja.distance_km,
            ja.matched_skills,
            ja.status,
            jp.required_skills
        FROM   job_applications ja
        JOIN   worker_profiles  wp ON wp.id   = ja.worker_id
        JOIN   job_postings     jp ON jp.id   = ja.job_id
        WHERE  ja.job_id = $1
          AND  ja.status IN ('applied', 'shortlisted')
        ORDER  BY ja.match_score DESC, ja.distance_km ASC
        """,
        job_id,
    )

    if not rows:
        return []

    return [
        CandidateOut(
            application_id           = row["application_id"],
            worker_id                = row["worker_id"],
            full_name                = row["full_name"],
            matched_skills           = row["matched_skills"] or [],
            missing_skills           = list(
                set(s.lower() for s in (row["required_skills"] or [])) -
                set(s.lower() for s in (row["matched_skills"] or []))
            ),
            match_score              = float(row["match_score"] or 0),
            distance_km              = float(row["distance_km"] or 0),
            background_check_status  = row["background_check_status"],
            daily_rate_expected      = float(row["daily_rate_expected"]) if row["daily_rate_expected"] else None,
            status                   = row["status"],
        )
        for row in rows
    ]


# ---------------------------------------------------------------------------
# PATCH /applications/{app_id}/decide  — Employer hires or rejects
# ---------------------------------------------------------------------------

class DecisionRequest(BaseModel):
    decision: str = Field(..., pattern="^(hired|rejected|shortlisted)$")
    note:     Optional[str] = Field(None, max_length=500)

@router.patch(
    "/applications/{app_id}/decide",
    summary="Employer makes final hiring decision (human-in-the-loop gate)",
)
async def decide_application(
    app_id:  UUID,
    body:    DecisionRequest,
    db:      asyncpg.Connection = Depends(get_db),
):
    # Fetch application + job slot info
    row = await db.fetchrow(
        """
        SELECT ja.id, ja.status, ja.job_id, ja.worker_id,
               jp.slots_available, jp.slots_filled
        FROM   job_applications ja
        JOIN   job_postings     jp ON jp.id = ja.job_id
        WHERE  ja.id = $1
        """,
        app_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Application not found")
    if row["status"] in ("hired", "rejected"):
        raise HTTPException(status_code=409, detail=f"Application already {row['status']}")

    if body.decision == "hired" and row["slots_filled"] >= row["slots_available"]:
        raise HTTPException(status_code=409, detail="No remaining slots for this job")

    async with db.transaction():
        # Update application status
        await db.execute(
            """
            UPDATE job_applications
            SET    status        = $1,
                   employer_note = $2,
                   decided_at   = NOW()
            WHERE  id = $3
            """,
            body.decision, body.note, app_id,
        )

        if body.decision == "hired":
            # Increment slots_filled; auto-close job if full
            await db.execute(
                """
                UPDATE job_postings
                SET    slots_filled = slots_filled + 1,
                       status = CASE
                           WHEN slots_filled + 1 >= slots_available THEN 'filled'
                           ELSE status
                       END
                WHERE  id = $1
                """,
                row["job_id"],
            )

        # Notify worker
        notif_title = "ยินดีด้วย! คุณได้รับการคัดเลือก" if body.decision == "hired" \
                      else "ผลการสมัครงาน"
        notif_body  = body.note or (
            "นายจ้างเลือกคุณแล้ว" if body.decision == "hired" else "ขออภัย ครั้งนี้ยังไม่ผ่านการคัดเลือก"
        )

        await db.execute(
            """
            INSERT INTO notifications (user_id, type, title, body)
            SELECT wp.user_id, $1, $2, $3
            FROM   worker_profiles wp
            WHERE  wp.id = $4
            """,
            body.decision, notif_title, notif_body, row["worker_id"],
        )

    return {"application_id": app_id, "new_status": body.decision}
