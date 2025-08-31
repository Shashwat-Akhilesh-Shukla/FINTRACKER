from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional

class TransactionBase(BaseModel):
    symbol: str
    type: str
    shares: float
    price: float
    fees: Optional[float] = 0.0
    note: Optional[str] = None
    transaction_date: Optional[datetime] = None

    @validator('symbol')
    def validate_symbol(cls, v):
        return v.upper()

    @validator('type')
    def validate_type(cls, v):
        if v.upper() not in ['BUY', 'SELL', 'DIVIDEND']:
            raise ValueError('Type must be BUY, SELL, or DIVIDEND')
        return v.upper()

    @validator('shares', 'price')
    def validate_positive(cls, v):
        if v <= 0:
            raise ValueError('Value must be positive')
        return v

    @validator('fees')
    def validate_fees(cls, v):
        if v is not None and v < 0:
            raise ValueError('Fees cannot be negative')
        return v

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(BaseModel):
    id: int
    portfolio_id: int
    symbol: str
    type: str
    shares: float
    price: float
    total_amount: float
    fees: Optional[float] = 0.0
    transaction_date: datetime
    note: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

"""
Transaction data validation schemas that:
- Validate transaction data
- Enforce transaction type constraints
- Define transaction response format
- Handle transaction metadata
"""
