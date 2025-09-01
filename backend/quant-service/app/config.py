from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "Quant Analytics Service"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str
    
    # Security
    AUTH_SERVICE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    
    # Cache
    REDIS_URL: str = "redis://localhost:6379/1"
    CACHE_TTL: int = 300
    
    # Performance
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    class Config:
        env_file = ".env"

settings = Settings()
