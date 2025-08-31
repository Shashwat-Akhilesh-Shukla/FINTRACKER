from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional

class HoldingBase(BaseModel):
    symbol: str
    shares: float
    avg_cost: float

    @validator('symbol')
    def validate_symbol(cls, v):
        return v.upper()

    @validator('shares', 'avg_cost')
    def validate_positive(cls, v):
        if v <= 0:
            raise ValueError('Value must be positive')
        return v

class HoldingCreate(HoldingBase):
    pass

class HoldingUpdate(BaseModel):
    shares: Optional[float] = None
    avg_cost: Optional[float] = None

    @validator('shares', 'avg_cost')
    def validate_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Value must be positive')
        return v

class HoldingResponse(HoldingBase):
    id: int
    name: str
    current_price: float
    market_value: float
    day_change: float
    day_change_percent: float
    total_return: float
    total_return_percent: float
    weight: float
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    last_price_update: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

"""
Holding data validation schemas that:
- Validate holding creation and updates
- Enforce data type and value constraints
- Define holding response structure
- Handle holding metadata validation
"""
