from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Holding(Base):
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    symbol = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    
    # Position data
    shares = Column(Float, nullable=False)
    avg_cost = Column(Float, nullable=False)
    current_price = Column(Float, default=0.0)
    market_value = Column(Float, default=0.0)
    
    # Performance metrics
    day_change = Column(Float, default=0.0)
    day_change_percent = Column(Float, default=0.0)
    total_return = Column(Float, default=0.0)
    total_return_percent = Column(Float, default=0.0)
    weight = Column(Float, default=0.0)
    
    # Stock metadata
    sector = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    market_cap = Column(Float, nullable=True)
    pe_ratio = Column(Float, nullable=True)
    dividend_yield = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_price_update = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="holdings")

    def __repr__(self):
        return f"<Holding(symbol={self.symbol}, shares={self.shares})>"

"""
Holding database model that:
- Defines structure for portfolio holdings
- Tracks position sizes and performance metrics
- Stores stock metadata and current values
- Manages relationship with portfolio
"""
