# app/models/portfolio.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Portfolio(Base):
    """
    Portfolio database model that:
    - Defines portfolio table structure
    - Manages portfolio metrics and relationships
    - Tracks portfolio performance and cash balance
    - Maintains timestamps and user associations
    """
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    name = Column(String, nullable=False, default="Default Portfolio")
    description = Column(String, nullable=True)
    
    # Portfolio totals (calculated fields)
    total_value = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    total_return = Column(Float, default=0.0)
    total_return_percent = Column(Float, default=0.0)
    day_change = Column(Float, default=0.0)
    day_change_percent = Column(Float, default=0.0)
    cash_balance = Column(Float, default=0.0)
    dividend_income = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_sync = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    holdings = relationship("Holding", back_populates="portfolio", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="portfolio", cascade="all, delete-orphan")

