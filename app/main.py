"""
main.py — FastAPI app entry point
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.database import create_pool, close_pool
from app.routers import workers, auth, employers, matching
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_pool()
    yield
    await close_pool()


app = FastAPI(
    title="Daily Wage Matchmaking API",
    description="แพลตฟอร์มจ้างงานรายวัน — BKK MVP",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(workers.router)
app.include_router(matching.router)
app.include_router(employers.router)

# Health check
@app.get("/health", tags=["System"])
async def health():
    return {"status": "ok"}
