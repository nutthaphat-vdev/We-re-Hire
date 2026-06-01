"""
services/worker_service.py — Business logic สำหรับ Worker Profile
"""

from uuid import UUID
from fastapi import HTTPException, status
import asyncpg

from app.schemas.worker import WorkerCreate, WorkerUpdate


# ---------------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------------

async def create_worker_profile(
    user_id: UUID,
    data:    WorkerCreate,
    db:      asyncpg.Connection,
) -> dict:
    # ตรวจว่ามี profile แล้วหรือยัง
    existing = await db.fetchval(
        "SELECT id FROM worker_profiles WHERE user_id = $1", user_id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="โปรไฟล์ถูกสร้างไปแล้ว"
        )

    # ตรวจว่า user role ถูกต้อง
    role = await db.fetchval("SELECT role FROM users WHERE id = $1", user_id)
    if role != "worker":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="เฉพาะ worker เท่านั้นที่สร้าง worker profile ได้"
        )

    row = await db.fetchrow(
        """
        INSERT INTO worker_profiles
            (user_id, full_name, national_id, skills,
             experience_years, daily_rate_expected,
             location, location_name)
        VALUES
            ($1, $2, $3, $4, $5, $6,
             ST_MakePoint($8, $7)::geography,
             $9)
        RETURNING
            id, user_id, full_name, skills, experience_years,
            daily_rate_expected, background_check_status,
            background_checked_at, location_name, is_available, updated_at,
            profile_photo_url
        """,
        user_id,
        data.full_name,
        data.national_id,
        data.skills,
        data.experience_years,
        data.daily_rate_expected,
        data.lat,   # $7
        data.lng,   # $8  ST_MakePoint(lng, lat)
        data.location_name,
    )

    return dict(row)


# ---------------------------------------------------------------------------
# GET (ตัวเอง)
# ---------------------------------------------------------------------------

async def get_my_profile(
    user_id: UUID,
    db:      asyncpg.Connection,
) -> dict:
    row = await db.fetchrow(
        """
        SELECT
            wp.id, wp.user_id, wp.full_name, wp.skills,
            wp.experience_years, wp.daily_rate_expected,
            wp.background_check_status, wp.background_checked_at,
            wp.location_name, wp.is_available, wp.updated_at,
            wp.profile_photo_url,
            -- review summary (LEFT JOIN — อาจยังไม่มี)
            wrs.total_reviews, wrs.avg_score,
            wrs.would_rehire_pct, wrs.top_tags
        FROM   worker_profiles wp
        LEFT JOIN worker_review_summary wrs ON wrs.worker_id = wp.id
        WHERE  wp.user_id = $1
        """,
        user_id,
    )

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ไม่พบโปรไฟล์ กรุณาสร้างโปรไฟล์ก่อน"
        )

    return _attach_review_summary(dict(row))


# ---------------------------------------------------------------------------
# GET PUBLIC (hirer ดู)
# ---------------------------------------------------------------------------

async def get_worker_public(
    worker_id: UUID,
    db:        asyncpg.Connection,
) -> dict:
    row = await db.fetchrow(
        """
        SELECT
            wp.id, wp.full_name, wp.skills,
            wp.experience_years, wp.daily_rate_expected,
            wp.background_check_status, wp.location_name,
            wp.is_available, wp.profile_photo_url,
            wrs.total_reviews, wrs.avg_score,
            wrs.would_rehire_pct, wrs.top_tags
        FROM   worker_profiles wp
        LEFT JOIN worker_review_summary wrs ON wrs.worker_id = wp.id
        WHERE  wp.id = $1
        """,
        worker_id,
    )

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ไม่พบ worker"
        )

    return _attach_review_summary(dict(row))


# ---------------------------------------------------------------------------
# UPDATE
# ---------------------------------------------------------------------------

async def update_worker_profile(
    user_id: UUID,
    data:    WorkerUpdate,
    db:      asyncpg.Connection,
) -> dict:
    # ดึง profile ปัจจุบัน
    current = await db.fetchrow(
        "SELECT id FROM worker_profiles WHERE user_id = $1", user_id
    )
    if not current:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ไม่พบโปรไฟล์"
        )

    # Column allowlist — ป้องกัน SQL injection จาก dynamic SET clause
    ALLOWED_COLUMNS = {
        "full_name", "skills", "experience_years",
        "daily_rate_expected", "location_name", "is_available",
    }

    # Build dynamic SET clause เฉพาะ field ที่ส่งมา
    updates = {}
    if data.full_name           is not None: updates["full_name"]           = data.full_name
    if data.skills              is not None: updates["skills"]              = data.skills
    if data.experience_years    is not None: updates["experience_years"]    = data.experience_years
    if data.daily_rate_expected is not None: updates["daily_rate_expected"] = data.daily_rate_expected
    if data.location_name       is not None: updates["location_name"]       = data.location_name
    if data.is_available        is not None: updates["is_available"]        = data.is_available

    # Validate allowlist (defense-in-depth)
    for col in updates:
        if col not in ALLOWED_COLUMNS:
            raise HTTPException(status_code=400, detail=f"Invalid field: {col}")

    # location ต้องใช้ PostGIS ไม่สามารถ SET ธรรมดาได้
    has_location = data.lat is not None and data.lng is not None

    if not updates and not has_location:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="ไม่มีข้อมูลที่ต้องการอัปเดต"
        )

    # สร้าง SET clause
    set_parts = [f"{col} = ${i+2}" for i, col in enumerate(updates)]
    values    = list(updates.values())

    if has_location:
        next_idx = len(values) + 2
        set_parts.append(f"location = ST_MakePoint(${next_idx+1}, ${next_idx})::geography")
        values += [data.lat, data.lng]

    set_clause = ", ".join(set_parts)

    row = await db.fetchrow(
        f"""
        UPDATE worker_profiles
        SET    {set_clause}
        WHERE  user_id = $1
        RETURNING
            id, user_id, full_name, skills, experience_years,
            daily_rate_expected, background_check_status,
            background_checked_at, location_name, is_available, updated_at,
            profile_photo_url
        """,
        user_id, *values,
    )

    # ดึง review summary แนบกลับไปด้วย
    summary = await db.fetchrow(
        "SELECT total_reviews, avg_score, would_rehire_pct, top_tags FROM worker_review_summary WHERE worker_id = $1",
        row["id"],
    )

    result = dict(row)
    result["total_reviews"]    = summary["total_reviews"]    if summary else None
    result["avg_score"]        = summary["avg_score"]        if summary else None
    result["would_rehire_pct"] = summary["would_rehire_pct"] if summary else None
    result["top_tags"]         = summary["top_tags"]         if summary else []

    return _attach_review_summary(result)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _attach_review_summary(row: dict) -> dict:
    """จัด review summary ให้อยู่ใน nested dict"""
    if row.get("total_reviews") is not None:
        row["review_summary"] = {
            "total_reviews":    row.pop("total_reviews"),
            "avg_score":        row.pop("avg_score"),
            "would_rehire_pct": row.pop("would_rehire_pct"),
            "top_tags":         row.pop("top_tags") or [],
        }
    else:
        # เอา key ออกถ้ามีติดมา
        for key in ("total_reviews", "avg_score", "would_rehire_pct", "top_tags"):
            row.pop(key, None)
        row["review_summary"] = None

    return row
