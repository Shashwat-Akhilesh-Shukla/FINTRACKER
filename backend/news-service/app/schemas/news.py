# app/schemas/news.py
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import List, Optional

class NewsArticleBase(BaseModel):
    title: str
    summary: Optional[str] = None
    url: str
    source: str
    author: Optional[str] = None
    published_at: datetime

class NewsArticleCreate(NewsArticleBase):
    external_id: str
    content: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    symbols: Optional[List[str]] = None
    tags: Optional[List[str]] = None

class NewsArticleResponse(NewsArticleBase):
    id: int
    external_id: str
    content: Optional[str]
    image_url: Optional[str]
    sentiment: Optional[str]
    sentiment_score: Optional[float]
    relevance_score: float
    category: Optional[str]
    symbols: Optional[List[str]]
    tags: Optional[List[str]]
    views: int
    is_featured: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class NewsSearchParams(BaseModel):
    q: Optional[str] = None
    symbols: Optional[List[str]] = None
    category: Optional[str] = None
    sentiment: Optional[str] = None
    limit: int = 20
    offset: int = 0
