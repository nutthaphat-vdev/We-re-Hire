"""
schemas/worker.py — Pydantic models สำหรับ Worker Profile API
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum


class BackgroundCheckStatus(str, Enum):
    pending  = "pending"
    verified = "verified"
    failed   = "failed"
    expired  = "expired"


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class WorkerCreate(BaseModel):
    full_name:           str            = Field(..., min_length=2, max_length=100)
    national_id:         Optional[str]  = Field(None, pattern=r"^\d{13}$")
    skills:              list[str]      = Field(default=[], max_length=20)
    experience_years:    int            = Field(default=0, ge=0, le=60)
    daily_rate_expected: Optional[float]= Field(None, gt=0, le=10000)
    lat:                 float          = Field(..., ge=13.4, le=14.0)
    lng:                 float          = Field(..., ge=100.3, le=101.2)
    location_name:       Optional[str]  = Field(None, max_length=255)

    @field_validator("skills")
    @classmethod
    def normalize_skills(cls, v: list[str]) -> list[str]:
        return list(dict.fromkeys(s.strip().lower() for s in v if s.strip()))

    @field_validator("national_id")
    @classmethod
    def validate_national_id(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        digits = [int(c) for c in v]
        total  = sum(d * (13 - i) for i, d in enumerate(digits[:12]))
        check  = (11 - (total % 11)) % 10
        if check != digits[12]:
            raise ValueError("เลขบัตรประชาชนไม่ถูกต้อง")
        return v


class WorkerUpdate(BaseModel):
    full_name:           Optional[str]        = Field(None, min_length=2, max_length=100)
    skills:              Optional[list[str]]  = Field(None, max_length=20)
    experience_years:    Optional[int]        = Field(None, ge=0, le=60)
    daily_rate_expected: Optional[float]      = Field(None, gt=0, le=10000)
    lat:                 Optional[float]      = Field(None, ge=13.4, le=14.0)
    lng:                 Optional[float]      = Field(None, ge=100.3, le=101.2)
    location_name:       Optional[str]        = Field(None, max_length=255)
    is_available:        Optional[bool]       = None

    @field_validator("skills")
    @classmethod
    def normalize_skills(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        if v is None:
            return v
        return list(dict.fromkeys(s.strip().lower() for s in v if s.strip()))


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class ReviewSummaryOut(BaseModel):
    total_reviews:    int
    avg_score:        Optional[float]
    would_rehire_pct: Optional[float]
    top_tags:         list[str]


class WorkerOut(BaseModel):
    """โปรไฟล์ที่ worker เห็นของตัวเอง"""
    id:                      UUID
    user_id:                 UUID
    full_name:               str
    skills:                  list[str]
    experience_years:        int
    daily_rate_expected:     Optional[float]
    background_check_status: BackgroundCheckStatus
    background_checked_at:   Optional[datetime]
    location_name:           Optional[str]
    is_available:            bool
    updated_at:              datetime
    profile_photo_url:       Optional[str] = None
    review_summary:          Optional[ReviewSummaryOut] = None

    model_config = {"from_attributes": True}


class WorkerPublicOut(BaseModel):
    """โปรไฟล์ที่ hirer เห็น — ไม่มี national_id, user_id"""
    id:                      UUID
    full_name:               str
    skills:                  list[str]
    experience_years:        int
    daily_rate_expected:     Optional[float]
    background_check_status: BackgroundCheckStatus
    location_name:           Optional[str]
    is_available:            bool
    profile_photo_url:       Optional[str] = None
    review_summary:          Optional[ReviewSummaryOut] = None

    model_config = {"from_attributes": True}
