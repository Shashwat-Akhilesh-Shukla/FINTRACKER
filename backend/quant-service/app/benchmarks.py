import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List

class BenchmarkService:
    def __init__(self):
        self.benchmarks = {
            "NIFTY50": "^NSEI",
            "SP500": "^GSPC", 
            "NASDAQ": "^IXIC",
            "SENSEX": "^BSESN"
        }
    
    async def get_benchmark_data(self, timeframe: str) -> Dict[str, List[Dict]]:
        period_map = {"1M": "1mo", "6M": "6mo", "1Y": "1y", "3Y": "3y", "MAX": "max"}
        period = period_map.get(timeframe, "1y")
        benchmark_data = {}
        
        for name, symbol in self.benchmarks.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period)
                
                data = []
                for date, row in hist.iterrows():
                    data.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "close": float(row['Close'])
                    })
                benchmark_data[name] = data
            except Exception as e:
                print(f"Error fetching {name}: {e}")
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
