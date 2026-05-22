"""
routers/auth.py
POST /auth/register  — สมัครสมาชิก (worker หรือ employer)
POST /auth/login     — เข้าสู่ระบบ รับ JWT token กลับมา
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
import asyncpg
import jwt
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.config import settings
from app.database import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    email:    EmailStr
    password: str      = Field(..., min_length=6, max_length=100)
    phone:    Optional[str] = Field(None, pattern=r"^0[0-9]{8,9}$")
    role:     str      = Field(..., pattern="^(worker|employer)$")


class LoginRequest(BaseModel):
    email:    EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    role:         str
    user_id:      UUID


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def hash_password(password: str) -> str:
    """SHA-256 + random salt — เปลี่ยนเป็น bcrypt ได้ใน phase 2"""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return f"{salt}:{hashed}"


def verify_password(password: str, stored_hash: str) -> bool:
    salt, hashed = stored_hash.split(":", 1)
    check = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return check == hashed


def create_token(user_id: UUID, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


# ---------------------------------------------------------------------------
# POST /auth/register
# ---------------------------------------------------------------------------

@router.post(
    "/register",
    response_model=TokenOut,
    status_code=status.HTTP_201_CREATED,
    summary="สมัครสมาชิก (worker หรือ employer)",
)
async def register(
    body: RegisterRequest,
    db:   asyncpg.Connection = Depends(get_db),
):
    # เช็ค email ซ้ำ
    exists = await db.fetchval(
        "SELECT id FROM users WHERE email = $1", body.email
    )
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="อีเมลนี้ถูกใช้งานแล้ว"
        )

    # เช็ค phone ซ้ำ (ถ้ามี)
    if body.phone:
        phone_exists = await db.fetchval(
            "SELECT id FROM users WHERE phone = $1", body.phone
        )
        if phone_exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="เบอร์โทรนี้ถูกใช้งานแล้ว"
            )

    # สร้าง user
    user = await db.fetchrow(
        """
        INSERT INTO users (email, phone, password_hash, role)
        VALUES ($1, $2, $3, $4)
        RETURNING id, role
        """,
        body.email,
        body.phone,
        hash_password(body.password),
        body.role,
    )

    token = create_token(user["id"], user["role"])

    return TokenOut(
        access_token=token,
        role=user["role"],
        user_id=user["id"],
    )


# ---------------------------------------------------------------------------
# POST /auth/login
# ---------------------------------------------------------------------------

@router.post(
    "/login",
    response_model=TokenOut,
    summary="เข้าสู่ระบบ รับ JWT token",
)
async def login(
    body: LoginRequest,
    db:   asyncpg.Connection = Depends(get_db),
):
    user = await db.fetchrow(
        "SELECT id, role, password_hash, is_active FROM users WHERE email = $1",
        body.email,
    )

    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="อีเมลหรือรหัสผ่านไม่ถูกต้อง"
        )

    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="บัญชีถูกระงับการใช้งาน"
        )

    token = create_token(user["id"], user["role"])

    return TokenOut(
        access_token=token,
        role=user["role"],
        user_id=user["id"],
    )
