from datetime import datetime, timedelta
from typing import Dict, List
from .market_data import FinnhubMarketDataService
import logging

logger = logging.getLogger(__name__)

class BenchmarkService:
    def __init__(self):
        self.benchmarks = {
            "NIFTY50": "^NSEI",
            "SP500": "^GSPC", 
            "NASDAQ": "^IXIC",
            "SENSEX": "^BSESN"
        }
        self.market_data_service = FinnhubMarketDataService()

    async def get_benchmark_data(self, timeframe: str) -> Dict[str, List[Dict]]:
        period_days = {
            "1M": 30, 
            "6M": 180, 
            "1Y": 365, 
            "3Y": 1095, 
            "MAX": 2000
        }
        days = period_days.get(timeframe, 365)

        benchmark_data = {}
        for name, symbol in self.benchmarks.items():
            try:
                data = await self.market_data_service.get_market_benchmark_data(symbol, days)
                benchmark_data[name] = data
            except Exception as e:
                logger.error(f"Error fetching {name}: {e}")
                benchmark_data[name] = []

        return benchmark_data

    async def calculate_benchmark_returns(self, timeframe: str) -> Dict[str, float]:
        data = await self.get_benchmark_data(timeframe)
        returns = {}

        for name, prices in data.items():
            if len(prices) >= 2:
                start_price = prices[0]["close"]
                end_price = prices[-1]["close"]
                return_pct = ((end_price - start_price) / start_price) * 100
                returns[name] = round(return_pct, 2)
            else:
                returns[name] = 0.0

        return returns

benchmark_service = BenchmarkService()
