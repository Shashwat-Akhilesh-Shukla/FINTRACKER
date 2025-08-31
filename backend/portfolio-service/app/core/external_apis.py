import httpx
import yfinance as yf
from typing import Dict, List, Optional
from datetime import datetime
from app.core.config import settings

class MarketDataAPI:
    """External API integration handler that:
    - Manages market data API connections
    - Provides stock quote fetching functionality
    - Handles historical data retrieval
    - Implements connection pooling and error handling"""
    
    def __init__(self):
        self.session = httpx.AsyncClient(timeout=30.0)
        self.alpha_vantage_key = settings.ALPHA_VANTAGE_API_KEY
        self.finnhub_key = settings.FINNHUB_API_KEY

    async def get_quote(self, symbol: str) -> Optional[Dict]:
        """Get real-time stock quote"""
        try:
            # Using yfinance for simplicity (replace with paid API in production)
            ticker = yf.Ticker(symbol)
            info = ticker.info
            history = ticker.history(period="2d")
            
            if history.empty:
                return None
            
            current_price = float(history['Close'].iloc[-1])
            previous_close = float(history['Close'].iloc[-2] if len(history) > 1 else current_price)
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100 if previous_close > 0 else 0
            
            return {
                "symbol": symbol,
                "name": info.get("longName", symbol),
                "price": current_price,
                "change": change,
                "changePercent": change_percent,
                "volume": info.get("volume", 0),
                "marketCap": info.get("marketCap", 0),
                "pe": info.get("forwardPE", 0),
                "dividend": info.get("dividendRate", 0),
                "dividendYield": info.get("dividendYield", 0),
                "sector": info.get("sector", ""),
                "industry": info.get("industry", ""),
                "lastUpdated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"Error fetching quote for {symbol}: {e}")
            return None

    async def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, Dict]:
        """Get quotes for multiple symbols"""
        quotes = {}
        for symbol in symbols:
            quote = await self.get_quote(symbol)
            if quote:
                quotes[symbol] = quote
        return quotes

    async def get_historical_data(self, symbol: str, period: str = "1y") -> List[Dict]:
        """Get historical price data"""
        try:
            ticker = yf.Ticker(symbol)
            history = ticker.history(period=period)
            
            data = []
            for date, row in history.iterrows():
                data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "open": float(row['Open']),
                    "high": float(row['High']),
                    "low": float(row['Low']),
                    "close": float(row['Close']),
                    "volume": int(row['Volume'])
                })
            
            return data
        except Exception as e:
            print(f"Error fetching historical data for {symbol}: {e}")
            return []

    async def close(self):
        await self.session.aclose()

# Global instance
market_data_api = MarketDataAPI()
