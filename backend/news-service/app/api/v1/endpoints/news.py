# app/api/v1/endpoints/news.py
from fastapi import APIRouter, Depends, Query, HTTPException, Path
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.news import NewsArticleResponse, NewsSearchParams
from app.services.news_service import NewsService
from app.api.deps import get_current_user_optional, get_current_user

router = APIRouter()

@router.get("/", response_model=List[NewsArticleResponse])
async def get_news(
    q: Optional[str] = Query(None, description="Search query for title, summary, or content"),
    symbols: Optional[str] = Query(None, description="Comma-separated stock symbols (e.g., AAPL,GOOGL,MSFT)"),
    category: Optional[str] = Query(None, description="News category filter"),
    sentiment: Optional[str] = Query(None, description="Sentiment filter: positive, negative, or neutral"),
    limit: int = Query(20, le=100, ge=1, description="Number of articles to return (max 100)"),
    offset: int = Query(0, ge=0, description="Number of articles to skip for pagination"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Get news articles with optional filtering and search.
    
    - **q**: Search in title, summary, and content
    - **symbols**: Filter by stock symbols (comma-separated)
    - **category**: Filter by category (earnings, markets, crypto, etc.)
    - **sentiment**: Filter by sentiment analysis result
    - **limit**: Number of results (1-100)
    - **offset**: Pagination offset
    """
    try:
        # Parse symbols if provided
        symbol_list = None
        if symbols:
            symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
        
        # Create search parameters
        search_params = NewsSearchParams(
            q=q,
            symbols=symbol_list,
            category=category,
            sentiment=sentiment,
            limit=limit,
            offset=offset
        )
        
        news_service = NewsService(db)
        articles = news_service.search_news(search_params)
        
        return articles
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching news: {str(e)}")

@router.get("/trending", response_model=List[NewsArticleResponse])
async def get_trending_news(
    limit: int = Query(20, le=50, ge=1, description="Number of trending articles to return (max 50)"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Get trending news articles based on views, relevance, and recency.
    
    Returns articles from the last 7 days, ordered by:
    1. View count
    2. Relevance score
    3. Publication date
    """
    try:
        news_service = NewsService(db)
        articles = news_service.get_trending_news(limit)
        return articles
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching trending news: {str(e)}")

@router.get("/categories")
async def get_categories():
    """
    Get list of available news categories.
    """
    return {
        "categories": [
            {"name": "earnings", "description": "Quarterly earnings and financial results"},
            {"name": "mergers", "description": "Mergers, acquisitions, and corporate deals"},
            {"name": "markets", "description": "Stock market and trading news"},
            {"name": "crypto", "description": "Cryptocurrency and blockchain news"},
            {"name": "fed", "description": "Federal Reserve and monetary policy"},
            {"name": "economic", "description": "Economic indicators and analysis"},
            {"name": "tech", "description": "Technology sector news"},
            {"name": "energy", "description": "Energy sector and commodity news"},
            {"name": "healthcare", "description": "Healthcare and pharmaceutical news"},
            {"name": "real_estate", "description": "Real estate and REIT news"},
            {"name": "general", "description": "General financial news"}
        ]
    }

@router.get("/category/{category_name}", response_model=List[NewsArticleResponse])
async def get_news_by_category(
    category_name: str = Path(..., description="Category name"),
    limit: int = Query(20, le=50, ge=1, description="Number of articles to return"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Get news articles by specific category.
    """
    try:
        news_service = NewsService(db)
        articles = news_service.get_news_by_category(category_name, limit)
        
        if not articles:
            return []
        
        return articles
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching category news: {str(e)}")

@router.get("/symbols/{symbols}", response_model=List[NewsArticleResponse])
async def get_news_by_symbols(
    symbols: str = Path(..., description="Comma-separated stock symbols"),
    limit: int = Query(20, le=50, ge=1, description="Number of articles to return"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Get news articles related to specific stock symbols.
    
    - **symbols**: Comma-separated list of stock symbols (e.g., AAPL,GOOGL,MSFT)
    """
    try:
        # Parse and validate symbols
        symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
        
        if not symbol_list:
            raise HTTPException(status_code=400, detail="No valid symbols provided")
        
        if len(symbol_list) > 10:
            raise HTTPException(status_code=400, detail="Too many symbols (max 10)")
        
        news_service = NewsService(db)
        articles = news_service.get_news_by_symbols(symbol_list, limit)
        
        return articles
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching symbol news: {str(e)}")

@router.get("/{article_id}", response_model=NewsArticleResponse)
async def get_article(
    article_id: int = Path(..., description="Article ID"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Get a specific news article by ID.
    
    This endpoint also increments the view count for the article.
    """
    try:
        news_service = NewsService(db)
        article = news_service.get_article_by_id(article_id)
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        return article
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching article: {str(e)}")

@router.post("/refresh")
async def refresh_news(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # Require authentication for manual refresh
):
    """
    Manually trigger news refresh from all sources.
    
    This endpoint requires authentication and manually fetches fresh news
    from all configured sources (RSS feeds, News API, etc.).
    """
    try:
        news_service = NewsService(db)
        await news_service.fetch_and_store_news()
        
        return {
            "message": "News refresh completed successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refreshing news: {str(e)}")

@router.delete("/cleanup")
async def cleanup_old_articles(
    days: int = Query(60, ge=30, le=365, description="Articles older than this many days will be deleted"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # Require authentication
):
    """
    Clean up old articles (requires authentication).
    
    Deletes articles older than the specified number of days.
    Minimum 30 days, maximum 365 days.
    """
    try:
        news_service = NewsService(db)
        deleted_count = news_service.cleanup_old_articles(days)
        
        return {
            "message": f"Successfully deleted {deleted_count} old articles",
            "days_threshold": days,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cleaning up articles: {str(e)}")

@router.get("/stats/summary")
async def get_news_stats(
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Get news statistics and summary.
    """
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import func
        
        # Basic statistics
        total_articles = db.query(NewsArticle).filter(NewsArticle.is_active == True).count()
        
        # Articles from last 24 hours
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_articles = db.query(NewsArticle).filter(
            NewsArticle.is_active == True,
            NewsArticle.published_at > yesterday
        ).count()
        
        # Articles by category (top 10)
        category_stats = db.query(
            NewsArticle.category,
            func.count(NewsArticle.id).label('count')
        ).filter(
            NewsArticle.is_active == True,
            NewsArticle.published_at > datetime.utcnow() - timedelta(days=7)
        ).group_by(NewsArticle.category).order_by(func.count(NewsArticle.id).desc()).limit(10).all()
        
        # Sentiment distribution
        sentiment_stats = db.query(
            NewsArticle.sentiment,
            func.count(NewsArticle.id).label('count')
        ).filter(
            NewsArticle.is_active == True,
            NewsArticle.published_at > datetime.utcnow() - timedelta(days=7)
        ).group_by(NewsArticle.sentiment).all()
        
        return {
            "total_articles": total_articles,
            "articles_last_24h": recent_articles,
            "categories": [{"name": cat, "count": count} for cat, count in category_stats],
            "sentiment_distribution": [{"sentiment": sent, "count": count} for sent, count in sentiment_stats],
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching news stats: {str(e)}")
