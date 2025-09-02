from __future__ import annotations

import asyncio
import os
import random
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Optional, Tuple, Union

import pandas as pd  # tvDatafeed returns pandas DataFrames
from tvDatafeed import TvDatafeed, Interval


# -----------------------------
# Configuration
# -----------------------------

DEFAULT_EXCHANGE = "NSE"
MAX_CONCURRENCY = 8                     # protect remote endpoints
RETRY_ATTEMPTS = 5                      # total attempts per call
RETRY_BASE_DELAY = 0.25                 # seconds, exponential backoff with jitter
HIST_52W_BARS = 270                     # trading days in ~52 weeks
INTRADAY_BARS_FOR_LAST_PRICE = 3        # pull last 3 one-minute bars
REQUEST_TIMEOUT = 12.0                  # seconds ceiling per remote op
SEARCH_TIMEOUT = 12.0

# If you set these, tvDatafeed will login and unlock more data and stability.


# -----------------------------
# Domain models
# -----------------------------

@dataclass
class Quote:
    symbol: str
    name: str
    price: float
    change: float
    changePercent: float
    volume: int
    marketCap: int
    pe: float
    dividend: float
    dividendYield: float
    high52Week: float
    low52Week: float
    sector: str
    industry: str
    provider: str
    lastUpdated: str


class MarketDataError(Exception):
    """Normalized error for market data operations."""


# -----------------------------
# Retry helpers
# -----------------------------

def _jitter_delay(base: float, attempt: int) -> float:
    # exponential backoff with full jitter
    return min(REQUEST_TIMEOUT, (base * (2 ** (attempt - 1))) * random.uniform(0.8, 1.3))


async def _retry(coro_factory, *, attempts: int, base_delay: float, timeout: float, op_name: str):
    last_exc: Optional[Exception] = None
    for i in range(1, attempts + 1):
        try:
            return await asyncio.wait_for(coro_factory(), timeout=timeout)
        except asyncio.TimeoutError as e:
            last_exc = e
        except Exception as e:
            last_exc = e

        if i < attempts:
            await asyncio.sleep(_jitter_delay(base_delay, i))
    # Exhausted
    raise MarketDataError(f"{op_name} failed after {attempts} attempts") from last_exc


# -----------------------------
# Service
# -----------------------------

class MarketDataService:
    def __init__(self):
        # tvDatafeed has its own internal session handling. Auth if possible.
        if TV_USERNAME and TV_PASSWORD:
            self.tv = TvDatafeed(TV_USERNAME, TV_PASSWORD)
        else:
            # Falls back to nologin; still works but with limits.
            self.tv = TvDatafeed()

        self._sem = asyncio.Semaphore(MAX_CONCURRENCY)

    # -------------- internal safe wrappers --------------

    async def _tv_search(self, query: str, exchange: Optional[str]) -> List[dict]:
        async def _call():
            def _sync_call():
                return self.tv.search_symbol(query, exchange)
            return await asyncio.to_thread(_sync_call)

        return await _retry(
            _call,
            attempts=RETRY_ATTEMPTS,
            base_delay=RETRY_BASE_DELAY,
            timeout=SEARCH_TIMEOUT,
            op_name="search_symbol",
        )

    async def _tv_hist(
        self,
        symbol: str,
        exchange: str,
        interval: Interval,
        n_bars: int,
    ) -> pd.DataFrame:
        async def _call():
            def _sync_call():
                return self.tv.get_hist(symbol=symbol, exchange=exchange, interval=interval, n_bars=n_bars)
            return await asyncio.to_thread(_sync_call)

        return await _retry(
            _call,
            attempts=RETRY_ATTEMPTS,
            base_delay=RETRY_BASE_DELAY,
            timeout=REQUEST_TIMEOUT,
            op_name=f"get_hist {symbol}:{exchange}:{interval.name}",
        )

    # -------------- public API --------------

    async def search_symbols(self, query: str, exchange: Optional[str] = None) -> List[Dict]:
        if not query or not query.strip():
            return []

        async with self._sem:
            try:
                results = await self._tv_search(query.strip(), exchange)
            except MarketDataError as e:
                # Quiet failure for UX; return empty list
                return []

        out: List[Dict] = []
        for r in results or []:
            # tvDatafeed search record fields vary; guard everything
            symbol = r.get("symbol") or r.get("ticker") or ""
            if not symbol:
                continue
            out.append({
                "symbol": symbol,
                "name": r.get("description") or symbol,
                "type": r.get("type") or "Equity",
                "region": exchange or "",
                "marketOpen": "09:15",
                "marketClose": "15:30",
                "timezone": "Asia/Kolkata",
                "currency": r.get("currency_code") or "INR",
            })
        return out

    async def get_quote(self, symbol: str, exchange: str = DEFAULT_EXCHANGE) -> Optional[Dict]:
        sym = (symbol or "").strip().upper()
        if not sym:
            return None

        async with self._sem:
            try:
                # 1) Last price from 1-min bars
                intraday = await self._tv_hist(
                    symbol=sym,
                    exchange=exchange,
                    interval=Interval.in_1_minute,
                    n_bars=INTRADAY_BARS_FOR_LAST_PRICE,
                )
            except MarketDataError:
                intraday = pd.DataFrame()

            # 2) 52w stats from daily bars
            try:
                daily = await self._tv_hist(
                    symbol=sym,
                    exchange=exchange,
                    interval=Interval.in_daily,
                    n_bars=HIST_52W_BARS,
                )
            except MarketDataError:
                daily = pd.DataFrame()

        if intraday is None or intraday.empty:
            # As a fallback, try daily to at least produce a price
            src = daily if daily is not None and not daily.empty else None
            if src is None:
                return None
            current = src.iloc[-1]
            prev = src.iloc[-2] if len(src) > 1 else current
        else:
            current = intraday.iloc[-1]
            prev = intraday.iloc[-2] if len(intraday) > 1 else current

        try:
            price = float(current["close"])
            prev_close = float(prev["close"]) if "close" in prev else price
            change = price - prev_close
            change_pct = (change / prev_close * 100.0) if prev_close else 0.0
            vol = int(current["volume"]) if "volume" in current else 0
        except Exception:
            return None

        if daily is not None and not daily.empty:
            try:
                high_52w = float(daily["high"].max())
                low_52w = float(daily["low"].min())
            except Exception:
                high_52w, low_52w = price, price
        else:
            high_52w, low_52w = price, price

        quote = Quote(
            symbol=sym,
            name=sym,
            price=price,
            change=change,
            changePercent=change_pct,
            volume=vol,
            marketCap=0,
            pe=0.0,
            dividend=0.0,
            dividendYield=0.0,
            high52Week=high_52w,
            low52Week=low_52w,
            sector="",
            industry="",
            provider="tradingview",
            lastUpdated=datetime.now(timezone.utc).isoformat(),
        )
        return asdict(quote)

    async def get_multiple_quotes(self, symbols: Iterable[str], exchange: str = DEFAULT_EXCHANGE) -> Dict[str, Dict]:
        # Constrain fan-out with semaphore per call via get_quote’s own semaphore
        tasks = [self.get_quote(s, exchange=exchange) for s in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        out: Dict[str, Dict] = {}
        for s, res in zip(symbols, results):
            sym = (s or "").strip().upper()
            if isinstance(res, Exception) or res is None:
                continue
            out[sym] = res
        return out

    async def get_historical_data(
        self,
        symbol: str,
        period: str = "1y",
        exchange: str = DEFAULT_EXCHANGE,
        interval: Interval = Interval.in_daily,
        n_bars: Optional[int] = None,
    ) -> List[Dict]:
        sym = (symbol or "").strip().upper()
        if not sym:
            return []

        # Period handling
        if n_bars is None:
            if period == "1y":
                n_bars = HIST_52W_BARS
            elif period in {"6mo", "6m"}:
                n_bars = 140
            elif period in {"3mo", "3m"}:
                n_bars = 75
            elif period in {"1mo", "1m"}:
                n_bars = 25
            elif period in {"5y"}:
                n_bars = 1300
            else:
                n_bars = HIST_52W_BARS

        async with self._sem:
            try:
                df = await self._tv_hist(
                    symbol=sym, exchange=exchange, interval=interval, n_bars=n_bars
                )
            except MarketDataError:
                return []

        if df is None or df.empty:
            return []

        # tvDatafeed uses DatetimeIndex; ensure tz-naive dates formatted as YYYY-MM-DD
        records: List[Dict] = []
        for idx, row in df.iterrows():
            try:
                if isinstance(idx, pd.Timestamp):
                    date_str = idx.tz_localize(None).strftime("%Y-%m-%d") if idx.tzinfo else idx.strftime("%Y-%m-%d")
                else:
                    date_str = str(idx)
                records.append({
                    "date": date_str,
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                    "volume": int(row["volume"]),
                })
            except Exception:
                continue
        return records

    async def close(self):
        # tvDatafeed does not require explicit close, but keep method for symmetry
        return
-----------------------------
Self-test
-----------------------------

async def _self_test():
    svc = MarketDataService()

    print("=== Testing search_symbols ===")
    try:
        results = await svc.search_symbols("RELIANCE", exchange=DEFAULT_EXCHANGE)
        print(f"found {len(results)} candidates")
    except Exception as e:
        print(f"search failed: {e}")

    test_symbol = "RELIANCE"

    print("\n=== Testing get_quote ===")
    q = await svc.get_quote(test_symbol, exchange=DEFAULT_EXCHANGE)
    print(q)

    print("\n=== Testing get_multiple_quotes ===")
    quotes = await svc.get_multiple_quotes([test_symbol, "INFY", "RELIANCE"], exchange=DEFAULT_EXCHANGE)
    print(quotes)

    print("\n=== Testing get_historical_data ===")
    hist = await svc.get_historical_data(test_symbol, period="1y", exchange=DEFAULT_EXCHANGE)
    print(hist[:5])

    await svc.close()


if __name__ == "__main__":
    asyncio.run(_self_test())
