# app/services/news_service.py
import httpx
import feedparser
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from dateutil import parser as date_parser

from app.models.news import NewsArticle
from app.schemas.news import NewsArticleCreate, NewsSearchParams
from app.services.sentiment_service import SentimentService
from app.core.config import settings
from app.utils.text_processing import text_processor
from app.core.external_apis import external_news_apis


class NewsService:
    def __init__(self, db: Session):
        self.db = db
        self.sentiment_service = SentimentService()

    async def fetch_and_store_news(self):
        """Fetch news from multiple sources and store"""
        try:
            # Use external APIs service for fetching
            await self.fetch_from_external_apis()
            
            # Also process RSS feeds directly
            await self._process_direct_rss_feeds()
            
            print("News fetching completed successfully")
        except Exception as e:
            print(f"Error in fetch_and_store_news: {e}")

    async def fetch_from_external_apis(self):
        """Fetch news from all external APIs"""
        try:
            # Fetch from multiple sources
            news_api_articles = await external_news_apis.fetch_news_api("finance OR stocks OR market")
            finnhub_articles = await external_news_apis.fetch_finnhub_news("general")
            alpha_vantage_articles = await external_news_apis.fetch_alpha_vantage_news("technology,earnings")
            rss_articles = await external_news_apis.fetch_rss_feeds()
            
            # Process each source
            all_sources = [
                ("newsapi", news_api_articles),
                ("finnhub", finnhub_articles),
                ("alphavantage", alpha_vantage_articles),
                ("rss", rss_articles)
            ]
            
            for source_name, articles in all_sources:
                if articles:
                    print(f"Processing {len(articles)} articles from {source_name}")
                    for article in articles:
                        await self._process_external_article(article, source_name)
                        
        except Exception as e:
            print(f"Error fetching from external APIs: {e}")

    async def _process_external_article(self, article: dict, source_type: str):
        """Process article from external API"""
        try:
            # Create unique ID based on URL or title
            url = article.get('url', '')
            title = article.get('title', '')
            
            if not url and not title:
                return  # Skip articles without URL or title
            
            external_id = f"{source_type}_{hash(url or title)}"
            
            # Check if already exists
            existing = self.db.query(NewsArticle).filter(
                NewsArticle.external_id == external_id
            ).first()
            
            if existing:
                return
            
            # Clean and process content using text processor
            title = text_processor.clean_text(title)
            summary = text_processor.clean_text(article.get('summary', article.get('description', '')))
            content = text_processor.clean_text(article.get('content', ''))
            
            if not title or len(title) < 10:
                return  # Skip articles with very short or no titles
            
            # Analyze sentiment
            text_for_analysis = f"{title} {summary}"
            sentiment, sentiment_score = await self.sentiment_service.analyze_sentiment(text_for_analysis)
            
            # Extract metadata using text processor
            symbols = text_processor.extract_stock_symbols(text_for_analysis)
            category = text_processor.categorize_content(title, summary)
            keywords = text_processor.extract_keywords(text_for_analysis)
            relevance_score = text_processor.calculate_financial_relevance(title, summary)
            
            # Parse published date
            published_at = datetime.utcnow()
            published_date = article.get('publishedAt', article.get('published', article.get('time_published')))
            
            if published_date:
                try:
                    if 'T' in str(published_date):
                        published_at = datetime.fromisoformat(
                            str(published_date).replace('Z', '+00:00').replace('+0000', '+00:00')
                        )
                    else:
                        published_at = date_parser.parse(str(published_date))
                except Exception as e:
                    print(f"Error parsing date {published_date}: {e}")
                    # Use current time if parsing fails
                    published_at = datetime.utcnow()
            
            # Determine source name
            source_name = source_type.title()
            if isinstance(article.get('source'), dict):
                source_name = article['source'].get('name', source_type.title())
            elif isinstance(article.get('source'), str):
                source_name = article['source']
            
            # Create article data
            article_data = NewsArticleCreate(
                external_id=external_id,
                title=title[:500],  # Limit title length
                summary=summary[:1000] if summary else None,  # Limit summary length
                content=content[:5000] if content else None,  # Limit content length
                url=url[:500] if url else '',
                image_url=article.get('urlToImage', article.get('image', article.get('banner_image')))[:500] if article.get('urlToImage', article.get('image', article.get('banner_image'))) else None,
                source=source_name[:100],  # Limit source length
                author=str(article.get('author', ''))[:100] if article.get('author') else None,
                published_at=published_at,
                category=category,
                symbols=symbols,
                tags=keywords[:10]  # Limit tags
            )
            
            # Only create if relevance score is decent
            if relevance_score > 0.2:
                await self.create_article(article_data, sentiment, sentiment_score)
                
        except Exception as e:
            print(f"Error processing external article: {e}")

    async def _process_direct_rss_feeds(self):
        """Process RSS feeds directly (fallback method)"""
        feeds = [
            {"url": "https://feeds.finance.yahoo.com/rss/2.0/headline", "source": "Yahoo Finance"},
            {"url": "https://www.cnbc.com/id/100003114/device/rss/rss.html", "source": "CNBC"},
            {"url": "https://www.marketwatch.com/rss/topstories", "source": "MarketWatch"},
        ]
        
        async with httpx.AsyncClient(timeout=30.0) as session:
            for feed_info in feeds:
                try:
                    await self._process_rss_feed(feed_info["url"], feed_info["source"], session)
                except Exception as e:
                    print(f"Error processing feed {feed_info['url']}: {e}")

    async def _process_rss_feed(self, feed_url: str, source_name: str, session: httpx.AsyncClient):
        """Process individual RSS feed"""
        try:
            response = await session.get(feed_url)
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            
            for entry in feed.entries[:15]:  # Limit to 15 articles per feed
                # Create external ID from URL
                external_id = f"rss_{hash(entry.get('link', entry.get('title', '')))}"
                
                # Check if article already exists
                existing = self.db.query(NewsArticle).filter(
                    NewsArticle.external_id == external_id
                ).first()
                
                if existing:
                    continue
                
                # Parse published date
                published_at = datetime.utcnow()
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    try:
                        published_at = datetime(*entry.published_parsed[:6])
                    except:
                        pass
                elif hasattr(entry, 'published'):
                    try:
                        published_at = date_parser.parse(entry.published)
                    except:
                        pass
                
                # Extract content
                title = text_processor.clean_text(getattr(entry, 'title', ''))
                summary = text_processor.clean_text(getattr(entry, 'summary', ''))
                content = summary  # RSS usually doesn't have full content
                
                if hasattr(entry, 'content') and entry.content:
                    content = text_processor.clean_text(entry.content[0].get('value', ''))
                
                if not title or len(title) < 10:
                    continue
                
                # Analyze sentiment
                text_for_analysis = f"{title} {summary}"
                sentiment, sentiment_score = await self.sentiment_service.analyze_sentiment(text_for_analysis)
                
                # Extract metadata using text processor
                symbols = text_processor.extract_stock_symbols(text_for_analysis)
                category = text_processor.categorize_content(title, summary)
                keywords = text_processor.extract_keywords(text_for_analysis)
                relevance_score = text_processor.calculate_financial_relevance(title, summary)
                
                # Create article
                article_data = NewsArticleCreate(
                    external_id=external_id,
                    title=title[:500],
                    summary=summary[:1000] if summary else None,
                    content=content[:5000] if content else None,
                    url=entry.get('link', '')[:500],
                    source=source_name,
                    author=getattr(entry, 'author', None),
                    published_at=published_at,
                    category=category,
                    symbols=symbols,
                    tags=keywords[:10]
                )
                
                if relevance_score > 0.2:
                    await self.create_article(article_data, sentiment, sentiment_score)
                
        except Exception as e:
            print(f"Error processing RSS feed {feed_url}: {e}")

    async def create_article(
        self, 
        article_data: NewsArticleCreate, 
        sentiment: str = None, 
        sentiment_score: float = None
    ) -> NewsArticle:
        """Create new news article"""
        try:
            # Calculate relevance score using text processor
            relevance_score = text_processor.calculate_financial_relevance(
                article_data.title, 
                article_data.summary or ""
            )
            
            db_article = NewsArticle(
                external_id=article_data.external_id,
                title=article_data.title,
                summary=article_data.summary,
                content=article_data.content,
                url=article_data.url,
                image_url=article_data.image_url,
                source=article_data.source,
                author=article_data.author,
                published_at=article_data.published_at,
                sentiment=sentiment,
                sentiment_score=sentiment_score,
                relevance_score=relevance_score,
                category=article_data.category,
                symbols=article_data.symbols,
                tags=article_data.tags,
                is_featured=(relevance_score > 0.7)  # Auto-feature high relevance articles
            )
            
            self.db.add(db_article)
            self.db.commit()
            self.db.refresh(db_article)
            return db_article
            
        except Exception as e:
            print(f"Error creating article: {e}")
            self.db.rollback()
            raise

    def search_news(self, search_params: NewsSearchParams) -> List[NewsArticle]:
        """Search news articles with filters"""
        query = self.db.query(NewsArticle).filter(NewsArticle.is_active == True)
        
        # Text search
        if search_params.q:
            search_term = f"%{search_params.q}%"
            query = query.filter(
                or_(
                    NewsArticle.title.ilike(search_term),
                    NewsArticle.summary.ilike(search_term),
                    NewsArticle.content.ilike(search_term)
                )
            )
        
        # Symbol filter - check if any of the provided symbols are in the article's symbols array
        if search_params.symbols:
            for symbol in search_params.symbols:
                query = query.filter(
                    NewsArticle.symbols.op('&&')(f'{{{symbol}}}')
                )
        
        # Category filter
        if search_params.category:
            query = query.filter(NewsArticle.category == search_params.category)
        
        # Sentiment filter
        if search_params.sentiment:
            query = query.filter(NewsArticle.sentiment == search_params.sentiment)
        
        # Filter out very old articles (older than 30 days)
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        query = query.filter(NewsArticle.published_at > cutoff_date)
        
        # Order by relevance and recency
        query = query.order_by(
            desc(NewsArticle.is_featured),
            desc(NewsArticle.relevance_score),
            desc(NewsArticle.published_at)
        )
        
        return query.offset(search_params.offset).limit(search_params.limit).all()

    def get_trending_news(self, limit: int = 20) -> List[NewsArticle]:
        """Get trending news based on views, relevance, and recency"""
        return self.db.query(NewsArticle).filter(
            NewsArticle.is_active == True,
            NewsArticle.published_at > datetime.utcnow() - timedelta(days=7),
            NewsArticle.relevance_score > 0.3
        ).order_by(
            desc(NewsArticle.views),
            desc(NewsArticle.relevance_score),
            desc(NewsArticle.published_at)
        ).limit(limit).all()

    def get_news_by_category(self, category: str, limit: int = 20) -> List[NewsArticle]:
        """Get news articles by category"""
        return self.db.query(NewsArticle).filter(
            NewsArticle.is_active == True,
            NewsArticle.category == category,
            NewsArticle.published_at > datetime.utcnow() - timedelta(days=14)
        ).order_by(
            desc(NewsArticle.relevance_score),
            desc(NewsArticle.published_at)
        ).limit(limit).all()

    def get_news_by_symbols(self, symbols: List[str], limit: int = 20) -> List[NewsArticle]:
        """Get news articles related to specific stock symbols"""
        query = self.db.query(NewsArticle).filter(
            NewsArticle.is_active == True,
            NewsArticle.published_at > datetime.utcnow() - timedelta(days=14)
        )
        
        # Filter by symbols
        for symbol in symbols:
            query = query.filter(
                NewsArticle.symbols.op('&&')(f'{{{symbol}}}')
            )
        
        return query.order_by(
            desc(NewsArticle.relevance_score),
            desc(NewsArticle.published_at)
        ).limit(limit).all()

    def increment_article_views(self, article_id: int):
        """Increment view count for an article"""
        try:
            article = self.db.query(NewsArticle).filter(NewsArticle.id == article_id).first()
            if article:
                article.views += 1
                self.db.commit()
        except Exception as e:
            print(f"Error incrementing article views: {e}")
            self.db.rollback()

    def get_article_by_id(self, article_id: int) -> Optional[NewsArticle]:
        """Get article by ID and increment views"""
        article = self.db.query(NewsArticle).filter(
            NewsArticle.id == article_id,
            NewsArticle.is_active == True
        ).first()
        
        if article:
            self.increment_article_views(article_id)
        
        return article

    def cleanup_old_articles(self, days_old: int = 60):
        """Clean up articles older than specified days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            deleted_count = self.db.query(NewsArticle).filter(
                NewsArticle.published_at < cutoff_date
            ).delete()
            
            self.db.commit()
            print(f"Cleaned up {deleted_count} old articles")
            return deleted_count
            
        except Exception as e:
            print(f"Error cleaning up old articles: {e}")
            self.db.rollback()
            return 0

    # Keep the old methods for backward compatibility but update them to use text_processor
    def _extract_symbols(self, text: str) -> List[str]:
        """Extract stock symbols from text using text processor"""
        return text_processor.extract_stock_symbols(text)

    def _categorize_news(self, title: str, summary: str) -> str:
        """Categorize news using text processor"""
        return text_processor.categorize_content(title, summary or "")

    def _extract_tags(self, text: str) -> List[str]:
        """Extract relevant tags from text using text processor"""
        return text_processor.extract_keywords(text)

    def _calculate_relevance_score(self, title: str, summary: str, symbols: List[str]) -> float:
        """Calculate relevance score using text processor"""
        return text_processor.calculate_financial_relevance(title, summary or "")
