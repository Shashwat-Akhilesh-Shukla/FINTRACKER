# app/core/config.py
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    APP_NAME: str = "FinTracker News Service"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str

    # External APIs
    NEWS_API_KEY: str
    FINNHUB_API_KEY: str
    ALPHA_VANTAGE_API_KEY: str   # <-- matches .env

    # Service URLs
    AUTH_SERVICE_URL: str
    PORTFOLIO_SERVICE_URL: str

    # News settings
    NEWS_UPDATE_INTERVAL: int = 900
    MAX_NEWS_ITEMS: int = 100
    NEWS_RETENTION_DAYS: int = 60

    # CORS
    BACKEND_CORS_ORIGINS: List[str]

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int
    RATE_LIMIT_WINDOW: int

    # Logging
    LOG_LEVEL: str = "INFO"

    # Security
    SECRET_KEY: str

    # External API Rate Limits
    NEWS_API_REQUESTS_PER_DAY: int
    FINNHUB_REQUESTS_PER_MINUTE: int
    ALPHA_VANTAGE_REQUESTS_PER_MINUTE: int

    # News Processing
    MIN_RELEVANCE_SCORE: float
    AUTO_FEATURE_THRESHOLD: float
    SENTIMENT_CONFIDENCE_THRESHOLD: float

    # DB Pool
    DB_POOL_SIZE: int
    DB_MAX_OVERFLOW: int
    DB_POOL_PRE_PING: bool

    # Cache
    CACHE_TTL_SECONDS: int
    CACHE_MAX_ITEMS: int

    # RSS
    RSS_TIMEOUT_SECONDS: int
    RSS_MAX_ARTICLES_PER_FEED: int
    RSS_UPDATE_INTERVAL: int

    # Performance
    MAX_CONCURRENT_REQUESTS: int
    REQUEST_TIMEOUT: int
    WORKER_CONNECTIONS: int

    class Config:
        env_file = ".env"


settings = Settings()
