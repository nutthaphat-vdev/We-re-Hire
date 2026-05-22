"""
routers/workers.py — Worker Profile endpoints

POST  /workers/profile      → สร้างโปรไฟล์
GET   /workers/profile/me   → ดูโปรไฟล์ตัวเอง
PATCH /workers/profile      → แก้ไขโปรไฟล์
GET   /workers/{id}         → hirer ดูโปรไฟล์ worker (public)
"""

from fastapi import APIRouter, Depends, status
from uuid import UUID
import asyncpg

from app.schemas.worker import (
    WorkerCreate, WorkerUpdate,
    WorkerOut, WorkerPublicOut,
)
from app.services import worker_service
from app.dependencies import get_current_user, get_db

router = APIRouter(prefix="/workers", tags=["Workers"])


# ---------------------------------------------------------------------------
# POST /workers/profile — สร้างโปรไฟล์ครั้งแรก
# ---------------------------------------------------------------------------

@router.post(
    "/profile",
    response_model=WorkerOut,
    status_code=status.HTTP_201_CREATED,
    summary="สร้าง worker profile",
)
async def create_profile(
    body:         WorkerCreate,
    current_user: dict              = Depends(get_current_user),
    db:           asyncpg.Connection= Depends(get_db),
):
    return await worker_service.create_worker_profile(
        user_id=current_user["id"],
        data=body,
        db=db,
    )


# ---------------------------------------------------------------------------
# GET /workers/profile/me — ดูโปรไฟล์ตัวเอง
# ---------------------------------------------------------------------------

@router.get(
    "/profile/me",
    response_model=WorkerOut,
    summary="ดูโปรไฟล์ตัวเอง (worker)",
)
async def get_my_profile(
    current_user: dict              = Depends(get_current_user),
    db:           asyncpg.Connection= Depends(get_db),
):
    return await worker_service.get_my_profile(
        user_id=current_user["id"],
        db=db,
    )


# ---------------------------------------------------------------------------
# PATCH /workers/profile — แก้ไขโปรไฟล์
# ---------------------------------------------------------------------------

@router.patch(
    "/profile",
    response_model=WorkerOut,
    summary="แก้ไขโปรไฟล์ (ส่งมาแค่ field ที่อยากเปลี่ยน)",
)
async def update_profile(
    body:         WorkerUpdate,
    current_user: dict              = Depends(get_current_user),
    db:           asyncpg.Connection= Depends(get_db),
):
    return await worker_service.update_worker_profile(
        user_id=current_user["id"],
        data=body,
        db=db,
    )


# ---------------------------------------------------------------------------
# GET /workers/{worker_id} — hirer ดูโปรไฟล์ worker (public view)
# ---------------------------------------------------------------------------

@router.get(
    "/{worker_id}",
    response_model=WorkerPublicOut,
    summary="ดูโปรไฟล์ worker (public — สำหรับ hirer)",
)
async def get_worker_public(
    worker_id:    UUID,
    current_user: dict              = Depends(get_current_user),
    db:           asyncpg.Connection= Depends(get_db),
):
    return await worker_service.get_worker_public(
        worker_id=worker_id,
        db=db,
    )
