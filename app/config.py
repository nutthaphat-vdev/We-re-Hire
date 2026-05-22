"""
config.py — App settings จาก environment variables
"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url:  str
    jwt_secret:    str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24  # 1 วัน

    class Config:
        env_file = ".env"

settings = Settings()
