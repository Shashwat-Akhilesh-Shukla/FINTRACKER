# app/core/config.py
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import validator
import secrets

class Settings(BaseSettings):
    # App
    APP_NAME: str = "FinTracker Auth Service"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # Database
    DATABASE_URL: str = "postgresql://fintracker:fintracker123@localhost:5432/fintracker_auth"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "https://localhost:3000"]
    
    # Email (for future use)
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600  # 1 hour
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
