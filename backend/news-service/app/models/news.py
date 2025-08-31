# app/models/news.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class NewsArticle(Base):
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True)  # Unique ID from news source
    
    # Article content
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    url = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    
    # Source information
    source = Column(String, nullable=False)
    author = Column(String, nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=False)
    
    # Analysis
    sentiment = Column(String, nullable=True)  # positive, negative, neutral
    sentiment_score = Column(Float, nullable=True)  # -1 to 1
    relevance_score = Column(Float, default=0.0)
    
    # Categorization
    category = Column(String, nullable=True)  # markets, earnings, crypto, etc.
    symbols = Column(JSON, nullable=True)  # Related stock symbols
    tags = Column(JSON, nullable=True)  # Topic tags
    
    # Engagement metrics
    views = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
