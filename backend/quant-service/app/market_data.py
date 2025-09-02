import os
import asyncio
import httpx
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
load_dotenv()

FINNHUB_BASE = "https://finnhub.io/api/v1"

class FinnhubError(Exception):
    pass

class RateLimitExceeded(FinnhubError):
    pass

class FinnhubMarketDataService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        api_key: Optional[str] = None,
        max_retries: int = 3,
        backoff_factor: float = 1.0,
        timeout: float = 10.0,
    ):
        if not hasattr(self, "initialized"):
            self.api_key = api_key or os.getenv("FINNHUB_API_KEY")
            if not self.api_key:
                raise ValueError("Missing Finnhub API key. Set FINNHUB_API_KEY in .env or pass api_key.")
            
            self.max_retries = max_retries
            self.backoff_factor = backoff_factor
            self.timeout = timeout
            self.initialized = True
            self._last_request = datetime.min
            self._request_interval = 1.0
            self._request_lock = asyncio.Lock()
            self._service_available = True

    async def _request(self, endpoint: str, params: Dict) -> Dict:
        """Async request with retries and rate limit handling."""
        if not self._service_available:
            raise FinnhubError("Market data service is unavailable")
            
        params = dict(params)
        params["token"] = self.api_key
        
        last_exc = None
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(1, self.max_retries + 1):
                try:
                    resp = await client.get(f"{FINNHUB_BASE}/{endpoint}", params=params)
                    
                    if resp.status_code == 429:
                        if attempt >= self.max_retries:
                            raise RateLimitExceeded("Finnhub rate limit exceeded")
                        sleep_for = self.backoff_factor * (2 ** (attempt - 1))
                        await asyncio.sleep(sleep_for)
                        continue
                    
                    if resp.status_code >= 400:
                        raise FinnhubError(f"Finnhub error {resp.status_code}: {resp.text}")
                    
                    return resp.json()
                    
                except httpx.RequestError as e:
                    last_exc = e
                    if attempt < self.max_retries:
                        await asyncio.sleep(self.backoff_factor * attempt)
                        continue
                    raise FinnhubError(f"Network error calling Finnhub: {e}") from e
                except Exception as e:
                    last_exc = e
                    if attempt < self.max_retries:
                        await asyncio.sleep(self.backoff_factor * attempt)
                        continue
                    break
        
        # If we get here, all attempts failed
        self._service_available = False
        raise FinnhubError("Finnhub request failed after retries") from last_exc

    async def _rate_limited_request(self, endpoint: str, params: Dict) -> Dict:
        """Rate-limited request wrapper"""
        async with self._request_lock:
            now = datetime.now()
            time_since_last = (now - self._last_request).total_seconds()
            if time_since_last < self._request_interval:
                await asyncio.sleep(self._request_interval - time_since_last)
            
            result = await self._request(endpoint, params)
            self._last_request = datetime.now()
            return result

    async def search_symbols(self, query: str) -> List[Dict]:
        try:
            data = await self._rate_limited_request("search", {"q": query})
            results = data.get("result") or []
            return [
                {
                    "symbol": r.get("symbol"),
                    "name": r.get("description"),
                    "type": r.get("type"),
                    "region": r.get("mic"),
                    "currency": r.get("currency"),
                }
                for r in results
            ]
        except Exception as e:
            logger.error(f"Error searching symbols: {e}")
            return []

    async def get_latest_price(self, symbol: str) -> Optional[float]:
        try:
            data = await self._rate_limited_request("quote", {"symbol": symbol})
            price = data.get("c")
            return float(price) if price is not None else None
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            return None

    async def get_historical_data(self, symbol: str, interval: str = "D", lookback_days: int = 365) -> Dict[str, Dict]:
        """Fetch historical OHLCV data from Finnhub."""
        valid_resolutions = {"1", "5", "15", "30", "60", "D", "W", "M"}
        if interval not in valid_resolutions:
            raise ValueError(f"interval must be one of {valid_resolutions}")

        now = int(datetime.now().timestamp())
        frm = now - lookback_days * 86400

        try:
            data = await self._rate_limited_request(
                "stock/candle", 
                {"symbol": symbol, "resolution": interval, "from": frm, "to": now}
            )
            
            if data.get("s") != "ok":
                raise FinnhubError(f"Unexpected response for candles: {data}")

            results: Dict[str, Dict] = {}
            for i, ts in enumerate(data["t"]):
                date_str = datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d")
                results[date_str] = {
                    "open": data["o"][i],
                    "high": data["h"][i],
                    "low": data["l"][i],
                    "close": data["c"][i],
                    "volume": data["v"][i],
                    "adjusted_close": data["c"][i],
                }
            return results
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {e}")
            return {}

    async def get_market_benchmark_data(self, symbol: str, period_days: int = 365) -> List[Dict]:
        """Get benchmark data for market indices"""
        try:
            data = await self.get_historical_data(symbol, lookback_days=period_days)
            return [
                {"date": date_str, "close": values["close"]}
                for date_str, values in sorted(data.items())
            ]
        except Exception as e:
            logger.error(f"Error getting benchmark data for {symbol}: {e}")
            return []

    def disable_service(self):
        """Disable the service to force DB fallback"""
        self._service_available = False
        logger.warning("Finnhub service disabled, falling back to database")

    def enable_service(self):
        """Re-enable the service"""
        self._service_available = True
        logger.info("Finnhub service re-enabled")

    @property
    def is_available(self) -> bool:
        return self._service_available
