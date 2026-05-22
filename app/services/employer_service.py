"""
services/employer_service.py — Business logic สำหรับ Employer + Job Posting
"""

from uuid import UUID
from fastapi import HTTPException, status
import asyncpg
from datetime import datetime, timedelta, timezone

from app.schemas.employer import EmployerCreate, JobCreate, JobStatusUpdate


# ---------------------------------------------------------------------------
# EMPLOYER
# ---------------------------------------------------------------------------

async def create_employer_profile(
    user_id: UUID,
    data:    EmployerCreate,
    db:      asyncpg.Connection,
) -> dict:
    existing = await db.fetchval(
        "SELECT id FROM employer_profiles WHERE user_id = $1", user_id
    )
    if existing:
        raise HTTPException(status_code=409, detail="โปรไฟล์ถูกสร้างไปแล้ว")

    role = await db.fetchval("SELECT role FROM users WHERE id = $1", user_id)
    if role != "employer":
        raise HTTPException(status_code=403, detail="เฉพาะ employer เท่านั้น")

    row = await db.fetchrow(
        """
        INSERT INTO employer_profiles (user_id, company_name, business_type, contact_person)
        VALUES ($1, $2, $3, $4)
        RETURNING id, user_id, company_name, business_type, contact_person, verified_status, created_at
        """,
        user_id, data.company_name, data.business_type.value, data.contact_person,
    )
    return dict(row)


async def get_my_employer_profile(user_id: UUID, db: asyncpg.Connection) -> dict:
    row = await db.fetchrow(
        """
        SELECT id, user_id, company_name, business_type, contact_person, verified_status, created_at
        FROM employer_profiles WHERE user_id = $1
        """,
        user_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="ไม่พบโปรไฟล์")
    return dict(row)


# ---------------------------------------------------------------------------
# JOB POSTINGS
# ---------------------------------------------------------------------------

async def create_job(
    user_id: UUID,
    data:    JobCreate,
    db:      asyncpg.Connection,
) -> dict:
    employer = await db.fetchrow(
        "SELECT id FROM employer_profiles WHERE user_id = $1", user_id
    )
    if not employer:
        raise HTTPException(status_code=404, detail="กรุณาสร้าง employer profile ก่อน")

    # ตั้ง expires_at 30 วันจากวันนี้
    expires_at = datetime.now(timezone.utc) + timedelta(days=30)

    row = await db.fetchrow(
        """
        INSERT INTO job_postings
            (employer_id, title, description, required_skills,
             daily_wage_rate, duration_days, slots_available,
             location, location_name, zone_name, start_date, expires_at)
        VALUES
            ($1, $2, $3, $4, $5, $6, $7,
             ST_MakePoint($9, $8)::geography,
             $10, $11, $12, $13)
        RETURNING
            id, employer_id, title, description, required_skills,
            daily_wage_rate, duration_days, slots_available, slots_filled,
            status, location_name, zone_name, start_date, expires_at, created_at
        """,
        employer["id"],
        data.title,
        data.description,
        data.required_skills,
        data.daily_wage_rate,
        data.duration_days,
        data.slots_available,
        data.lat,    # $8
        data.lng,    # $9  ST_MakePoint(lng, lat)
        data.location_name,
        data.zone_name,
        data.start_date,
        expires_at,
    )
    return dict(row)


async def get_my_jobs(user_id: UUID, db: asyncpg.Connection) -> list[dict]:
    employer = await db.fetchrow(
        "SELECT id FROM employer_profiles WHERE user_id = $1", user_id
    )
    if not employer:
        raise HTTPException(status_code=404, detail="ไม่พบ employer profile")

    rows = await db.fetch(
        """
        SELECT id, employer_id, title, description, required_skills,
               daily_wage_rate, duration_days, slots_available, slots_filled,
               status, location_name, zone_name, start_date, expires_at, created_at
        FROM   job_postings
        WHERE  employer_id = $1
        ORDER  BY created_at DESC
        """,
        employer["id"],
    )
    return [dict(r) for r in rows]


async def get_job_detail(job_id: UUID, db: asyncpg.Connection) -> dict:
    row = await db.fetchrow(
        """
        SELECT id, employer_id, title, description, required_skills,
               daily_wage_rate, duration_days, slots_available, slots_filled,
               status, location_name, zone_name, start_date, expires_at, created_at
        FROM   job_postings WHERE id = $1
        """,
        job_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="ไม่พบงาน")
    return dict(row)


async def update_job_status(
    user_id: UUID,
    job_id:  UUID,
    data:    JobStatusUpdate,
    db:      asyncpg.Connection,
) -> dict:
    employer = await db.fetchrow(
        "SELECT id FROM employer_profiles WHERE user_id = $1", user_id
    )
    if not employer:
        raise HTTPException(status_code=404, detail="ไม่พบ employer profile")

    row = await db.fetchrow(
        """
        UPDATE job_postings SET status = $1
        WHERE  id = $2 AND employer_id = $3
        RETURNING id, employer_id, title, description, required_skills,
                  daily_wage_rate, duration_days, slots_available, slots_filled,
                  status, location_name, zone_name, start_date, expires_at, created_at
        """,
        data.status, job_id, employer["id"],
    )
    if not row:
        raise HTTPException(status_code=404, detail="ไม่พบงาน หรือไม่มีสิทธิ์แก้ไข")
    return dict(row)
