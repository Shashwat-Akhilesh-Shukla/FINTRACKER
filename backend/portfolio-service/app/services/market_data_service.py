# import asyncio
# from typing import Dict, List, Optional
# from datetime import datetime
# from tvDatafeed import TvDatafeed, Interval
# from dotenv import load_dotenv
# import os

# load_dotenv()


# class MarketDataService:
#     def __init__(self):
#         self.tv = TvDatafeed()
#     async def search_symbols(self, query: str, exchange: Optional[str] = None) -> List[Dict]:
#         """Redirect AlphaVantage-style symbol search to TradingView search"""
#         try:
#             results = self.tv.search_symbol(query, exchange)  # returns list of dicts
#             normalized = []
#             for r in results:
#                 normalized.append({
#                     "symbol": r.get("symbol"),
#                     "name": r.get("description", r.get("symbol")),
#                     "type": r.get("type", "Equity"),
#                     "region": exchange or "",
#                     "marketOpen": "09:15",
#                     "marketClose": "15:30",
#                     "timezone": "Asia/Kolkata",
#                     "currency": r.get("currency_code", "INR")
#                 })
#             return normalized
#         except Exception as e:
#             print(f"Error searching symbols with TradingView: {e}")
#             return []

#     async def get_quote_yfinance(self, symbol: str, exchange: str = "NSE") -> Optional[Dict]:
#         """Redirect Yahoo quote fetch to TradingView's latest candle"""
#         try:
#             await asyncio.sleep(0.2)
#             df = self.tv.get_hist(
#                 symbol=symbol,
#                 exchange=exchange,
#                 interval=Interval.in_1_minute,
#                 n_bars=2
#             )
#             if df is None or df.empty:
#                 return None

#             current = df.iloc[-1]
#             prev = df.iloc[-2] if len(df) > 1 else current
#             price = float(current["close"])
#             change = price - float(prev["close"])
#             change_percent = (change / float(prev["close"])) * 100 if prev["close"] else 0

#             return {
#                 "symbol": symbol,
#                 "name": symbol,
#                 "price": price,
#                 "change": change,
#                 "changePercent": change_percent,
#                 "volume": int(current["volume"]),
#                 "marketCap": 0,
#                 "pe": 0,
#                 "dividend": 0,
#                 "dividendYield": 0,
#                 "high52Week": float(df["high"].max()),
#                 "low52Week": float(df["low"].min()),
#                 "sector": "",
#                 "industry": "",
#                 "provider": "tradingview",
#                 "lastUpdated": datetime.utcnow().isoformat(),
#             }
#         except Exception as e:
#             print(f"Error fetching quote for {symbol} from TradingView: {e}")
#             return None

#     async def get_quote_alpha_vantage(self, symbol: str, exchange: str = "NSE") -> Optional[Dict]:
#         """AlphaVantage fallback is also routed to TradingView"""
#         return await self.get_quote_yfinance(symbol, exchange=exchange)

#     async def get_quote(self, symbol: str, exchange: str = "NSE") -> Optional[Dict]:
#         """Preserve fallback chain, but both point to TradingView now"""
#         result = await self.get_quote_yfinance(symbol, exchange=exchange)
#         if result:
#             return result
#         print(f"Falling back (still TradingView) for {symbol}")
#         return await self.get_quote_alpha_vantage(symbol, exchange=exchange)

#     async def get_multiple_quotes(self, symbols: List[str], exchange: str = "NSE") -> Dict[str, Dict]:
#         tasks = [self.get_quote(symbol, exchange) for symbol in symbols]
#         results = await asyncio.gather(*tasks, return_exceptions=True)
#         quotes = {}
#         for symbol, result in zip(symbols, results):
#             if not isinstance(result, Exception) and result:
#                 quotes[symbol] = result
#         return quotes

#     async def get_historical_data(self, symbol: str, period: str = "1y", exchange: str = "NSE") -> List[Dict]:
#         """Redirect historical fetch to TradingView's get_hist"""
#         try:
#             interval = Interval.in_daily
#             n_bars = 250 if period == "1y" else 1000
#             df = self.tv.get_hist(
#                 symbol=symbol,
#                 exchange=exchange,
#                 interval=interval,
#                 n_bars=n_bars
#             )
#             if df is None or df.empty:
#                 return []

#             data = []
#             for idx, row in df.iterrows():
#                 data.append({
#                     "date": idx.strftime("%Y-%m-%d"),
#                     "open": float(row["open"]),
#                     "high": float(row["high"]),
#                     "low": float(row["low"]),
#                     "close": float(row["close"]),
#                     "volume": int(row["volume"])
#                 })
#             return data
#         except Exception as e:
#             print(f"Error fetching historical data for {symbol} via TradingView: {e}")
#             return []

#     async def close(self):
#         pass


# # Global instance
# market_data_service = MarketDataService()



from typing import Dict, List, Optional
from datetime import datetime

class MarketDataService:
    """Mock market data service for development"""
    
    async def get_quote(self, symbol: str) -> Optional[Dict]:
        """Return mock quote data"""
        return {
            "symbol": symbol,
            "name": f"Mock {symbol}",
            "price": 100.00,
            "change": 0.00,
            "changePercent": 0.00,
            "volume": 0,
            "marketCap": 1000000,
            "pe": 15.0,
            "dividend": 2.0,
            "dividendYield": 2.0,
            "sector": "Technology",
            "industry": "Software",
            "lastUpdated": datetime.utcnow().isoformat()
        }

    async def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, Dict]:
        """Return mock quotes for multiple symbols"""
        return {
            symbol: await self.get_quote(symbol)
            for symbol in symbols
        }

    async def search_symbols(self, query: str) -> List[Dict]:
        """Return mock search results"""
        return [{
            "symbol": query.upper(),
            "name": f"Mock Company {query.upper()}",
            "type": "Equity",
            "region": "US",
            "currency": "USD"
        }]

    async def get_historical_data(self, symbol: str, period: str = "1y") -> List[Dict]:
        """Return mock historical data"""
        return [{
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "open": 100.00,
            "high": 101.00,
            "low": 99.00,
            "close": 100.50,
            "volume": 1000000
        }]

    async def close(self):
        pass

# Global instance
market_data_service = MarketDataService()