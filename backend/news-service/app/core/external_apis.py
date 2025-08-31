# app/core/external_apis.py
import httpx
from typing import Dict, List, Optional
from datetime import datetime
from app.core.config import settings

class ExternalNewsAPIs:
    """Handler for external news APIs"""
    
    def __init__(self):
        self.session = httpx.AsyncClient(timeout=30.0)
        self.news_api_key = settings.NEWS_API_KEY
        self.finnhub_api_key = settings.FINNHUB_API_KEY
        self.alpha_vantage_key = settings.ALPHA_VANTAGE_API_KEY

    async def fetch_news_api(self, query: str = None, sources: str = None, language: str = "en") -> List[Dict]:
        """Fetch news from NewsAPI.org"""
        if not self.news_api_key:
            return []
        
        try:
            params = {
                "apiKey": self.news_api_key,
                "language": language,
                "sortBy": "publishedAt",
                "pageSize": 50
            }
            
            if query:
                params["q"] = query
                endpoint = "https://newsapi.org/v2/everything"
            else:
                params["category"] = "business"
                endpoint = "https://newsapi.org/v2/top-headlines"
            
            if sources:
                params["sources"] = sources
            
            response = await self.session.get(endpoint, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get("articles", [])
            
        except Exception as e:
            print(f"Error fetching from NewsAPI: {e}")
            return []

    async def fetch_finnhub_news(self, category: str = "general") -> List[Dict]:
        """Fetch news from Finnhub API"""
        if not self.finnhub_api_key:
            return []
        
        try:
            params = {
                "category": category,
                "token": self.finnhub_api_key
            }
            
            response = await self.session.get(
                "https://finnhub.io/api/v1/news",
                params=params
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Error fetching from Finnhub: {e}")
            return []

    async def fetch_alpha_vantage_news(self, topics: str = "technology,earnings") -> List[Dict]:
        """Fetch news from Alpha Vantage"""
        if not self.alpha_vantage_key:
            return []
        
        try:
            params = {
                "function": "NEWS_SENTIMENT",
                "topics": topics,
                "apikey": self.alpha_vantage_key,
                "limit": 50
            }
            
            response = await self.session.get(
                "https://www.alphavantage.co/query",
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get("feed", [])
            
        except Exception as e:
            print(f"Error fetching from Alpha Vantage: {e}")
            return []

    async def fetch_rss_feeds(self) -> List[Dict]:
        """Fetch from various RSS feeds"""
        feeds = [
            {
                "url": "https://feeds.finance.yahoo.com/rss/2.0/headline",
                "source": "Yahoo Finance"
            },
            {
                "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
                "source": "CNBC"
            },
            {
                "url": "https://www.marketwatch.com/rss/topstories",
                "source": "MarketWatch"
            },
            {
                "url": "https://feeds.reuters.com/reuters/businessNews",
                "source": "Reuters Business"
            },
            {
                "url": "https://rss.cnn.com/rss/money_latest.rss",
                "source": "CNN Business"
            }
        ]
        
        all_articles = []
        
        for feed_info in feeds:
            try:
                import feedparser
                
                response = await self.session.get(feed_info["url"])
                feed_data = feedparser.parse(response.content)
                
                for entry in feed_data.entries[:20]:  # Limit per feed
                    article = {
                        "title": entry.get("title", ""),
                        "summary": entry.get("summary", ""),
                        "url": entry.get("link", ""),
                        "source": feed_info["source"],
                        "author": entry.get("author", ""),
                        "published": entry.get("published", ""),
                        "content": self._extract_content(entry)
                    }
                    all_articles.append(article)
                    
            except Exception as e:
                print(f"Error fetching RSS feed {feed_info['url']}: {e}")
                continue
        
        return all_articles

    def _extract_content(self, entry) -> str:
        """Extract content from RSS entry"""
        content = ""
        
        if hasattr(entry, 'content') and entry.content:
            content = entry.content[0].get('value', '')
        elif hasattr(entry, 'summary'):
            content = entry.summary
        
        # Clean HTML tags
        if content:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            content = soup.get_text()
        
        return content

    async def close(self):
        """Close the HTTP session"""
        await self.session.aclose()

# Global instance
external_news_apis = ExternalNewsAPIs()
