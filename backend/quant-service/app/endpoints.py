from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import get_db
from .analytics import analytics_engine
from .benchmarks import benchmark_service
from .schemas import AnalyticsResponse, BenchmarkComparison, HealthResponse, BenchmarkData
from .models import Portfolio, Transaction, MarketData, SecurityMetadata
from .market_data import FinnhubMarketDataService
from datetime import datetime, timedelta
import asyncio
from typing import List, Dict
import logging

router = APIRouter()
security = HTTPBearer()

# Initialize market data service
market_data_service = FinnhubMarketDataService()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify token with auth service"""
    try:
        return {"user_id": 1}  # Mock for development
    except Exception:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

@router.on_event("startup")
async def startup_event():
    """Initialize market data service and create tables"""
    from .database import engine, Base
    Base.metadata.create_all(bind=engine)

@router.get("/analytics/{user_id}", response_model=AnalyticsResponse)
async def get_portfolio_analytics(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive portfolio analytics"""
    try:
        logger.info(f"Calculating analytics for user {user_id}")
        
        # Add overall timeout for the entire endpoint
        async with asyncio.timeout(120):  # 2 minute max
            performance_metrics = await analytics_engine.calculate_performance_metrics(db, user_id)
            logger.info("Performance metrics calculated")

            sector_allocation = await analytics_engine.calculate_sector_allocation(db, user_id)
            logger.info("Sector allocation calculated")

            correlation_matrix = await analytics_engine.calculate_correlation_matrix(db, user_id)
            logger.info("Correlation matrix calculated")

            diversification_score = await analytics_engine.calculate_diversification_score(db, user_id)
            logger.info("Diversification score calculated")

            response = AnalyticsResponse(
                user_id=user_id,
                performance_metrics=performance_metrics,
                sector_allocation=sector_allocation,
                correlation_matrix=correlation_matrix,
                diversification_score=diversification_score,
                last_updated=datetime.utcnow()
            )

            logger.info("Analytics response prepared")
            return response

    except asyncio.TimeoutError:
        logger.error(f"Analytics calculation timed out for user {user_id}")
        raise HTTPException(status_code=504, detail="Analytics calculation timed out")
    except Exception as e:
        logger.error(f"Analytics calculation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Analytics calculation failed: {str(e)}"
        )

@router.get("/benchmark-comparison/{user_id}", response_model=BenchmarkComparison)
async def get_benchmark_comparison(
    user_id: int,
    timeframe: str = Query("1Y", regex="^(1M|6M|1Y|3Y|MAX)$"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Portfolio vs benchmark comparison using market data service"""
    try:
        async with asyncio.timeout(120):
            # Get benchmark data
            benchmark_returns = await benchmark_service.calculate_benchmark_returns(timeframe)
            
            # Calculate portfolio historical data
            portfolio_data = await _calculate_portfolio_historical_data(db, user_id, timeframe)
            
            return BenchmarkComparison(
                timeframe=timeframe,
                portfolio_data=portfolio_data,
                benchmark_returns=benchmark_returns
            )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Benchmark comparison timed out")
    except Exception as e:
        logger.error(f"Benchmark comparison failed: {e}")
        raise HTTPException(status_code=500, detail=f"Benchmark comparison failed: {str(e)}")

async def _calculate_portfolio_historical_data(db: Session, user_id: int, timeframe: str) -> List[BenchmarkData]:
    """Calculate historical portfolio values using market data service"""
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
    if not portfolio:
        return []

    # Get transactions for the timeframe
    end_date = datetime.now()
    timeframe_days = {"1M": 30, "6M": 180, "1Y": 365, "3Y": 1095, "MAX": 3650}
    start_date = end_date - timedelta(days=timeframe_days.get(timeframe, 365))

    transactions = db.query(Transaction).filter(
        Transaction.portfolio_id == portfolio.id,
        Transaction.transaction_date >= start_date
    ).order_by(Transaction.transaction_date).all()

    if not transactions:
        return []

    # Build portfolio positions over time
    holdings_tracker = {}
    historical_data = []

    # Get benchmark data for comparison using market data service
    benchmark_data = await market_data_service.get_market_benchmark_data("^GSPC", timeframe_days.get(timeframe, 365))
    
    if not benchmark_data:
        return []

    benchmark_start_price = benchmark_data[0]["close"] if benchmark_data else 1.0

    for i, tx in enumerate(transactions):
        date_str = tx.transaction_date.strftime("%Y-%m-%d")

        # Update holdings
        if tx.type == "BUY":
            if tx.symbol not in holdings_tracker:
                holdings_tracker[tx.symbol] = {"shares": 0, "total_cost": 0}
            holdings_tracker[tx.symbol]["shares"] += tx.shares
            holdings_tracker[tx.symbol]["total_cost"] += (tx.shares * tx.price)
        elif tx.type == "SELL" and tx.symbol in holdings_tracker:
            holdings_tracker[tx.symbol]["shares"] -= tx.shares
            if holdings_tracker[tx.symbol]["shares"] <= 0:
                del holdings_tracker[tx.symbol]

        # Calculate portfolio value using current market prices
        portfolio_value = 0
        symbols = list(holdings_tracker.keys())
        
        if symbols:
            try:
                # Get current prices for all symbols
                current_prices = await analytics_engine._get_current_prices(db, symbols)
                for symbol, position in holdings_tracker.items():
                    if position["shares"] > 0:
                        price = current_prices.get(symbol, tx.price)  # Fallback to transaction price
                        portfolio_value += position["shares"] * price
            except Exception as e:
                logger.error(f"Error getting historical prices: {e}")
                # Fallback to transaction prices
                for symbol, position in holdings_tracker.items():
                    if position["shares"] > 0:
                        portfolio_value += position["shares"] * tx.price

        # Get benchmark value for the same date
        benchmark_normalized = portfolio_value  # Default fallback
        try:
            tx_date = tx.transaction_date.date()
            # Find closest benchmark date
            closest_benchmark = None
            for bm_data in benchmark_data:
                bm_date = datetime.strptime(bm_data["date"], "%Y-%m-%d").date()
                if bm_date >= tx_date:
                    closest_benchmark = bm_data
                    break
            
            if closest_benchmark:
                benchmark_on_date = closest_benchmark["close"]
                if i == 0:
                    initial_portfolio_value = portfolio_value
                benchmark_normalized = (benchmark_on_date / benchmark_start_price) * initial_portfolio_value
        except Exception as e:
            logger.error(f"Error getting benchmark data: {e}")

        historical_data.append(BenchmarkData(
            date=date_str,
            portfolio_value=round(portfolio_value, 2),
            benchmark_value=round(benchmark_normalized, 2)
        ))

    return historical_data

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="quant-analytics-service",
        version="1.0.0"
    )

@router.get("/market-data/{symbol}")
async def get_market_data(
    symbol: str,
    days: int = Query(30, gt=0, le=365),
    db: Session = Depends(get_db)
):
    """Get market data with DB caching"""
    try:
        data = await market_data_service.get_historical_data(symbol, lookback_days=days)
        
        # Cache in DB
        if data:
            for date_str, values in data.items():
                market_data = MarketData(
                    symbol=symbol,
                    date=datetime.strptime(date_str, "%Y-%m-%d"),
                    **values
                )
                db.merge(market_data)
            db.commit()
        
        return data
    except Exception as e:
        logger.error(f"Error getting market data: {e}")
        # Fallback to DB
        return analytics_engine._get_db_market_data(db, symbol, days)
