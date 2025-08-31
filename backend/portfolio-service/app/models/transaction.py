from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    symbol = Column(String, nullable=False, index=True)
    
    # Transaction details
    type = Column(String, nullable=False)  # BUY, SELL, DIVIDEND
    shares = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    fees = Column(Float, default=0.0)
    
    # Metadata
    transaction_date = Column(DateTime(timezone=True), nullable=False)
    note = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction(symbol={self.symbol}, type={self.type}, shares={self.shares})>"

    """
    Transaction database model that:
    - Records all portfolio transactions
    - Tracks buy/sell/dividend events
    - Stores transaction details and fees
    - Maintains audit trail with timestamps
    """
