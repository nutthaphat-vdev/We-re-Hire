"""
schemas/employer.py — Pydantic models สำหรับ Employer + Job Posting
"""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime, date
from enum import Enum


class BusinessType(str, Enum):
    factory  = "factory"
    grocery  = "grocery"
    sme      = "sme"
    warehouse= "warehouse"
    other    = "other"


class JobStatus(str, Enum):
    draft  = "draft"
    open   = "open"
    filled = "filled"
    closed = "closed"
    expired= "expired"


# ---------------------------------------------------------------------------
# Employer Request / Response
# ---------------------------------------------------------------------------

class EmployerCreate(BaseModel):
    company_name:  str          = Field(..., min_length=2, max_length=200)
    business_type: BusinessType = BusinessType.other
    contact_person:str          = Field(..., min_length=2, max_length=100)


class EmployerOut(BaseModel):
    id:             UUID
    user_id:        UUID
    company_name:   str
    business_type:  Optional[str]
    contact_person: str
    verified_status:str
    created_at:     datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Job Posting Request / Response
# ---------------------------------------------------------------------------

class JobCreate(BaseModel):
    title:           str        = Field(..., min_length=2, max_length=200)
    description:     Optional[str] = None
    required_skills: list[str]  = Field(default=[])
    daily_wage_rate: float      = Field(..., gt=0, le=10000)
    duration_days:   int        = Field(..., gt=0, le=365)
    slots_available: int        = Field(default=1, gt=0, le=100)
    lat:             float      = Field(..., ge=13.4, le=14.0)
    lng:             float      = Field(..., ge=100.3, le=101.2)
    location_name:   Optional[str] = Field(None, max_length=255)
    zone_name:       Optional[str] = None
    start_date:      Optional[date]= None


class JobStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(open|closed|draft)$")


class JobOut(BaseModel):
    id:              UUID
    employer_id:     UUID
    title:           str
    description:     Optional[str]
    required_skills: list[str]
    daily_wage_rate: float
    duration_days:   int
    slots_available: int
    slots_filled:    int
    status:          str
    location_name:   Optional[str]
    zone_name:       Optional[str]
    start_date:      Optional[date]
    expires_at:      Optional[datetime]
    created_at:      datetime

    model_config = {"from_attributes": True}
