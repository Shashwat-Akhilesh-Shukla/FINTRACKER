# app/api/v1/endpoints/portfolio.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.api.deps import get_current_user
from app.schemas.portfolio import PortfolioSummary, PortfolioMetrics, PortfolioResponse
from app.schemas.holding import HoldingCreate, HoldingResponse
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.services.portfolio_service import PortfolioService

router = APIRouter()

@router.get("/summary", response_model=PortfolioSummary)
async def get_portfolio_summary(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get portfolio summary with real-time data"""
    service = PortfolioService(db)
    return await service.get_portfolio_summary(current_user["user_id"])

@router.get("/holdings", response_model=List[HoldingResponse])
async def get_holdings(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all holdings"""
    service = PortfolioService(db)
    return await service.get_holdings(current_user["user_id"])

@router.post("/holdings", response_model=HoldingResponse)
async def add_holding(
    holding_data: HoldingCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a new holding"""
    service = PortfolioService(db)
    return await service.add_holding(current_user["user_id"], holding_data)

@router.get("/metrics")
async def get_portfolio_metrics(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get advanced portfolio metrics"""
    service = PortfolioService(db)
    return await service.get_portfolio_metrics(current_user["user_id"])

@router.get("/history")
async def get_portfolio_history(
    timeframe: str = "1M",
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get portfolio historical performance"""
    # This would be implemented with stored daily portfolio values
    # For now, returning mock data structure
    return [
        {"date": "2024-01-01", "value": 100000, "change": 0, "changePercent": 0},
        # ... more historical data
    ]
