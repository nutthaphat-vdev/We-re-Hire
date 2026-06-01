"""
routers/matching.py — Matching Engine endpoints

GET   /jobs/nearby                  — worker scan หางานใกล้บ้าน
POST  /jobs/{job_id}/apply          — worker สมัครงาน
GET   /jobs/{job_id}/candidates     — employer ดูผู้สมัคร
PATCH /applications/{app_id}/decide — employer ตัดสินใจจ้าง/ปฏิเสธ
GET   /workers/applications         — worker ดูประวัติการสมัคร
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
import asyncpg

from app.dependencies import get_current_user, get_db

router = APIRouter(tags=["Matching"])

DEFAULT_RADIUS_KM = 5.0
MAX_RADIUS_KM     = 15.0
W_SKILLS          = 0.60
W_DISTANCE        = 0.25
W_RATE            = 0.15


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def compute_match_score(
    worker_skills:   list[str],
    required_skills: list[str],
    distance_km:     float,
    radius_km:       float,
    worker_rate:     Optional[float],
    job_rate:        float,
) -> tuple[float, list[str], list[str]]:
    required_set = set(s.lower() for s in required_skills)
    worker_set   = set(s.lower() for s in worker_skills)
    matched      = list(worker_set & required_set)
    missing      = list(required_set - worker_set)

    skill_score    = len(matched) / len(required_set) if required_set else 1.0
    distance_score = max(0.0, 1.0 - (distance_km / radius_km))

    if worker_rate and job_rate > 0:
        ratio      = worker_rate / job_rate
        rate_score = 1.0 if ratio <= 1.0 else (1.0 - ((ratio - 1.0) / 0.2) if ratio <= 1.2 else 0.0)
    else:
        rate_score = 0.5

    final = round((W_SKILLS * skill_score + W_DISTANCE * distance_score + W_RATE * rate_score) * 100, 2)
    return final, [s.title() for s in matched], [s.title() for s in missing]


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class ApplyRequest(BaseModel):
    lat: float = Field(..., ge=13.4, le=14.0)
    lng: float = Field(..., ge=100.3, le=101.2)


class DecisionRequest(BaseModel):
    decision: str          = Field(..., pattern="^(hired|rejected|shortlisted)$")
    note:     Optional[str]= Field(None, max_length=500)


# ---------------------------------------------------------------------------
# GET /jobs/nearby
# ---------------------------------------------------------------------------

@router.get(
    "/jobs/nearby",
    summary="หางานใกล้บ้าน (worker)",
)
async def get_nearby_jobs(
    lat:          float,
    lng:          float,
    radius_km:    float            = DEFAULT_RADIUS_KM,
    current_user: dict             = Depends(get_current_user),
    db:           asyncpg.Connection = Depends(get_db),
):
    radius_km = min(radius_km, MAX_RADIUS_KM)

    worker = await db.fetchrow(
        "SELECT skills, daily_rate_expected FROM worker_profiles WHERE user_id = $1",
        current_user["id"],
    )
    worker_skills = worker["skills"] if worker else []
    worker_rate   = float(worker["daily_rate_expected"]) if worker and worker["daily_rate_expected"] else None

    rows = await db.fetch(
        """
        SELECT
            jp.id, jp.title, jp.required_skills,
            jp.daily_wage_rate, jp.duration_days,
            jp.slots_available - jp.slots_filled AS slots_remaining,
            jp.location_name, jp.zone_name, jp.start_date,
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
                   $3 * 1000
               )
          AND  (jp.required_skills = '{}' OR jp.required_skills && $4)
        ORDER  BY distance_km ASC
        LIMIT  50
        """,
        lng, lat, radius_km, worker_skills,
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
            "job_id":          str(row["id"]),
            "title":           row["title"],
            "daily_wage_rate": float(row["daily_wage_rate"]),
            "duration_days":   row["duration_days"],
            "slots_remaining": row["slots_remaining"],
            "location_name":   row["location_name"],
            "zone_name":       row["zone_name"],
            "start_date":      str(row["start_date"]) if row["start_date"] else None,
            "distance_km":     round(float(row["distance_km"]), 2),
            "match_score":     score,
            "matched_skills":  matched,
            "missing_skills":  missing,
        })

    results.sort(key=lambda x: (-x["match_score"], x["distance_km"]))
    return {"count": len(results), "jobs": results}


# ---------------------------------------------------------------------------
# POST /jobs/{job_id}/apply
# ---------------------------------------------------------------------------

@router.post(
    "/jobs/{job_id}/apply",
    status_code=status.HTTP_201_CREATED,
    summary="สมัครงาน (worker)",
)
async def apply_to_job(
    job_id:       UUID,
    body:         ApplyRequest,
    current_user: dict               = Depends(get_current_user),
    db:           asyncpg.Connection = Depends(get_db),
):
    job = await db.fetchrow(
        """
        SELECT id, required_skills, daily_wage_rate, slots_available, slots_filled, status
        FROM   job_postings WHERE id = $1
        """,
        job_id,
    )
    if not job:
        raise HTTPException(status_code=404, detail="ไม่พบงาน")
    if job["status"] != "open":
        raise HTTPException(status_code=409, detail="งานนี้ปิดรับสมัครแล้ว")
    if job["slots_filled"] >= job["slots_available"]:
        raise HTTPException(status_code=409, detail="งานนี้รับครบแล้ว")

    worker = await db.fetchrow(
        "SELECT id, skills, daily_rate_expected FROM worker_profiles WHERE user_id = $1",
        current_user["id"],
    )
    if not worker:
        raise HTTPException(status_code=404, detail="กรุณาสร้าง worker profile ก่อน")

    distance_row = await db.fetchrow(
        """
        SELECT ST_Distance(ST_MakePoint($1, $2)::geography, location) / 1000.0 AS distance_km
        FROM   job_postings WHERE id = $3
        """,
        body.lng, body.lat, job_id,
    )
    distance_km = float(distance_row["distance_km"])

    if distance_km > MAX_RADIUS_KM:
        raise HTTPException(
            status_code=400,
            detail=f"งานอยู่ห่าง {distance_km:.1f} กม. เกินระยะ {MAX_RADIUS_KM} กม."
        )

    score, matched_skills, _ = compute_match_score(
        worker_skills   = worker["skills"] or [],
        required_skills = job["required_skills"] or [],
        distance_km     = distance_km,
        radius_km       = DEFAULT_RADIUS_KM,
        worker_rate     = float(worker["daily_rate_expected"]) if worker["daily_rate_expected"] else None,
        job_rate        = float(job["daily_wage_rate"]),
    )

    app = await db.fetchrow(
        """
        INSERT INTO job_applications
            (job_id, worker_id, status, match_score, distance_km, matched_skills)
        VALUES ($1, $2, 'applied', $3, $4, $5)
        ON CONFLICT (job_id, worker_id) DO UPDATE SET
            status        = 'applied',
            match_score   = EXCLUDED.match_score,
            distance_km   = EXCLUDED.distance_km,
            matched_skills= EXCLUDED.matched_skills,
            applied_at    = NOW()
        RETURNING id, status
        """,
        job_id, worker["id"], score, round(distance_km, 2), matched_skills,
    )

    # แจ้งเตือน employer
    await db.execute(
        """
        INSERT INTO notifications (user_id, type, title, body)
        SELECT ep.user_id, 'new_applicant',
               'มีผู้สมัครงานใหม่',
               'match score ' || $1 || '/100'
        FROM   job_postings jp
        JOIN   employer_profiles ep ON ep.id = jp.employer_id
        WHERE  jp.id = $2
        """,
        str(int(score)), job_id,
    )

    return {
        "application_id": str(app["id"]),
        "status":         app["status"],
        "match_score":    score,
        "distance_km":    round(distance_km, 2),
        "matched_skills": matched_skills,
    }


# ---------------------------------------------------------------------------
# GET /jobs/{job_id}/candidates
# ---------------------------------------------------------------------------

@router.get(
    "/jobs/{job_id}/candidates",
    summary="ดูผู้สมัครทั้งหมด (employer)",
)
async def get_candidates(
    job_id:       UUID,
    current_user: dict               = Depends(get_current_user),
    db:           asyncpg.Connection = Depends(get_db),
):
    rows = await db.fetch(
        """
        SELECT
            ja.id              AS application_id,
            wp.id              AS worker_id,
            wp.full_name,
            wp.background_check_status,
            wp.daily_rate_expected,
            wp.profile_photo_url,
            ja.match_score,
            ja.distance_km,
            ja.matched_skills,
            ja.status,
            jp.required_skills
        FROM   job_applications ja
        JOIN   worker_profiles  wp ON wp.id = ja.worker_id
        JOIN   job_postings     jp ON jp.id = ja.job_id
        WHERE  ja.job_id = $1
          AND  ja.status IN ('applied', 'shortlisted')
        ORDER  BY ja.match_score DESC, ja.distance_km ASC
        """,
        job_id,
    )

    return [
        {
            "application_id":          str(row["application_id"]),
            "worker_id":               str(row["worker_id"]),
            "full_name":               row["full_name"],
            "background_check_status": row["background_check_status"],
            "daily_rate_expected":     float(row["daily_rate_expected"]) if row["daily_rate_expected"] else None,
            "profile_photo_url":       row["profile_photo_url"],
            "match_score":             float(row["match_score"] or 0),
            "distance_km":             float(row["distance_km"] or 0),
            "matched_skills":          row["matched_skills"] or [],
            "missing_skills":          list(
                set(s.lower() for s in (row["required_skills"] or [])) -
                set(s.lower() for s in (row["matched_skills"] or []))
            ),
            "status": row["status"],
        }
        for row in rows
    ]


# ---------------------------------------------------------------------------
# PATCH /applications/{app_id}/decide
# ---------------------------------------------------------------------------

@router.patch(
    "/applications/{app_id}/decide",
    summary="ตัดสินใจจ้าง/ปฏิเสธ (employer)",
)
async def decide_application(
    app_id:       UUID,
    body:         DecisionRequest,
    current_user: dict               = Depends(get_current_user),
    db:           asyncpg.Connection = Depends(get_db),
):
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
        raise HTTPException(status_code=404, detail="ไม่พบใบสมัคร")
    if row["status"] in ("hired", "rejected"):
        raise HTTPException(status_code=409, detail=f"ตัดสินใจไปแล้ว: {row['status']}")
    if body.decision == "hired" and row["slots_filled"] >= row["slots_available"]:
        raise HTTPException(status_code=409, detail="ไม่มี slot ว่างแล้ว")

    async with db.transaction():
        await db.execute(
            """
            UPDATE job_applications
            SET status = $1, employer_note = $2, decided_at = NOW()
            WHERE id = $3
            """,
            body.decision, body.note, app_id,
        )

        if body.decision == "hired":
            await db.execute(
                """
                UPDATE job_postings
                SET slots_filled = slots_filled + 1,
                    status = CASE WHEN slots_filled + 1 >= slots_available THEN 'filled' ELSE status END
                WHERE id = $1
                """,
                row["job_id"],
            )

        notif_title = "ยินดีด้วย! คุณได้รับการคัดเลือก" if body.decision == "hired" else "ผลการสมัครงาน"
        notif_body  = body.note or ("นายจ้างเลือกคุณแล้ว" if body.decision == "hired" else "ขออภัย ครั้งนี้ยังไม่ผ่าน")

        await db.execute(
            """
            INSERT INTO notifications (user_id, type, title, body)
            SELECT wp.user_id, $1, $2, $3
            FROM   worker_profiles wp WHERE wp.id = $4
            """,
            body.decision, notif_title, notif_body, row["worker_id"],
        )

    return {"application_id": str(app_id), "new_status": body.decision}


# ---------------------------------------------------------------------------
# GET /workers/applications
# ---------------------------------------------------------------------------

@router.get(
    "/workers/applications",
    summary="ดูประวัติการสมัครงาน (worker)",
)
async def get_my_applications(
    current_user: dict               = Depends(get_current_user),
    db:           asyncpg.Connection = Depends(get_db),
):
    worker = await db.fetchrow(
        "SELECT id FROM worker_profiles WHERE user_id = $1", current_user["id"]
    )
    if not worker:
        raise HTTPException(status_code=404, detail="ไม่พบ worker profile")

    rows = await db.fetch(
        """
        SELECT
            ja.id, ja.status, ja.match_score, ja.distance_km,
            ja.matched_skills, ja.employer_note, ja.applied_at, ja.decided_at,
            jp.title, jp.daily_wage_rate, jp.duration_days, jp.location_name
        FROM   job_applications ja
        JOIN   job_postings     jp ON jp.id = ja.job_id
        WHERE  ja.worker_id = $1
        ORDER  BY ja.applied_at DESC
        """,
        worker["id"],
    )

    return [
        {
            "application_id":  str(row["id"]),
            "status":          row["status"],
            "match_score":     float(row["match_score"] or 0),
            "distance_km":     float(row["distance_km"] or 0),
            "matched_skills":  row["matched_skills"] or [],
            "employer_note":   row["employer_note"],
            "applied_at":      row["applied_at"].isoformat(),
            "decided_at":      row["decided_at"].isoformat() if row["decided_at"] else None,
            "job": {
                "title":           row["title"],
                "daily_wage_rate": float(row["daily_wage_rate"]),
                "duration_days":   row["duration_days"],
                "location_name":   row["location_name"],
            },
        }
        for row in rows
    ]
