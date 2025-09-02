# app/services/market_data_service.py

import os
import time
import requests
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv
import asyncio

load_dotenv()

FINNHUB_BASE = "https://finnhub.io/api/v1"


# ----- Exceptions -----
class FinnhubError(Exception):
    pass


class RateLimitExceeded(FinnhubError):
    pass


# ----- Service -----
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
            self.session = requests.Session()
            self.session.headers.update({"User-Agent": "FinnhubClient/1.0"})
            self.initialized = True
            self._last_request = datetime.min
            self._request_interval = 1.0  # seconds between requests
            self._request_lock = asyncio.Lock()

    def _request(self, endpoint: str, params: Dict) -> Dict:
        """Low-level request with retries and rate limit handling."""
        params = dict(params)
        params["token"] = self.api_key

        last_exc = None
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = self.session.get(f"{FINNHUB_BASE}/{endpoint}", params=params, timeout=self.timeout)
            except Exception as e:
                last_exc = e
                if attempt < self.max_retries:
                    time.sleep(self.backoff_factor * attempt)
                    continue
                raise FinnhubError(f"Network error calling Finnhub: {e}") from e

            if resp.status_code == 429:
                # Rate limit
                if attempt >= self.max_retries:
                    raise RateLimitExceeded("Finnhub rate limit exceeded")
                sleep_for = self.backoff_factor * (2 ** (attempt - 1))
                time.sleep(sleep_for)
                continue

            if resp.status_code >= 400:
                raise FinnhubError(f"Finnhub error {resp.status_code}: {resp.text}")

            try:
                return resp.json()
            except ValueError as e:
                last_exc = e
                if attempt < self.max_retries:
                    time.sleep(self.backoff_factor * attempt)
                    continue
                raise FinnhubError("Finnhub returned non-JSON response") from e

        raise FinnhubError("Finnhub request failed after retries") from last_exc

    async def _rate_limited_request(self, endpoint: str, params: Dict) -> Dict:
        """Rate-limited request wrapper"""
        async with self._request_lock:
            now = datetime.now()
            time_since_last = (now - self._last_request).total_seconds()
            if time_since_last < self._request_interval:
                await asyncio.sleep(self._request_interval - time_since_last)
            
            result = self._request(endpoint, params)
            self._last_request = datetime.now()
            return result

    # ---------- Public API ----------

    async def search_symbols(self, query: str) -> List[Dict]:
        data = await self._rate_limited_request("search", {"q": query})
        results = data.get("result") or []
        out = []
        for r in results:
            out.append({
                "symbol": r.get("symbol"),
                "name": r.get("description"),
                "type": r.get("type"),
                "region": r.get("mic"),
                "currency": r.get("currency"),
            })
        return out

    async def get_latest_price(self, symbol: str) -> Optional[float]:
        data = await self._rate_limited_request("quote", {"symbol": symbol})
        price = data.get("c")
        try:
            return float(price) if price is not None else None
        except ValueError:
            return None

    async def get_historical_data(self, symbol: str, interval: str = "D", lookback_days: int = 365) -> Dict[str, Dict]:
        """
        Fetch historical OHLCV data from Finnhub.
        interval: '1', '5', '15', '30', '60' (minutes), 'D', 'W', 'M'
        lookback_days: number of days back to fetch
        """
        valid_resolutions = {"1", "5", "15", "30", "60", "D", "W", "M"}
        if interval not in valid_resolutions:
            raise ValueError(f"interval must be one of {valid_resolutions}")

        now = int(time.time())
        frm = now - lookback_days * 86400

        data = await self._rate_limited_request("stock/candle", {"symbol": symbol, "resolution": interval, "from": frm, "to": now})

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
                "adjusted_close": data["c"][i],  # Finnhub gives adjusted values directly
            }

        return results


# ----- Self-test script -----
async def self_test():
    """Self test for market data service"""
    api_key = os.getenv("FINNHUB_API_KEY")
    if not api_key:
        print("ERROR: FINNHUB_API_KEY not set")
        return

    svc = FinnhubMarketDataService(api_key=api_key)

    try:
        print("1. Testing search_symbols('AAPL')...")
        results = await svc.search_symbols("AAPL")
        print("   Found:", results[:5])
    except Exception as e:
        print("   ERROR:", e)

    try:
        print("\n2. Testing get_historical_data('AAPL')...")
        hist = await svc.get_historical_data("AAPL")
        dates = list(sorted(hist.keys()))[:3]
        print("   Latest dates:", dates)
    except Exception as e:
        print("   ERROR:", e)

    try:
        print("\n3. Testing get_latest_price('AAPL')...")
        price = await svc.get_latest_price("AAPL")
        print("   Price:", price)
    except Exception as e:
        print("   ERROR:", e)

if __name__ == "__main__":
    asyncio.run(self_test())
