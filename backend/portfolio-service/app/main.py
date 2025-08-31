"""
Main FastAPI application entry point that:
- Initializes the FastAPI application
- Sets up CORS middleware
- Creates database tables on startup
- Manages application lifecycle (startup/shutdown)
- Includes API routes
- Provides basic health check endpoint
"""


# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.api import api_router
from app.services.market_data_service import market_data_service

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"Starting {settings.APP_NAME}")
    yield
    # Shutdown
    await market_data_service.close()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "portfolio-service"}
