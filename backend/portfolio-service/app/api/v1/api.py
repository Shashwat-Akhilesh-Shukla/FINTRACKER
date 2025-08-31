from fastapi import APIRouter
from app.api.v1.endpoints import portfolio, holdings, transactions, market

"""
API router configuration that:
- Centralizes all API route definitions
- Organizes endpoints by category
- Provides health check endpoint
- Manages API versioning
"""

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    portfolio.router, 
    tags=["portfolio"]
)

api_router.include_router(
    holdings.router, 
    tags=["holdings"]
)

api_router.include_router(
    transactions.router, 
    tags=["transactions"]
)

api_router.include_router(
    market.router,
    tags=["market"]
)

@api_router.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "service": "portfolio-service",
        "version": "1.0.0"
    }


