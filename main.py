"""
WeHire — Daily Wage Matchmaking Platform
main.py — FastAPI entry point + Auth + Profile CRUD + Matching engine

Stack: FastAPI + asyncpg + Supabase (PostgreSQL + PostGIS) + PyJWT
"""

import os
import asyncpg
import jwt
import bcrypt
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from pydantic_settings import BaseSettings

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

class Settings(BaseSettings):
    database_url:         str
    jwt_secret:           str
    jwt_algorithm:        str = "HS256"
    jwt_expire_minutes:   int = 1440
    cors_origins:         str = "http://localhost:5500,http://127.0.0.1:5500,http://localhost:3000,null"
    frontend_url:         str = ""   # Railway frontend URL เช่น https://wehire.up.railway.app
    supabase_url:         str = "https://wexupoegrynxbhdzioym.supabase.co"
    supabase_anon_key:    str = ""
    supabase_jwt_secret:  str = ""  # Settings → API → JWT Secret

    class Config:
        env_file = ".env"

settings = Settings()


# ---------------------------------------------------------------------------
# DB Connection Pool (lifespan)
# ---------------------------------------------------------------------------

pool: asyncpg.Pool | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global pool
    pool = await asyncpg.create_pool(
        settings.database_url,
        min_size=2,
        max_size=10,
        command_timeout=30,
    )
    print("✅ DB pool connected")
    yield
    await pool.close()
    print("🔌 DB pool closed")

async def get_db() -> asyncpg.Connection:
    async with pool.acquire() as conn:
        yield conn


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="WeHire API",
    version="0.1.0",
    description="Daily Wage Matchmaking Platform — BKK MVP",
    lifespan=lifespan,
)

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
if settings.frontend_url:
    origins.append(settings.frontend_url.strip())

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# JWT Helpers
# ---------------------------------------------------------------------------

security = HTTPBearer()

def create_token(user_id: str, role: str) -> str:
    payload = {
        "sub":  user_id,
        "role": role,
        "exp":  datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes),
        "iat":  datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token หมดอายุ กรุณาเข้าสู่ระบบใหม่")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token ไม่ถูกต้อง")

async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    return decode_token(creds.credentials)

async def require_worker(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "worker":
        raise HTTPException(status_code=403, detail="เฉพาะ Worker เท่านั้น")
    return user

async def require_employer(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "employer":
        raise HTTPException(status_code=403, detail="เฉพาะ Employer เท่านั้น")
    return user


# ============================================================
# AUTH ROUTES
# ============================================================

# ── Google OAuth via Supabase ──────────────────────────────

class GoogleCallbackRequest(BaseModel):
    access_token: str          # Supabase session access_token
    role:         str = Field(..., pattern="^(worker|employer)$")

@app.get("/auth/google/url", tags=["Auth"])
async def google_login_url(role: str = "worker"):
    """Frontend เรียกเพื่อได้ redirect URL ไป Google"""
    if role not in ("worker", "employer"):
        raise HTTPException(status_code=400, detail="role ไม่ถูกต้อง")
    url = (
        f"{settings.supabase_url}/auth/v1/authorize"
        f"?provider=google"
        f"&redirect_to={settings.frontend_url or 'http://127.0.0.1:5500'}/index.html?role={role}"
    )
    return {"url": url}

@app.post("/auth/google/callback", tags=["Auth"])
async def google_callback(
    body: GoogleCallbackRequest,
    db:   asyncpg.Connection = Depends(get_db),
):
    """
    Frontend ได้ Supabase session แล้วส่ง access_token มาที่นี่
    Backend verify → สร้าง/หา user ใน DB → ออก JWT ของเรา
    """
    # Verify Supabase JWT
    try:
        payload = jwt.decode(
            body.access_token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Supabase token ไม่ถูกต้อง: {e}")

    supabase_uid = payload.get("sub")
    email        = payload.get("email") or payload.get("user_metadata", {}).get("email", "")

    if not email:
        raise HTTPException(status_code=400, detail="ไม่พบ email จาก Google")

    # Upsert user ใน DB ของเรา
    user = await db.fetchrow(
        """
        INSERT INTO users (email, password_hash, role)
        VALUES ($1, 'google_oauth', $2)
        ON CONFLICT (email) DO UPDATE
            SET role = CASE
                WHEN users.password_hash = 'google_oauth' THEN $2
                ELSE users.role   -- ถ้า email มีอยู่แล้ว (สมัครด้วย password) ไม่เปลี่ยน role
            END
        RETURNING id, role, is_active
        """,
        email, body.role,
    )

    if not user["is_active"]:
        raise HTTPException(status_code=403, detail="บัญชีถูกระงับ")

    token = create_token(str(user["id"]), user["role"])
    return {
        "access_token": token,
        "token_type":   "bearer",
        "role":         user["role"],
        "user_id":      str(user["id"]),
    }


class RegisterRequest(BaseModel):
    email:    EmailStr
    password: str  = Field(..., min_length=6, max_length=100)
    role:     str  = Field(..., pattern="^(worker|employer)$")
    phone:    Optional[str] = Field(None, max_length=20)

class LoginRequest(BaseModel):
    email:    EmailStr
    password: str

@app.post("/auth/register", status_code=201, tags=["Auth"])
async def register(body: RegisterRequest, db: asyncpg.Connection = Depends(get_db)):
    # Check duplicate
    existing = await db.fetchval("SELECT id FROM users WHERE email=$1", body.email)
    if existing:
        raise HTTPException(status_code=409, detail="อีเมลนี้ถูกใช้งานแล้ว")

    if body.phone:
        existing_phone = await db.fetchval("SELECT id FROM users WHERE phone=$1", body.phone)
        if existing_phone:
            raise HTTPException(status_code=409, detail="เบอร์โทรนี้ถูกใช้งานแล้ว")

    # Hash password (bcrypt cost=12 — ปลอดภัยดี ไม่แรงเกิน)
    hashed = bcrypt.hashpw(body.password.encode(), bcrypt.gensalt(rounds=12)).decode()

    user = await db.fetchrow(
        """
        INSERT INTO users (email, phone, password_hash, role)
        VALUES ($1, $2, $3, $4)
        RETURNING id, role
        """,
        body.email, body.phone, hashed, body.role,
    )

    token = create_token(str(user["id"]), user["role"])
    return {
        "access_token": token,
        "token_type":   "bearer",
        "role":         user["role"],
        "user_id":      str(user["id"]),
    }


@app.post("/auth/login", tags=["Auth"])
async def login(body: LoginRequest, db: asyncpg.Connection = Depends(get_db)):
    user = await db.fetchrow(
        "SELECT id, password_hash, role, is_active FROM users WHERE email=$1",
        body.email,
    )
    if not user:
        raise HTTPException(status_code=401, detail="อีเมลหรือรหัสผ่านไม่ถูกต้อง")
    if not user["is_active"]:
        raise HTTPException(status_code=403, detail="บัญชีถูกระงับ")

    if not bcrypt.checkpw(body.password.encode(), user["password_hash"].encode()):
        raise HTTPException(status_code=401, detail="อีเมลหรือรหัสผ่านไม่ถูกต้อง")

    token = create_token(str(user["id"]), user["role"])
    return {
        "access_token": token,
        "token_type":   "bearer",
        "role":         user["role"],
        "user_id":      str(user["id"]),
    }


@app.get("/auth/me", tags=["Auth"])
async def me(user: dict = Depends(get_current_user), db: asyncpg.Connection = Depends(get_db)):
    row = await db.fetchrow(
        "SELECT id, email, phone, role, created_at FROM users WHERE id=$1",
        UUID(user["sub"]),
    )
    if not row:
        raise HTTPException(status_code=404, detail="ไม่พบผู้ใช้")
    return dict(row)


# ============================================================
# WORKER PROFILE
# ============================================================

class WorkerProfileCreate(BaseModel):
    full_name:           str   = Field(..., min_length=1, max_length=100)
    skills:              list[str] = Field(default=[])
    experience_years:    int   = Field(default=0, ge=0, le=50)
    daily_rate_expected: Optional[float] = Field(None, gt=0)
    lat:                 float = Field(..., ge=-90,  le=90)
    lng:                 float = Field(..., ge=-180, le=180)
    location_name:       Optional[str] = Field(None, max_length=255)

class WorkerProfileUpdate(BaseModel):
    skills:              Optional[list[str]] = None
    experience_years:    Optional[int]       = Field(None, ge=0, le=50)
    daily_rate_expected: Optional[float]     = Field(None, gt=0)
    lat:                 Optional[float]     = Field(None, ge=-90,  le=90)
    lng:                 Optional[float]     = Field(None, ge=-180, le=180)
    location_name:       Optional[str]       = Field(None, max_length=255)
    is_available:        Optional[bool]      = None

@app.get("/workers/profile/me", tags=["Worker"])
async def get_worker_profile(
    user: dict = Depends(require_worker),
    db:   asyncpg.Connection = Depends(get_db),
):
    row = await db.fetchrow(
        """
        SELECT id, full_name, skills, experience_years, daily_rate_expected,
               background_check_status, location_name, is_available,
               ST_X(location::geometry) AS lng,
               ST_Y(location::geometry) AS lat,
               updated_at
        FROM   worker_profiles
        WHERE  user_id = $1
        """,
        UUID(user["sub"]),
    )
    if not row:
        raise HTTPException(status_code=404, detail="ไม่พบโปรไฟล์ Worker")
    return dict(row)

@app.post("/workers/profile", status_code=201, tags=["Worker"])
async def create_worker_profile(
    body: WorkerProfileCreate,
    user: dict = Depends(require_worker),
    db:   asyncpg.Connection = Depends(get_db),
):
    existing = await db.fetchval(
        "SELECT id FROM worker_profiles WHERE user_id=$1", UUID(user["sub"])
    )
    if existing:
        raise HTTPException(status_code=409, detail="มีโปรไฟล์อยู่แล้ว ใช้ PATCH แทน")

    # Clean skills — lowercase + dedupe
    clean_skills = list({s.strip().lower() for s in body.skills if s.strip()})

    row = await db.fetchrow(
        """
        INSERT INTO worker_profiles
            (user_id, full_name, skills, experience_years, daily_rate_expected,
             location, location_name)
        VALUES
            ($1, $2, $3, $4, $5,
             ST_MakePoint($6, $7)::geography, $8)
        RETURNING id, full_name, skills, experience_years, daily_rate_expected,
                  background_check_status, location_name, is_available
        """,
        UUID(user["sub"]), body.full_name, clean_skills,
        body.experience_years, body.daily_rate_expected,
        body.lng, body.lat, body.location_name,
    )
    return dict(row)

@app.patch("/workers/profile", tags=["Worker"])
async def update_worker_profile(
    body: WorkerProfileUpdate,
    user: dict = Depends(require_worker),
    db:   asyncpg.Connection = Depends(get_db),
):
    # Build dynamic SET clause — only update fields provided
    updates = {}
    if body.skills is not None:
        updates["skills"] = list({s.strip().lower() for s in body.skills if s.strip()})
    if body.experience_years is not None:
        updates["experience_years"] = body.experience_years
    if body.daily_rate_expected is not None:
        updates["daily_rate_expected"] = body.daily_rate_expected
    if body.location_name is not None:
        updates["location_name"] = body.location_name
    if body.is_available is not None:
        updates["is_available"] = body.is_available

    if not updates and body.lat is None:
        raise HTTPException(status_code=400, detail="ไม่มีข้อมูลที่ต้องอัปเดต")

    # Build parameterized query
    set_parts = []
    params    = []
    idx       = 1

    for key, val in updates.items():
        set_parts.append(f"{key} = ${idx}")
        params.append(val)
        idx += 1

    if body.lat is not None and body.lng is not None:
        set_parts.append(f"location = ST_MakePoint(${idx}, ${idx+1})::geography")
        params.extend([body.lng, body.lat])
        idx += 2

    params.append(UUID(user["sub"]))
    query = f"""
        UPDATE worker_profiles
        SET    {', '.join(set_parts)}
        WHERE  user_id = ${idx}
        RETURNING id, full_name, skills, experience_years, daily_rate_expected,
                  background_check_status, location_name, is_available
    """
    row = await db.fetchrow(query, *params)
    if not row:
        raise HTTPException(status_code=404, detail="ไม่พบโปรไฟล์ Worker")
    return dict(row)


# ============================================================
# EMPLOYER PROFILE
# ============================================================

class EmployerProfileCreate(BaseModel):
    company_name:   str = Field(..., min_length=1, max_length=200)
    business_type:  Optional[str] = Field(None, max_length=100)
    contact_person: str = Field(..., min_length=1, max_length=100)

class EmployerProfileUpdate(BaseModel):
    company_name:   Optional[str] = Field(None, min_length=1, max_length=200)
    business_type:  Optional[str] = Field(None, max_length=100)
    contact_person: Optional[str] = Field(None, min_length=1, max_length=100)

@app.get("/employers/profile/me", tags=["Employer"])
async def get_employer_profile(
    user: dict = Depends(require_employer),
    db:   asyncpg.Connection = Depends(get_db),
):
    row = await db.fetchrow(
        """
        SELECT id, company_name, business_type, contact_person, verified_status, created_at
        FROM   employer_profiles
        WHERE  user_id = $1
        """,
        UUID(user["sub"]),
    )
    if not row:
        raise HTTPException(status_code=404, detail="ไม่พบโปรไฟล์ Employer")
    return dict(row)

@app.post("/employers/profile", status_code=201, tags=["Employer"])
async def create_employer_profile(
    body: EmployerProfileCreate,
    user: dict = Depends(require_employer),
    db:   asyncpg.Connection = Depends(get_db),
):
    existing = await db.fetchval(
        "SELECT id FROM employer_profiles WHERE user_id=$1", UUID(user["sub"])
    )
    if existing:
        raise HTTPException(status_code=409, detail="มีโปรไฟล์อยู่แล้ว ใช้ PATCH แทน")

    row = await db.fetchrow(
        """
        INSERT INTO employer_profiles (user_id, company_name, business_type, contact_person)
        VALUES ($1, $2, $3, $4)
        RETURNING id, company_name, business_type, contact_person, verified_status
        """,
        UUID(user["sub"]), body.company_name, body.business_type, body.contact_person,
    )
    return dict(row)

@app.patch("/employers/profile", tags=["Employer"])
async def update_employer_profile(
    body: EmployerProfileUpdate,
    user: dict = Depends(require_employer),
    db:   asyncpg.Connection = Depends(get_db),
):
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="ไม่มีข้อมูลที่ต้องอัปเดต")

    set_parts = []
    params    = []
    for idx, (key, val) in enumerate(updates.items(), start=1):
        set_parts.append(f"{key} = ${idx}")
        params.append(val)
    params.append(UUID(user["sub"]))

    query = f"""
        UPDATE employer_profiles
        SET    {', '.join(set_parts)}
        WHERE  user_id = ${len(params)}
        RETURNING id, company_name, business_type, contact_person, verified_status
    """
    row = await db.fetchrow(query, *params)
    if not row:
        raise HTTPException(status_code=404, detail="ไม่พบโปรไฟล์ Employer")
    return dict(row)


# ============================================================
# JOB POSTINGS
# ============================================================

class JobCreate(BaseModel):
    title:           str   = Field(..., min_length=1, max_length=200)
    description:     Optional[str] = None
    required_skills: list[str]     = Field(default=[])
    daily_wage_rate: float          = Field(..., gt=0)
    duration_days:   int            = Field(..., gt=0)
    slots_available: int            = Field(default=1, gt=0, le=500)
    lat:             float          = Field(..., ge=-90,  le=90)
    lng:             float          = Field(..., ge=-180, le=180)
    location_name:   Optional[str] = Field(None, max_length=255)
    zone_name:       Optional[str] = Field(None, max_length=30)
    start_date:      Optional[str] = None   # ISO date string

class JobStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(open|closed|draft)$")

@app.post("/jobs", status_code=201, tags=["Jobs"])
async def post_job(
    body: JobCreate,
    user: dict = Depends(require_employer),
    db:   asyncpg.Connection = Depends(get_db),
):
    # Get employer profile id
    emp_id = await db.fetchval(
        "SELECT id FROM employer_profiles WHERE user_id=$1", UUID(user["sub"])
    )
    if not emp_id:
        raise HTTPException(status_code=404, detail="สร้าง Employer Profile ก่อน")

    clean_skills = list({s.strip().lower() for s in body.required_skills if s.strip()})

    start_date = None
    if body.start_date:
        from datetime import date
        try:
            start_date = date.fromisoformat(body.start_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="start_date format ไม่ถูกต้อง (YYYY-MM-DD)")

    row = await db.fetchrow(
        """
        INSERT INTO job_postings
            (employer_id, title, description, required_skills, daily_wage_rate,
             duration_days, slots_available, location, location_name, zone_name, start_date)
        VALUES
            ($1, $2, $3, $4, $5, $6, $7,
             ST_MakePoint($8, $9)::geography, $10, $11, $12)
        RETURNING id, title, status, created_at
        """,
        emp_id, body.title, body.description, clean_skills,
        body.daily_wage_rate, body.duration_days, body.slots_available,
        body.lng, body.lat, body.location_name, body.zone_name, start_date,
    )
    return dict(row)

@app.get("/jobs/mine", tags=["Jobs"])
async def get_my_jobs(
    user: dict = Depends(require_employer),
    db:   asyncpg.Connection = Depends(get_db),
):
    emp_id = await db.fetchval(
        "SELECT id FROM employer_profiles WHERE user_id=$1", UUID(user["sub"])
    )
    if not emp_id:
        return []

    rows = await db.fetch(
        """
        SELECT id, title, status, daily_wage_rate, duration_days,
               slots_available, slots_filled, location_name, zone_name,
               start_date, created_at
        FROM   job_postings
        WHERE  employer_id = $1
        ORDER  BY created_at DESC
        LIMIT  100
        """,
        emp_id,
    )
    return [dict(r) for r in rows]

@app.patch("/jobs/{job_id}/status", tags=["Jobs"])
async def update_job_status(
    job_id: UUID,
    body:   JobStatusUpdate,
    user:   dict = Depends(require_employer),
    db:     asyncpg.Connection = Depends(get_db),
):
    emp_id = await db.fetchval(
        "SELECT id FROM employer_profiles WHERE user_id=$1", UUID(user["sub"])
    )
    row = await db.fetchrow(
        "SELECT id FROM job_postings WHERE id=$1 AND employer_id=$2",
        job_id, emp_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="ไม่พบงาน หรือไม่มีสิทธิ์แก้ไข")
    await db.execute(
        "UPDATE job_postings SET status=$1 WHERE id=$2", body.status, job_id
    )
    return {"job_id": job_id, "status": body.status}


# ============================================================
# WORKER APPLICATIONS
# ============================================================

@app.get("/workers/applications", tags=["Worker"])
async def get_my_applications(
    user: dict = Depends(require_worker),
    db:   asyncpg.Connection = Depends(get_db),
):
    worker_id = await db.fetchval(
        "SELECT id FROM worker_profiles WHERE user_id=$1", UUID(user["sub"])
    )
    if not worker_id:
        return []

    rows = await db.fetch(
        """
        SELECT
            ja.id, ja.status, ja.match_score, ja.distance_km,
            ja.matched_skills, ja.employer_note, ja.applied_at,
            jp.id          AS job_id,
            jp.title       AS job_title,
            jp.daily_wage_rate,
            jp.duration_days,
            jp.location_name,
            ST_Y(jp.location::geometry) AS job_lat,
            ST_X(jp.location::geometry) AS job_lng
        FROM   job_applications ja
        JOIN   job_postings     jp ON jp.id = ja.job_id
        WHERE  ja.worker_id = $1
        ORDER  BY ja.applied_at DESC
        """,
        worker_id,
    )
    return [
        {
            "id":           str(r["id"]),
            "status":       r["status"],
            "match_score":  float(r["match_score"] or 0),
            "distance_km":  float(r["distance_km"] or 0),
            "matched_skills": r["matched_skills"] or [],
            "employer_note": r["employer_note"],
            "applied_at":   r["applied_at"].isoformat(),
            "maps_link":    (
                f"https://www.google.com/maps/dir/?api=1&destination={r['job_lat']},{r['job_lng']}"
                if r["status"] == "hired" else None
            ),
            "job": {
                "id":             str(r["job_id"]),
                "title":          r["job_title"],
                "daily_wage_rate": float(r["daily_wage_rate"]),
                "duration_days":  r["duration_days"],
                "location_name":  r["location_name"],
            }
        }
        for r in rows
    ]


# ============================================================
# MATCHING ENGINE (from matching_engine.py — wired with real auth)
# ============================================================

DEFAULT_RADIUS_KM = 10.0
MAX_RADIUS_KM     = 30.0
W_SKILLS   = 0.60
W_DISTANCE = 0.25
W_RATE     = 0.15

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
        ratio = worker_rate / job_rate
        rate_score = 1.0 if ratio <= 1.0 else (1.0 - (ratio - 1.0) / 0.2 if ratio <= 1.2 else 0.0)
    else:
        rate_score = 0.5

    raw   = W_SKILLS * skill_score + W_DISTANCE * distance_score + W_RATE * rate_score
    score = round(raw * 100, 2)
    return score, [s.title() for s in matched], [s.title() for s in missing]


class ApplyRequest(BaseModel):
    lat: float = Field(..., ge=-90,  le=90)
    lng: float = Field(..., ge=-180, le=180)

@app.post("/jobs/{job_id}/apply", status_code=201, tags=["Matching"])
async def apply_to_job(
    job_id: UUID,
    body:   ApplyRequest,
    user:   dict = Depends(require_worker),
    db:     asyncpg.Connection = Depends(get_db),
):
    job = await db.fetchrow(
        """
        SELECT id, required_skills, daily_wage_rate, slots_available, slots_filled, status
        FROM   job_postings
        WHERE  id = $1
        """,
        job_id,
    )
    if not job:
        raise HTTPException(status_code=404, detail="ไม่พบงาน")
    if job["status"] != "open":
        raise HTTPException(status_code=409, detail="งานนี้ปิดรับสมัครแล้ว")
    if job["slots_filled"] >= job["slots_available"]:
        raise HTTPException(status_code=409, detail="ที่นั่งเต็มแล้ว")

    worker = await db.fetchrow(
        "SELECT id, skills, daily_rate_expected FROM worker_profiles WHERE user_id=$1",
        UUID(user["sub"]),
    )
    if not worker:
        raise HTTPException(status_code=404, detail="สร้าง Worker Profile ก่อน")

    dist_row = await db.fetchrow(
        """
        SELECT ST_Distance(
            ST_MakePoint($1, $2)::geography,
            location
        ) / 1000.0 AS distance_km
        FROM job_postings WHERE id = $3
        """,
        body.lng, body.lat, job_id,
    )
    distance_km = float(dist_row["distance_km"])

    if distance_km > MAX_RADIUS_KM:
        raise HTTPException(
            status_code=400,
            detail=f"งานอยู่ห่าง {distance_km:.1f} กม. เกินรัศมี {MAX_RADIUS_KM} กม.",
        )

    score, matched_skills, missing_skills = compute_match_score(
        worker_skills   = worker["skills"] or [],
        required_skills = job["required_skills"] or [],
        distance_km     = distance_km,
        radius_km       = DEFAULT_RADIUS_KM,
        worker_rate     = worker["daily_rate_expected"],
        job_rate        = float(job["daily_wage_rate"]),
    )

    app_row = await db.fetchrow(
        """
        INSERT INTO job_applications
            (job_id, worker_id, status, match_score, distance_km, matched_skills)
        VALUES ($1, $2, 'applied', $3, $4, $5)
        ON CONFLICT (job_id, worker_id)
            DO UPDATE SET
                status         = 'applied',
                match_score    = EXCLUDED.match_score,
                distance_km    = EXCLUDED.distance_km,
                matched_skills = EXCLUDED.matched_skills,
                applied_at     = NOW()
        RETURNING id, status
        """,
        job_id, worker["id"], score, round(distance_km, 2), matched_skills,
    )

    # Notify employer (fire-and-forget — don't fail apply if notif fails)
    try:
        await db.execute(
            """
            INSERT INTO notifications (user_id, type, title, body)
            SELECT ep.user_id, 'new_applicant',
                   'มีผู้สมัครงานใหม่',
                   'คะแนน Match ' || $1 || '/100'
            FROM   job_postings jp
            JOIN   employer_profiles ep ON ep.id = jp.employer_id
            WHERE  jp.id = $2
            """,
            str(int(score)), job_id,
        )
    except Exception:
        pass

    return {
        "application_id": str(app_row["id"]),
        "status":         app_row["status"],
        "match_score":    score,
        "distance_km":    round(distance_km, 2),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
    }


@app.get("/jobs/nearby", tags=["Matching"])
async def get_nearby_jobs(
    lat:       float,
    lng:       float,
    radius_km: float = DEFAULT_RADIUS_KM,
    user:      dict  = Depends(require_worker),
    db:        asyncpg.Connection = Depends(get_db),
):
    radius_km = min(radius_km, MAX_RADIUS_KM)

    worker = await db.fetchrow(
        "SELECT skills, daily_rate_expected FROM worker_profiles WHERE user_id=$1",
        UUID(user["sub"]),
    )
    worker_skills = worker["skills"] if worker else []
    worker_rate   = worker["daily_rate_expected"] if worker else None

    rows = await db.fetch(
        """
        SELECT
            jp.id, jp.title, jp.required_skills, jp.daily_wage_rate,
            jp.duration_days,
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


@app.get("/jobs/{job_id}/candidates", tags=["Matching"])
async def get_candidates(
    job_id: UUID,
    user:   dict = Depends(require_employer),
    db:     asyncpg.Connection = Depends(get_db),
):
    # Verify job belongs to this employer
    emp_id = await db.fetchval(
        "SELECT id FROM employer_profiles WHERE user_id=$1", UUID(user["sub"])
    )
    job_check = await db.fetchval(
        "SELECT id FROM job_postings WHERE id=$1 AND employer_id=$2", job_id, emp_id
    )
    if not job_check:
        raise HTTPException(status_code=404, detail="ไม่พบงาน หรือไม่มีสิทธิ์ดู")

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
            "application_id":          str(r["application_id"]),
            "worker_id":               str(r["worker_id"]),
            "full_name":               r["full_name"],
            "background_check_status": r["background_check_status"],
            "daily_rate_expected":     float(r["daily_rate_expected"]) if r["daily_rate_expected"] else None,
            "match_score":             float(r["match_score"] or 0),
            "distance_km":             float(r["distance_km"] or 0),
            "matched_skills":          r["matched_skills"] or [],
            "missing_skills":          list(
                set(s.lower() for s in (r["required_skills"] or [])) -
                set(s.lower() for s in (r["matched_skills"] or []))
            ),
            "status": r["status"],
        }
        for r in rows
    ]


class DecisionRequest(BaseModel):
    decision: str = Field(..., pattern="^(hired|rejected|shortlisted)$")
    note:     Optional[str] = Field(None, max_length=500)

@app.patch("/applications/{app_id}/decide", tags=["Matching"])
async def decide_application(
    app_id: UUID,
    body:   DecisionRequest,
    user:   dict = Depends(require_employer),
    db:     asyncpg.Connection = Depends(get_db),
):
    row = await db.fetchrow(
        """
        SELECT ja.id, ja.status, ja.job_id, ja.worker_id,
               jp.slots_available, jp.slots_filled, jp.employer_id,
               jp.title          AS job_title,
               jp.location_name,
               ST_Y(jp.location::geometry) AS job_lat,
               ST_X(jp.location::geometry) AS job_lng
        FROM   job_applications ja
        JOIN   job_postings     jp ON jp.id = ja.job_id
        WHERE  ja.id = $1
        """,
        app_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="ไม่พบใบสมัคร")

    # Verify this employer owns the job
    emp_id = await db.fetchval(
        "SELECT id FROM employer_profiles WHERE user_id=$1", UUID(user["sub"])
    )
    if row["employer_id"] != emp_id:
        raise HTTPException(status_code=403, detail="ไม่มีสิทธิ์ตัดสินใจงานนี้")

    if row["status"] in ("hired", "rejected"):
        raise HTTPException(status_code=409, detail=f"ใบสมัครนี้ {row['status']} แล้ว")

    if body.decision == "hired" and row["slots_filled"] >= row["slots_available"]:
        raise HTTPException(status_code=409, detail="ที่นั่งเต็มแล้ว")

    async with db.transaction():
        await db.execute(
            """
            UPDATE job_applications
            SET    status = $1, employer_note = $2, decided_at = NOW()
            WHERE  id = $3
            """,
            body.decision, body.note, app_id,
        )
        if body.decision == "hired":
            await db.execute(
                """
                UPDATE job_postings
                SET    slots_filled = slots_filled + 1,
                       status = CASE WHEN slots_filled + 1 >= slots_available THEN 'filled' ELSE status END
                WHERE  id = $1
                """,
                row["job_id"],
            )

        notif_title = "ยินดีด้วย! คุณได้รับการคัดเลือก" if body.decision == "hired" else "ผลการสมัครงาน"

        if body.decision == "hired":
            # Generate Google Maps navigation link
            maps_link = f"https://www.google.com/maps/dir/?api=1&destination={row['job_lat']},{row['job_lng']}"
            place_name = row["location_name"] or "สถานที่ทำงาน"
            notif_body = (
                f"{body.note + ' | ' if body.note else ''}"
                f"📍 {place_name}\n"
                f"🗺️ นำทาง: {maps_link}"
            )
        else:
            notif_body = body.note or "ขออภัย ครั้งนี้ยังไม่ผ่านการคัดเลือก"

        try:
            await db.execute(
                """
                INSERT INTO notifications (user_id, type, title, body)
                SELECT wp.user_id, $1, $2, $3
                FROM   worker_profiles wp WHERE wp.id = $4
                """,
                body.decision, notif_title, notif_body, row["worker_id"],
            )
        except Exception:
            pass

    # ถ้า hired — return contact info ทันทีไม่ต้อง call ซ้ำ
    contact = None
    if body.decision == "hired":
        contact_row = await db.fetchrow(
            """
            SELECT wp.full_name, uw.phone AS worker_phone, uw.email AS worker_email
            FROM   worker_profiles wp
            JOIN   users uw ON uw.id = wp.user_id
            WHERE  wp.id = $1
            """,
            row["worker_id"],
        )
        if contact_row:
            contact = {
                "contact_name": contact_row["full_name"],
                "phone":        contact_row["worker_phone"],
                "email":        contact_row["worker_email"],
            }

    return {
        "application_id": str(app_id),
        "new_status":     body.decision,
        "contact":        contact,
    }


# ============================================================
# JOB CATEGORIES & TITLES (Master Data)
# ============================================================

@app.get("/job-categories", tags=["Master Data"])
async def get_job_categories(db: asyncpg.Connection = Depends(get_db)):
    rows = await db.fetch(
        "SELECT id, code, name_th, icon FROM job_categories ORDER BY sort_order"
    )
    return [dict(r) for r in rows]

@app.get("/job-categories/{category_code}/titles", tags=["Master Data"])
async def get_job_titles(
    category_code: str,
    db: asyncpg.Connection = Depends(get_db),
):
    rows = await db.fetch(
        """
        SELECT jt.id, jt.code, jt.name_th
        FROM   job_titles jt
        JOIN   job_categories jc ON jc.id = jt.category_id
        WHERE  jc.code = $1
        ORDER  BY jt.sort_order
        """,
        category_code,
    )
    if not rows:
        raise HTTPException(status_code=404, detail="ไม่พบ category นี้")
    return [dict(r) for r in rows]


# ============================================================
# CONTACT REVEAL — เปิดเผยเบอร์โทรเฉพาะคู่ที่ hired แล้ว
# ============================================================

@app.get("/applications/{app_id}/contact", tags=["Matching"])
async def get_contact(
    app_id: UUID,
    user:   dict = Depends(get_current_user),
    db:     asyncpg.Connection = Depends(get_db),
):
    user_id = UUID(user["sub"])
    role    = user["role"]

    row = await db.fetchrow(
        """
        SELECT
            ja.status,
            ja.worker_id,
            wp.user_id  AS worker_user_id,
            ep.user_id  AS employer_user_id,
            jp.title    AS job_title,
            -- worker info
            wp.full_name,
            uw.phone    AS worker_phone,
            uw.email    AS worker_email,
            -- employer info
            ep.company_name,
            ep.contact_person,
            ue.phone    AS employer_phone,
            ue.email    AS employer_email
        FROM   job_applications ja
        JOIN   worker_profiles   wp ON wp.id  = ja.worker_id
        JOIN   users             uw ON uw.id  = wp.user_id
        JOIN   job_postings      jp ON jp.id  = ja.job_id
        JOIN   employer_profiles ep ON ep.id  = jp.employer_id
        JOIN   users             ue ON ue.id  = ep.user_id
        WHERE  ja.id = $1
        """,
        app_id,
    )

    if not row:
        raise HTTPException(status_code=404, detail="ไม่พบใบสมัคร")

    # ต้อง hired เท่านั้น
    if row["status"] != "hired":
        raise HTTPException(status_code=403, detail="เปิดเผยข้อมูลติดต่อได้เฉพาะงานที่ hired แล้วเท่านั้น")

    # ตรวจสิทธิ์ — ต้องเป็นคู่ที่เกี่ยวข้องกัน
    if role == "worker" and row["worker_user_id"] != user_id:
        raise HTTPException(status_code=403, detail="ไม่มีสิทธิ์ดูข้อมูลนี้")
    if role == "employer" and row["employer_user_id"] != user_id:
        raise HTTPException(status_code=403, detail="ไม่มีสิทธิ์ดูข้อมูลนี้")

    # Worker เห็นข้อมูล Employer / Employer เห็นข้อมูล Worker
    if role == "worker":
        return {
            "job_title":    row["job_title"],
            "contact_name": row["contact_person"],
            "company_name": row["company_name"],
            "phone":        row["employer_phone"],
            "email":        row["employer_email"],
        }
    else:
        return {
            "job_title":    row["job_title"],
            "contact_name": row["full_name"],
            "phone":        row["worker_phone"],
            "email":        row["worker_email"],
        }


# ============================================================
# NOTIFICATIONS
# ============================================================

@app.get("/notifications", tags=["Notifications"])
async def get_notifications(
    limit:  int  = 20,
    unread: bool = False,
    user:   dict = Depends(get_current_user),
    db:     asyncpg.Connection = Depends(get_db),
):
    query = """
        SELECT id, type, title, body, is_read, created_at
        FROM   notifications
        WHERE  user_id = $1
    """
    params = [UUID(user["sub"])]
    if unread:
        query += " AND is_read = FALSE"
    query += " ORDER BY created_at DESC LIMIT $2"
    params.append(limit)

    rows = await db.fetch(query, *params)
    return [
        {
            "id":         str(r["id"]),
            "type":       r["type"],
            "title":      r["title"],
            "body":       r["body"],
            "is_read":    r["is_read"],
            "created_at": r["created_at"].isoformat(),
        }
        for r in rows
    ]

@app.get("/notifications/unread-count", tags=["Notifications"])
async def get_unread_count(
    user: dict = Depends(get_current_user),
    db:   asyncpg.Connection = Depends(get_db),
):
    count = await db.fetchval(
        "SELECT COUNT(*) FROM notifications WHERE user_id=$1 AND is_read=FALSE",
        UUID(user["sub"]),
    )
    return {"count": int(count)}

@app.patch("/notifications/read-all", tags=["Notifications"])
async def mark_all_read(
    user: dict = Depends(get_current_user),
    db:   asyncpg.Connection = Depends(get_db),
):
    await db.execute(
        "UPDATE notifications SET is_read=TRUE WHERE user_id=$1 AND is_read=FALSE",
        UUID(user["sub"]),
    )
    return {"status": "ok"}

@app.patch("/notifications/{notif_id}/read", tags=["Notifications"])
async def mark_read(
    notif_id: UUID,
    user:     dict = Depends(get_current_user),
    db:       asyncpg.Connection = Depends(get_db),
):
    await db.execute(
        "UPDATE notifications SET is_read=TRUE WHERE id=$1 AND user_id=$2",
        notif_id, UUID(user["sub"]),
    )
    return {"status": "ok"}


# ============================================================
# REVIEW SUMMARY
# ============================================================

@app.get("/workers/{worker_user_id}/review-summary", tags=["Reviews"])
async def get_worker_review_summary(
    worker_user_id: UUID,
    db: asyncpg.Connection = Depends(get_db),
):
    """Public summary — แสดงบน profile card"""
    row = await db.fetchrow(
        """
        SELECT
            COUNT(r.id)                                          AS total_reviews,
            ROUND(AVG(r.star_rating), 1)                        AS avg_stars,
            COUNT(r.id) FILTER (WHERE r.would_rehire = TRUE)    AS rehire_count,
            ARRAY_AGG(rt.tag_label ORDER BY cnt DESC)           AS top_tags
        FROM reviews r
        LEFT JOIN LATERAL (
            SELECT rt.tag_label, COUNT(*) AS cnt
            FROM   review_tag_selections rts
            JOIN   review_tags rt ON rt.id = rts.tag_id
            WHERE  rts.review_id = r.id
            GROUP  BY rt.tag_label
            ORDER  BY cnt DESC
            LIMIT  3
        ) rt ON TRUE
        WHERE  r.reviewee_id  = $1
          AND  r.is_visible   = TRUE
          AND  r.reviewer_role = 'employer'
        """,
        worker_user_id,
    )

    if not row or not row["total_reviews"]:
        return {"total_reviews": 0, "avg_stars": None, "rehire_pct": None, "top_tags": []}

    total     = int(row["total_reviews"])
    rehire    = int(row["rehire_count"] or 0)
    return {
        "total_reviews": total,
        "avg_stars":     float(row["avg_stars"]) if row["avg_stars"] else None,
        "rehire_pct":    round(rehire / total * 100) if total else None,
        "top_tags":      [t for t in (row["top_tags"] or []) if t][:3],
    }

@app.get("/employers/{employer_user_id}/review-summary", tags=["Reviews"])
async def get_employer_review_summary(
    employer_user_id: UUID,
    db: asyncpg.Connection = Depends(get_db),
):
    row = await db.fetchrow(
        """
        SELECT
            COUNT(r.id)                  AS total_reviews,
            ROUND(AVG(r.star_rating), 1) AS avg_stars
        FROM reviews r
        WHERE  r.reviewee_id   = $1
          AND  r.is_visible    = TRUE
          AND  r.reviewer_role = 'worker'
        """,
        employer_user_id,
    )
    if not row or not row["total_reviews"]:
        return {"total_reviews": 0, "avg_stars": None}
    return {
        "total_reviews": int(row["total_reviews"]),
        "avg_stars":     float(row["avg_stars"]) if row["avg_stars"] else None,
    }


# ============================================================
# BACKGROUND CHECK (Mock flow)
# ============================================================

@app.post("/workers/background-check/request", tags=["Trust & Safety"])
async def request_background_check(
    user: dict = Depends(require_worker),
    db:   asyncpg.Connection = Depends(get_db),
):
    """Worker ขอทำ background check — mock: auto-verify ใน 5 วิ"""
    worker = await db.fetchrow(
        "SELECT id, background_check_status FROM worker_profiles WHERE user_id=$1",
        UUID(user["sub"]),
    )
    if not worker:
        raise HTTPException(status_code=404, detail="สร้าง Worker Profile ก่อน")
    if worker["background_check_status"] == "verified":
        raise HTTPException(status_code=409, detail="ผ่านการตรวจสอบแล้ว")

    # Set pending
    await db.execute(
        "UPDATE worker_profiles SET background_check_status='pending' WHERE id=$1",
        worker["id"],
    )

    # Mock: auto-verify ทันที (production: ส่งไป 3rd party service)
    await db.execute(
        """
        UPDATE worker_profiles
        SET    background_check_status = 'verified',
               background_checked_at  = NOW()
        WHERE  id = $1
        """,
        worker["id"],
    )

    # Notify worker
    await db.execute(
        """
        INSERT INTO notifications (user_id, type, title, body)
        VALUES ($1, 'background_check', '✅ ผ่านการตรวจสอบแล้ว',
                'โปรไฟล์ของคุณได้รับ Badge "Verified" แล้ว นายจ้างจะเห็นคุณก่อนคนอื่น')
        """,
        UUID(user["sub"]),
    )

    return {"status": "verified", "message": "ผ่านการตรวจสอบแล้ว"}


# ============================================================
# EMPLOYER VERIFICATION (Mock flow)
# ============================================================

@app.post("/employers/verify/request", tags=["Trust & Safety"])
async def request_employer_verification(
    user: dict = Depends(require_employer),
    db:   asyncpg.Connection = Depends(get_db),
):
    """Employer ขอ verify บริษัท — mock: auto-verify"""
    emp = await db.fetchrow(
        "SELECT id, verified_status FROM employer_profiles WHERE user_id=$1",
        UUID(user["sub"]),
    )
    if not emp:
        raise HTTPException(status_code=404, detail="สร้าง Employer Profile ก่อน")
    if emp["verified_status"] == "verified":
        raise HTTPException(status_code=409, detail="ได้รับการยืนยันแล้ว")

    await db.execute(
        "UPDATE employer_profiles SET verified_status='verified' WHERE id=$1",
        emp["id"],
    )

    await db.execute(
        """
        INSERT INTO notifications (user_id, type, title, body)
        VALUES ($1, 'employer_verified', '✅ บริษัทได้รับการยืนยันแล้ว',
                'โปรไฟล์ของคุณได้รับ Badge "Verified Employer" แล้ว Worker จะเชื่อถือมากขึ้น')
        """,
        UUID(user["sub"]),
    )

    return {"status": "verified", "message": "บริษัทได้รับการยืนยันแล้ว"}


# ============================================================
# REPORT & BLOCK
# ============================================================

class ReportRequest(BaseModel):
    reported_user_id: UUID
    reason:           str = Field(..., pattern="^(spam|fake|harassment|payment_fraud|other)$")
    detail:           Optional[str] = Field(None, max_length=500)

class BlockRequest(BaseModel):
    blocked_user_id: UUID

@app.post("/users/report", status_code=201, tags=["Trust & Safety"])
async def report_user(
    body: ReportRequest,
    user: dict = Depends(get_current_user),
    db:   asyncpg.Connection = Depends(get_db),
):
    reporter_id = UUID(user["sub"])
    if reporter_id == body.reported_user_id:
        raise HTTPException(status_code=400, detail="ไม่สามารถรายงานตัวเองได้")

    # Check ว่า reported user มีอยู่จริง
    exists = await db.fetchval(
        "SELECT id FROM users WHERE id=$1", body.reported_user_id
    )
    if not exists:
        raise HTTPException(status_code=404, detail="ไม่พบผู้ใช้")

    # Upsert report (1 คน report 1 คนได้ครั้งเดียว ต่อ reason)
    await db.execute(
        """
        INSERT INTO user_reports (reporter_id, reported_user_id, reason, detail)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (reporter_id, reported_user_id, reason) DO UPDATE
            SET detail     = EXCLUDED.detail,
                updated_at = NOW()
        """,
        reporter_id, body.reported_user_id, body.reason, body.detail,
    )

    # ถ้า report เยอะกว่า 3 ครั้ง จาก user ต่างกัน → auto-flag
    report_count = await db.fetchval(
        """
        SELECT COUNT(DISTINCT reporter_id) FROM user_reports
        WHERE  reported_user_id = $1
        """,
        body.reported_user_id,
    )
    if report_count >= 3:
        await db.execute(
            "UPDATE users SET is_active=FALSE WHERE id=$1 AND is_active=TRUE",
            body.reported_user_id,
        )

    return {"status": "reported", "message": "รายงานถูกส่งแล้ว ทีมงานจะตรวจสอบ"}


@app.post("/users/block", status_code=201, tags=["Trust & Safety"])
async def block_user(
    body: BlockRequest,
    user: dict = Depends(get_current_user),
    db:   asyncpg.Connection = Depends(get_db),
):
    blocker_id = UUID(user["sub"])
    if blocker_id == body.blocked_user_id:
        raise HTTPException(status_code=400, detail="ไม่สามารถบล็อคตัวเองได้")

    await db.execute(
        """
        INSERT INTO user_blocks (blocker_id, blocked_user_id)
        VALUES ($1, $2)
        ON CONFLICT DO NOTHING
        """,
        blocker_id, body.blocked_user_id,
    )
    return {"status": "blocked"}


@app.delete("/users/block/{blocked_user_id}", tags=["Trust & Safety"])
async def unblock_user(
    blocked_user_id: UUID,
    user: dict = Depends(get_current_user),
    db:   asyncpg.Connection = Depends(get_db),
):
    await db.execute(
        "DELETE FROM user_blocks WHERE blocker_id=$1 AND blocked_user_id=$2",
        UUID(user["sub"]), blocked_user_id,
    )
    return {"status": "unblocked"}


@app.get("/users/blocked", tags=["Trust & Safety"])
async def get_blocked_users(
    user: dict = Depends(get_current_user),
    db:   asyncpg.Connection = Depends(get_db),
):
    rows = await db.fetch(
        """
        SELECT u.id, u.email, u.role, ub.created_at AS blocked_at
        FROM   user_blocks ub
        JOIN   users u ON u.id = ub.blocked_user_id
        WHERE  ub.blocker_id = $1
        ORDER  BY ub.created_at DESC
        """,
        UUID(user["sub"]),
    )
    return [{"user_id": str(r["id"]), "email": r["email"],
             "role": r["role"], "blocked_at": r["blocked_at"].isoformat()} for r in rows]


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health", tags=["System"])
async def health(db: asyncpg.Connection = Depends(get_db)):
    version = await db.fetchval("SELECT version()")
    return {
        "status":   "ok",
        "db":       "connected",
        "pg":       version.split(" ")[1] if version else "unknown",
    }


# ============================================================
# REVIEW SYSTEM
# ============================================================

class ReviewSubmit(BaseModel):
    application_id: UUID
    star_rating:    int       = Field(..., ge=1, le=5)
    tag_keys:       list[str] = Field(default=[])
    would_rehire:   Optional[bool] = None  # employer only

@app.get("/review-tags", tags=["Reviews"])
async def get_review_tags(
    target_role: str,
    db: asyncpg.Connection = Depends(get_db),
):
    if target_role not in ("worker", "employer"):
        raise HTTPException(status_code=400, detail="target_role ต้องเป็น worker หรือ employer")
    rows = await db.fetch(
        "SELECT id, tag_key, tag_label, is_positive FROM review_tags WHERE target_role=$1 ORDER BY sort_order",
        target_role,
    )
    return [dict(r) for r in rows]


@app.post("/reviews", status_code=201, tags=["Reviews"])
async def submit_review(
    body: ReviewSubmit,
    user: dict = Depends(get_current_user),
    db:   asyncpg.Connection = Depends(get_db),
):
    reviewer_id   = UUID(user["sub"])
    reviewer_role = user["role"]

    app_row = await db.fetchrow(
        """
        SELECT ja.id, ja.worker_id, ja.job_id,
               wp.user_id AS worker_user_id,
               ep.user_id AS employer_user_id
        FROM   job_applications ja
        JOIN   worker_profiles   wp ON wp.id = ja.worker_id
        JOIN   job_postings      jp ON jp.id = ja.job_id
        JOIN   employer_profiles ep ON ep.id = jp.employer_id
        WHERE  ja.id = $1 AND ja.status = 'hired'
        """,
        body.application_id,
    )
    if not app_row:
        raise HTTPException(status_code=404, detail="ไม่พบงานที่ได้รับการจ้าง")

    if reviewer_role == "worker" and app_row["worker_user_id"] != reviewer_id:
        raise HTTPException(status_code=403, detail="ไม่มีสิทธิ์ review งานนี้")
    if reviewer_role == "employer" and app_row["employer_user_id"] != reviewer_id:
        raise HTTPException(status_code=403, detail="ไม่มีสิทธิ์ review งานนี้")

    reviewee_id  = app_row["employer_user_id"] if reviewer_role == "worker" else app_row["worker_user_id"]
    would_rehire = body.would_rehire if reviewer_role == "employer" else None

    try:
        review = await db.fetchrow(
            """
            INSERT INTO reviews
                (application_id, reviewer_id, reviewee_id, reviewer_role, star_rating, would_rehire)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id
            """,
            body.application_id, reviewer_id, reviewee_id,
            reviewer_role, body.star_rating, would_rehire,
        )
    except asyncpg.UniqueViolationError:
        raise HTTPException(status_code=409, detail="คุณ review งานนี้ไปแล้ว")

    if body.tag_keys:
        tag_rows = await db.fetch(
            "SELECT id FROM review_tags WHERE tag_key = ANY($1::text[])", body.tag_keys,
        )
        if tag_rows:
            await db.executemany(
                "INSERT INTO review_tag_selections (review_id, tag_id) VALUES ($1, $2)",
                [(review["id"], r["id"]) for r in tag_rows],
            )

    # Auto-reveal ถ้าทั้งคู่ส่งแล้ว
    count = await db.fetchval(
        "SELECT COUNT(*) FROM reviews WHERE application_id=$1", body.application_id,
    )
    if count >= 2:
        await db.execute(
            "UPDATE reviews SET is_visible=TRUE, revealed_at=NOW() WHERE application_id=$1 AND is_visible=FALSE",
            body.application_id,
        )

    return {"review_id": str(review["id"]), "status": "submitted"}


@app.get("/reviews/me", tags=["Reviews"])
async def get_my_reviews(
    user: dict = Depends(get_current_user),
    db:   asyncpg.Connection = Depends(get_db),
):
    rows = await db.fetch(
        """
        SELECT r.id, r.star_rating, r.would_rehire, r.reviewer_role,
               r.revealed_at, jp.title AS job_title,
               ARRAY_AGG(rt.tag_label ORDER BY rt.sort_order)
                   FILTER (WHERE rt.id IS NOT NULL) AS tags
        FROM   reviews r
        JOIN   job_applications ja ON ja.id = r.application_id
        JOIN   job_postings     jp ON jp.id = ja.job_id
        LEFT JOIN review_tag_selections rts ON rts.review_id = r.id
        LEFT JOIN review_tags           rt  ON rt.id = rts.tag_id
        WHERE  r.reviewee_id = $1 AND r.is_visible = TRUE
        GROUP  BY r.id, jp.title
        ORDER  BY r.revealed_at DESC
        """,
        UUID(user["sub"]),
    )
    return [
        {
            "review_id":     str(r["id"]),
            "star_rating":   r["star_rating"],
            "would_rehire":  r["would_rehire"],
            "reviewer_role": r["reviewer_role"],
            "job_title":     r["job_title"],
            "tags":          r["tags"] or [],
            "revealed_at":   r["revealed_at"].isoformat() if r["revealed_at"] else None,
        }
        for r in rows
    ]


@app.get("/reviews/pending", tags=["Reviews"])
async def get_pending_reviews(
    user: dict = Depends(get_current_user),
    db:   asyncpg.Connection = Depends(get_db),
):
    user_id = UUID(user["sub"])
    role    = user["role"]

    if role == "worker":
        rows = await db.fetch(
            """
            SELECT ja.id AS application_id, jp.title AS job_title,
                   ep.company_name, ja.decided_at
            FROM   job_applications ja
            JOIN   job_postings      jp ON jp.id = ja.job_id
            JOIN   employer_profiles ep ON ep.id = jp.employer_id
            JOIN   worker_profiles   wp ON wp.id = ja.worker_id
            WHERE  wp.user_id = $1 AND ja.status = 'hired'
              AND  NOT EXISTS (
                  SELECT 1 FROM reviews r
                  WHERE  r.application_id = ja.id AND r.reviewer_id = $1
              )
            ORDER BY ja.decided_at DESC
            """,
            user_id,
        )
        return [{"application_id": str(r["application_id"]), "job_title": r["job_title"],
                 "company_name": r["company_name"], "review_target": "employer",
                 "decided_at": r["decided_at"].isoformat() if r["decided_at"] else None}
                for r in rows]
    else:
        rows = await db.fetch(
            """
            SELECT ja.id AS application_id, jp.title AS job_title,
                   wp.full_name AS worker_name, ja.decided_at
            FROM   job_applications ja
            JOIN   job_postings      jp ON jp.id = ja.job_id
            JOIN   employer_profiles ep ON ep.id = jp.employer_id
            JOIN   worker_profiles   wp ON wp.id = ja.worker_id
            WHERE  ep.user_id = $1 AND ja.status = 'hired'
              AND  NOT EXISTS (
                  SELECT 1 FROM reviews r
                  WHERE  r.application_id = ja.id AND r.reviewer_id = $1
              )
            ORDER BY ja.decided_at DESC
            """,
            user_id,
        )
        return [{"application_id": str(r["application_id"]), "job_title": r["job_title"],
                 "worker_name": r["worker_name"], "review_target": "worker",
                 "decided_at": r["decided_at"].isoformat() if r["decided_at"] else None}
                for r in rows]
