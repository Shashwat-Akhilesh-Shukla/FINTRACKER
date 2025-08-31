# app/api/v1/api.py
from fastapi import APIRouter
from app.api.v1.endpoints import news

api_router = APIRouter()

# Include news endpoints
api_router.include_router(
    news.router, 
    # prefix="/market/news", 
    tags=["news"]
)

# Health check for news service
@api_router.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "service": "news-service",
        "version": "1.0.0"
    }
