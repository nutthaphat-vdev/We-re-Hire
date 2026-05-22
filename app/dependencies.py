"""
dependencies.py — FastAPI dependencies ที่ใช้ร่วมกันทุก router
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from uuid import UUID

from app.config import settings
from app.database import get_db
import asyncpg

bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db:          asyncpg.Connection           = Depends(get_db),
) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        user_id = UUID(payload["sub"])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token ไม่ถูกต้องหรือหมดอายุ",
        )

    user = await db.fetchrow(
        "SELECT id, email, role, is_active FROM users WHERE id = $1",
        user_id,
    )

    if not user or not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ไม่พบผู้ใช้หรือบัญชีถูกระงับ",
        )

    return dict(user)


async def get_current_worker(
    current_user: dict = Depends(get_current_user),
) -> dict:
    if current_user["role"] != "worker":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="เฉพาะ worker เท่านั้น",
        )
    return current_user


async def get_current_employer(
    current_user: dict = Depends(get_current_user),
) -> dict:
    if current_user["role"] != "employer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="เฉพาะ employer เท่านั้น",
        )
    return current_user
