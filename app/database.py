"""
database.py — asyncpg connection pool
"""
import asyncpg
from app.config import settings

_pool: asyncpg.Pool | None = None


async def create_pool():
    global _pool
    _pool = await asyncpg.create_pool(
        dsn=settings.database_url,
        min_size=2,
        max_size=10,
    )


async def close_pool():
    if _pool:
        await _pool.close()


async def get_db() -> asyncpg.Connection:
    async with _pool.acquire() as conn:
        yield conn
