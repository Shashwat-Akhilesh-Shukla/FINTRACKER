'''
Configuration management that:
- Defines application settings using Pydantic
- Loads environment variables
- Manages critical configuration like database URLs, API keys, security settings
- Controls CORS, database pools, and caching parameters
'''


from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str
    VERSION: str
    DEBUG: bool
    API_V1_STR: str

    TV_USER: str
    TV_PASS: str
    
    DATABASE_URL: str
    REDIS_URL: str

    ALPHA_VANTAGE_API_KEY: str
    FINNHUB_API_KEY: str

    AUTH_SERVICE_URL: str
    NEWS_SERVICE_URL: str

    MARKET_DATA_UPDATE_INTERVAL: int
    MARKET_DATA_CACHE_TTL: int

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_DAYS: int
    ALGORITHM: str

    BACKEND_CORS_ORIGINS: List[str]

    DB_POOL_SIZE: int
    DB_MAX_OVERFLOW: int
    CACHE_TTL: int
    REQUEST_TIMEOUT: int

    class Config:
        env_file = ".env"

settings = Settings()
