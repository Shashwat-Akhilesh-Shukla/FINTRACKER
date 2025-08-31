from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.services.market_data_service import market_data_service
from datetime import datetime, timedelta
import numpy as np

router = APIRouter()

@router.get("/market/quote/{symbol}")
async def get_market_quote(symbol: str):
    """Get real-time market quote for a symbol"""
    # try:
    #     quote = await market_data_service.get_quote(symbol.upper())
    #     if not quote:
    #         raise HTTPException(status_code=404, detail="Symbol not found")
    #     return quote
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))
    return {
        "symbol": symbol.upper(),
        "name": f"Mock {symbol.upper()}",
        "price": 100.00,
        "change": 0.00,
        "changePercent": 0.00,
        "volume": 0,
        "lastUpdated": datetime.now().isoformat()
    }

@router.post("/market/quotes")
async def get_multiple_quotes(symbols: List[str]):
    """Get real-time quotes for multiple symbols"""
    # try:
    #     quotes = await market_data_service.get_multiple_quotes([s.upper() for s in symbols])
    #     return quotes
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))
    return {
        symbol.upper(): {
            "symbol": symbol.upper(),
            "name": f"Mock {symbol.upper()}",
            "price": 100.00,
            "change": 0.00,
            "changePercent": 0.00,
            "volume": 0,
            "lastUpdated": datetime.now().isoformat()
        }
        for symbol in symbols
    }

@router.get("/search/symbols")
async def search_symbols(q: str = Query(..., min_length=1)):
    """Search for stock symbols and companies"""
    # try:
    #     # This would typically use a more comprehensive search API
    #     # For now, using a basic implementation with market data service
    #     results = await market_data_service.search_symbols(q.upper())
    #     return results
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))
    return [
        {
            "symbol": q.upper(),
            "name": f"Mock Company {q.upper()}",
            "type": "Equity",
            "region": "US",
            "marketOpen": "09:30",
            "marketClose": "16:00",
            "timezone": "UTC-04",
            "currency": "USD"
        }
    ]

@router.get("/predictions/{symbol}")
async def get_prediction(
    symbol: str,
    timeframe: str = Query("1m", regex="^(1d|1w|1m|3m|6m|1y)$")
):
    """Get AI-powered price predictions (mock data for now)"""
    try:
        # Get current price as baseline
        quote = await market_data_service.get_quote(symbol.upper())
        if not quote:
            raise HTTPException(status_code=404, detail="Symbol not found")

        current_price = quote["price"]
        
        # Generate mock prediction data
        timeframe_days = {
            "1d": 1, "1w": 7, "1m": 30,
            "3m": 90, "6m": 180, "1y": 365
        }
        
        days = timeframe_days[timeframe]
        dates = [(datetime.now() + timedelta(days=x)).strftime("%Y-%m-%d") 
                for x in range(days)]
        
        # Generate slightly random but trending predictions
        trend = np.random.choice([1, -1])  # Random trend direction
        volatility = 0.02  # 2% daily volatility
        predictions = []
        last_price = current_price
        
        for date in dates:
            change = np.random.normal(0.001 * trend, volatility)
            last_price *= (1 + change)
            predictions.append({
                "date": date,
                "price": round(last_price, 2),
                "confidence": round(np.random.uniform(0.6, 0.9), 2)
            })

        return {
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "current_price": current_price,
            "predictions": predictions,
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market/history/{symbol}")
async def get_historical_data(
    symbol: str,
    period: str = Query("1y", regex="^(1d|5d|1mo|3mo|6mo|1y|2y|5y|10y|max)$")
):
    """Get historical price data for a symbol"""
    try:
        data = await market_data_service.get_historical_data(symbol.upper(), period)
        if not data:
            raise HTTPException(status_code=404, detail="Historical data not found")
        return {
            "symbol": symbol.upper(),
            "period": period,
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))