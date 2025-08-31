from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.api.deps import get_current_user
from app.schemas.holding import HoldingCreate, HoldingUpdate, HoldingResponse
from app.services.portfolio_service import PortfolioService

router = APIRouter()

@router.get("/get_holdings", response_model=List[HoldingResponse])
async def get_holdings(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all holdings for the current user's portfolio"""
    service = PortfolioService(db)
    return await service.get_holdings(current_user["user_id"])

@router.post("/add_holding", response_model=HoldingResponse)
async def add_holding(
    holding_data: HoldingCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a new holding to the portfolio"""
    service = PortfolioService(db)
    return await service.add_holding(current_user["user_id"], holding_data)

@router.get("/get_holding_by_ID_{holding_id}", response_model=HoldingResponse)
async def get_holding(
    holding_id: int = Path(..., description="Holding ID"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific holding by ID"""
    service = PortfolioService(db)
    holding = await service.get_holding(holding_id, current_user["user_id"])
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")
    return holding

@router.put("/update_holding_by_ID_{holding_id}", response_model=HoldingResponse)
async def update_holding(
    holding_id: int = Path(..., description="Holding ID"),
    holding_update: HoldingUpdate = ...,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a holding"""
    service = PortfolioService(db)
    holding = await service.update_holding(holding_id, current_user["user_id"], holding_update)
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")
    return holding

@router.delete("/delete_holding_by_ID_{holding_id}")
async def delete_holding(
    holding_id: int = Path(..., description="Holding ID"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a holding"""
    service = PortfolioService(db)
    success = await service.delete_holding(holding_id, current_user["user_id"])
    if not success:
        raise HTTPException(status_code=404, detail="Holding not found")
    return {"message": "Holding deleted successfully"}
