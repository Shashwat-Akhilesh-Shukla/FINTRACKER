from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.api.deps import get_current_user
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.services.portfolio_service import PortfolioService

router = APIRouter()

@router.get("/get_transactions", response_model=List[TransactionResponse])
async def get_transactions(
    symbol: Optional[str] = Query(None, description="Filter by stock symbol"),
    transaction_type: Optional[str] = Query(None, description="Filter by transaction type"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    limit: int = Query(50, le=200, description="Limit number of results"),
    offset: int = Query(0, description="Offset for pagination"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get transactions with optional filtering"""
    service = PortfolioService(db)
    transactions = await service.get_transactions(
        user_id=current_user["user_id"],
        symbol=symbol,
        transaction_type=transaction_type,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset
    )
    
    # Explicitly map the transaction fields to match TransactionResponse schema
    return [
        TransactionResponse(
            id=tx.id,
            portfolio_id=tx.portfolio_id,
            symbol=tx.symbol,
            type=tx.type,
            shares=tx.shares,
            price=tx.price,
            total_amount=tx.total_amount,
            fees=tx.fees,
            transaction_date=tx.transaction_date,
            note=tx.note,
            created_at=tx.created_at
        ) for tx in transactions
    ]

@router.post("/add_transaction", response_model=TransactionResponse)
async def add_transaction(
    transaction_data: TransactionCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a new transaction"""
    service = PortfolioService(db)
    return await service.add_transaction(current_user["user_id"], transaction_data)

@router.get("/get_{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int = Path(..., description="Transaction ID"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific transaction by ID"""
    service = PortfolioService(db)
    transaction = await service.get_transaction(transaction_id, current_user["user_id"])
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.delete("/del_{transaction_id}")
async def delete_transaction(
    transaction_id: int = Path(..., description="Transaction ID"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a transaction"""
    service = PortfolioService(db)
    success = await service.delete_transaction(transaction_id, current_user["user_id"])
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Transaction deleted successfully"}

@router.get("/summary/stats")
async def get_transaction_stats(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get transaction statistics"""
    service = PortfolioService(db)
    return await service.get_transaction_stats(current_user["user_id"])
