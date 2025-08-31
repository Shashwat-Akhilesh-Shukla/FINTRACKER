# app/schemas/portfolio.py
from pydantic import BaseModel, validator
from datetime import datetime
from typing import List, Optional

class PortfolioBase(BaseModel):
    name: str
    description: Optional[str] = None

class PortfolioCreate(PortfolioBase):
    pass

class PortfolioUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class PortfolioSummary(BaseModel):
    total_value: float
    total_cost: float
    total_return: float
    total_return_percent: float
    day_change: float
    day_change_percent: float
    cash_balance: float
    dividend_income: float
    last_sync: Optional[datetime]

class PortfolioMetrics(BaseModel):
    sharpe_ratio: float
    beta: float
    alpha: float
    var_95: float
    max_drawdown: float
    volatility: float
    annualized_return: float
    information_ratio: float

class PortfolioResponse(PortfolioBase):
    id: int
    user_id: int
    summary: PortfolioSummary
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# app/schemas/holding.py
class HoldingBase(BaseModel):
    symbol: str
    shares: float
    avg_cost: float

class HoldingCreate(HoldingBase):
    pass

class HoldingUpdate(BaseModel):
    shares: Optional[float] = None
    avg_cost: Optional[float] = None

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
    sector: Optional[str]
    industry: Optional[str]
    last_price_update: Optional[datetime]
    
    class Config:
        from_attributes = True

# app/schemas/transaction.py
class TransactionBase(BaseModel):
    symbol: str
    type: str
    shares: float
    price: float
    fees: float = 0.0
    note: Optional[str] = None

class TransactionCreate(TransactionBase):
    transaction_date: Optional[datetime] = None
    
    @validator('type')
    def validate_type(cls, v):
        if v not in ['BUY', 'SELL', 'DIVIDEND']:
            raise ValueError('Type must be BUY, SELL, or DIVIDEND')
        return v

class TransactionResponse(TransactionBase):
    id: int
    total_amount: float
    transaction_date: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

# Portfolio data validation schemas that:
# - Define data structures for portfolio operations
# - Validate portfolio creation and updates
# - Structure portfolio summary responses
# - Define portfolio metrics format
