"""
routers/employers.py — Employer Profile + Job Posting endpoints

POST  /employers/profile       → สร้าง employer profile
GET   /employers/profile/me    → ดูโปรไฟล์ตัวเอง
POST  /jobs                    → โพสต์งานใหม่
GET   /jobs/mine               → ดูงานทั้งหมดของตัวเอง
GET   /jobs/{job_id}           → ดูรายละเอียดงาน
PATCH /jobs/{job_id}/status    → เปิด/ปิดงาน
"""

from fastapi import APIRouter, Depends, status
from uuid import UUID
import asyncpg

from app.schemas.employer import (
    EmployerCreate, EmployerOut,
    JobCreate, JobOut, JobStatusUpdate,
)
from app.services import employer_service
from app.dependencies import get_current_user, get_db

router = APIRouter(tags=["Employers & Jobs"])


# ---------------------------------------------------------------------------
# Employer Profile
# ---------------------------------------------------------------------------

@router.post(
    "/employers/profile",
    response_model=EmployerOut,
    status_code=status.HTTP_201_CREATED,
    summary="สร้าง employer profile",
)
async def create_employer_profile(
    body:         EmployerCreate,
    current_user: dict               = Depends(get_current_user),
    db:           asyncpg.Connection = Depends(get_db),
):
    return await employer_service.create_employer_profile(
        user_id=current_user["id"], data=body, db=db,
    )


@router.get(
    "/employers/profile/me",
    response_model=EmployerOut,
    summary="ดูโปรไฟล์ employer ตัวเอง",
)
async def get_my_employer_profile(
    current_user: dict               = Depends(get_current_user),
    db:           asyncpg.Connection = Depends(get_db),
):
    return await employer_service.get_my_employer_profile(
        user_id=current_user["id"], db=db,
    )


# ---------------------------------------------------------------------------
# Job Postings
# ---------------------------------------------------------------------------

@router.post(
    "/jobs",
    response_model=JobOut,
    status_code=status.HTTP_201_CREATED,
    summary="โพสต์งานใหม่",
)
async def create_job(
    body:         JobCreate,
    current_user: dict               = Depends(get_current_user),
    db:           asyncpg.Connection = Depends(get_db),
):
    return await employer_service.create_job(
        user_id=current_user["id"], data=body, db=db,
    )


@router.get(
    "/jobs/mine",
    response_model=list[JobOut],
    summary="ดูงานทั้งหมดที่โพสต์ไว้",
)
async def get_my_jobs(
    current_user: dict               = Depends(get_current_user),
    db:           asyncpg.Connection = Depends(get_db),
):
    return await employer_service.get_my_jobs(
        user_id=current_user["id"], db=db,
    )


@router.get(
    "/jobs/{job_id}",
    response_model=JobOut,
    summary="ดูรายละเอียดงาน (ต้องอยู่หลัง /jobs/mine)",
)
async def get_job_detail(
    job_id:       UUID,
    current_user: dict               = Depends(get_current_user),
    db:           asyncpg.Connection = Depends(get_db),
):
    return await employer_service.get_job_detail(job_id=job_id, db=db)


@router.patch(
    "/jobs/{job_id}/status",
    response_model=JobOut,
    summary="เปิด/ปิดงาน",
)
async def update_job_status(
    job_id:       UUID,
    body:         JobStatusUpdate,
    current_user: dict               = Depends(get_current_user),
    db:           asyncpg.Connection = Depends(get_db),
):
    return await employer_service.update_job_status(
        user_id=current_user["id"], job_id=job_id, data=body, db=db,
    )
