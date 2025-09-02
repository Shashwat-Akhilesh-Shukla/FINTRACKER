import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from .models import Portfolio, Holding, Transaction, MarketData
from .schemas import PerformanceMetrics, SectorAllocation, CorrelationMatrix
from .market_data import FinnhubMarketDataService
from datetime import datetime, timedelta
import asyncio
from asyncio import TimeoutError
import logging

logger = logging.getLogger(__name__)

class AnalyticsEngine:
    def __init__(self):
        self.risk_free_rate = 0.05
        self.market_symbol = "^GSPC"  # S&P 500 for Finnhub
        self.market_data_service = FinnhubMarketDataService()
        self.timeout = 60

    async def calculate_performance_metrics(self, db: Session, user_id: int) -> PerformanceMetrics:
        try:
            async with asyncio.timeout(self.timeout):
                portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
                if not portfolio:
                    return self._default_metrics()

                returns = await self._calculate_portfolio_returns(db, portfolio.id)
                if len(returns) < 30:
                    return self._default_metrics()

                returns_array = np.array(returns)

                # Calculate metrics
                sharpe_ratio = await self._calculate_sharpe_ratio(returns_array)
                alpha = await self._calculate_alpha(returns_array, portfolio.id)
                beta = await self._calculate_beta(returns_array)
                volatility = await self._calculate_volatility(returns_array)
                max_drawdown = await self._calculate_max_drawdown(returns_array)
                sortino_ratio = await self._calculate_sortino_ratio(returns_array)

                return PerformanceMetrics(
                    sharpe_ratio=sharpe_ratio,
                    alpha=alpha,
                    beta=beta,
                    volatility=volatility,
                    max_drawdown=max_drawdown,
                    sortino_ratio=sortino_ratio
                )
        except asyncio.TimeoutError:
            logger.error(f"Analytics calculation timed out for user {user_id}")
            return self._default_metrics()
        except Exception as e:
            logger.error(f"Analytics calculation failed: {e}")
            return self._default_metrics()

    async def _calculate_portfolio_returns(self, db: Session, portfolio_id: int) -> List[float]:
        """Calculate actual daily portfolio returns from transactions"""
        try:
            transactions = db.query(Transaction).filter(
                Transaction.portfolio_id == portfolio_id
            ).order_by(Transaction.transaction_date).all()

            if len(transactions) < 2:
                return []

            daily_portfolio_values = {}
            holdings_tracker = {}

            for tx in transactions:
                date_key = tx.transaction_date.date()
                
                if tx.type == "BUY":
                    if tx.symbol not in holdings_tracker:
                        holdings_tracker[tx.symbol] = {"shares": 0, "total_cost": 0}
                    
                    old_shares = holdings_tracker[tx.symbol]["shares"]
                    old_cost = holdings_tracker[tx.symbol]["total_cost"]
                    new_shares = old_shares + tx.shares
                    new_cost = old_cost + (tx.shares * tx.price)
                    
                    holdings_tracker[tx.symbol] = {
                        "shares": new_shares,
                        "total_cost": new_cost,
                        "avg_cost": new_cost / new_shares if new_shares > 0 else 0
                    }
                elif tx.type == "SELL" and tx.symbol in holdings_tracker:
                    holdings_tracker[tx.symbol]["shares"] -= tx.shares
                    if holdings_tracker[tx.symbol]["shares"] <= 0:
                        del holdings_tracker[tx.symbol]

                # Calculate portfolio value
                portfolio_value = 0
                symbols = list(holdings_tracker.keys())
                
                if symbols:
                    try:
                        current_prices = await self._get_current_prices(db, symbols)
                        for symbol, position in holdings_tracker.items():
                            if symbol in current_prices and position["shares"] > 0:
                                portfolio_value += position["shares"] * current_prices[symbol]
                    except Exception as e:
                        logger.error(f"Error getting prices: {e}")
                        portfolio_value = sum(pos["total_cost"] for pos in holdings_tracker.values())

                daily_portfolio_values[date_key] = portfolio_value

            # Calculate daily returns
            sorted_dates = sorted(daily_portfolio_values.keys())
            returns = []
            
            for i in range(1, len(sorted_dates)):
                prev_value = daily_portfolio_values[sorted_dates[i-1]]
                curr_value = daily_portfolio_values[sorted_dates[i]]
                if prev_value > 0:
                    daily_return = (curr_value - prev_value) / prev_value
                    returns.append(daily_return)

            return returns

        except Exception as e:
            logger.error(f"Error in portfolio returns: {e}")
            return []

    def _store_market_data(self, db: Session, symbol: str, data: Dict[str, Dict]):
        """Store market data in database"""
        try:
            for date_str, values in data.items():
                date = datetime.strptime(date_str, "%Y-%m-%d")
                market_data = MarketData(
                    symbol=symbol,
                    date=date,
                    open=values["open"],
                    high=values["high"],
                    low=values["low"],
                    close=values["close"],
                    volume=values["volume"],
                    adjusted_close=values["adjusted_close"]
                )
                db.merge(market_data)
            db.commit()
        except Exception as e:
            logger.error(f"Error storing market data: {e}")
            db.rollback()

    async def _get_historical_prices(self, db: Session, symbol: str, days: int = 365) -> Dict[str, Dict]:
        """Get historical prices via market data service with DB fallback"""
        try:
            if self.market_data_service.is_available:
                data = await self.market_data_service.get_historical_data(
                    symbol=symbol,
                    interval="D",
                    lookback_days=days
                )
                if data:
                    self._store_market_data(db, symbol, data)
                    return data
        except Exception as e:
            logger.error(f"Finnhub error for {symbol}: {e}")
            self.market_data_service.disable_service()

        # Fallback to database
        return self._get_db_market_data(db, symbol, days)

    def _get_db_market_data(self, db: Session, symbol: str, days: int) -> Dict[str, Dict]:
        """Get historical data from database"""
        cutoff_date = datetime.now() - timedelta(days=days)
        data = db.query(MarketData).filter(
            MarketData.symbol == symbol,
            MarketData.date >= cutoff_date
        ).order_by(MarketData.date).all()

        results = {}
        for row in data:
            date_str = row.date.strftime("%Y-%m-%d")
            results[date_str] = {
                "open": row.open,
                "high": row.high,
                "low": row.low,
                "close": row.close,
                "volume": row.volume,
                "adjusted_close": row.adjusted_close
            }
        return results

    async def _get_current_prices(self, db: Session, symbols: List[str]) -> Dict[str, float]:
        """Get current prices via market data service with DB fallback"""
        prices = {}
        
        try:
            if self.market_data_service.is_available:
                async with asyncio.timeout(self.timeout):
                    for symbol in symbols:
                        try:
                            price = await self.market_data_service.get_latest_price(symbol)
                            if price is not None:
                                prices[symbol] = price
                                continue
                        except Exception as e:
                            logger.error(f"Error getting price for {symbol}: {e}")
                        
                        # Fallback to database for this symbol
                        latest_price = db.query(MarketData.close).filter(
                            MarketData.symbol == symbol
                        ).order_by(MarketData.date.desc()).first()
                        
                        if latest_price:
                            prices[symbol] = latest_price[0]
        except asyncio.TimeoutError:
            logger.error("Timeout getting current prices")
            self.market_data_service.disable_service()
        except Exception as e:
            logger.error(f"Error getting current prices: {e}")

        # Final fallback to stored prices for missing symbols
        for symbol in symbols:
            if symbol not in prices:
                latest = db.query(MarketData).filter(
                    MarketData.symbol == symbol
                ).order_by(MarketData.date.desc()).first()
                if latest:
                    prices[symbol] = latest.close

        return prices

    async def _calculate_correlation(self, db: Session, symbol1: str, symbol2: str) -> float:
        """Calculate correlation using market data service with DB fallback"""
        try:
            data1 = await self._get_historical_prices(db, symbol1)
            data2 = await self._get_historical_prices(db, symbol2)

            common_dates = sorted(set(data1.keys()) & set(data2.keys()))
            if len(common_dates) < 20:
                return 0.0

            returns1 = []
            returns2 = []

            for i in range(1, len(common_dates)):
                r1 = (data1[common_dates[i]]["close"] / data1[common_dates[i-1]]["close"]) - 1
                r2 = (data2[common_dates[i]]["close"] / data2[common_dates[i-1]]["close"]) - 1
                returns1.append(r1)
                returns2.append(r2)

            if not returns1 or not returns2:
                return 0.0

            correlation = np.corrcoef(returns1, returns2)[0, 1]
            return float(correlation) if not np.isnan(correlation) else 0.0

        except Exception as e:
            logger.error(f"Error calculating correlation: {e}")
            return 0.0

    async def _calculate_sharpe_ratio(self, returns: np.ndarray) -> float:
        if len(returns) == 0:
            return 0.0
        
        annual_return = np.mean(returns) * 252
        annual_volatility = np.std(returns, ddof=1) * np.sqrt(252)
        
        if annual_volatility == 0:
            return 0.0
            
        sharpe = (annual_return - self.risk_free_rate) / annual_volatility
        return round(float(sharpe), 3)

    async def _calculate_alpha(self, returns: np.ndarray, portfolio_id: int) -> float:
        if len(returns) == 0:
            return 0.0
        
        try:
            market_returns = await self._get_market_returns(len(returns))
            if len(market_returns) != len(returns):
                return 0.0

            portfolio_return = np.mean(returns)
            market_return = np.mean(market_returns)
            beta = await self._calculate_beta_with_market(returns, market_returns)
            daily_risk_free = self.risk_free_rate / 252

            expected_return = daily_risk_free + beta * (market_return - daily_risk_free)
            alpha = portfolio_return - expected_return
            alpha_annualized = alpha * 252 * 100
            
            return round(float(alpha_annualized), 3)
        except Exception as e:
            logger.error(f"Error calculating alpha: {e}")
            return 0.0

    async def _calculate_beta(self, returns: np.ndarray) -> float:
        if len(returns) == 0:
            return 1.0
        
        try:
            market_returns = await self._get_market_returns(len(returns))
            return await self._calculate_beta_with_market(returns, market_returns)
        except Exception as e:
            logger.error(f"Error calculating beta: {e}")
            return 1.0

    async def _calculate_beta_with_market(self, portfolio_returns: np.ndarray, market_returns: np.ndarray) -> float:
        if len(portfolio_returns) != len(market_returns) or len(portfolio_returns) == 0:
            return 1.0

        covariance_matrix = np.cov(portfolio_returns, market_returns)
        covariance = covariance_matrix[0, 1]
        market_variance = np.var(market_returns, ddof=1)

        if market_variance == 0:
            return 1.0

        beta = covariance / market_variance
        return round(float(beta), 3)

    async def _get_market_returns(self, num_days: int) -> np.ndarray:
        """Get market returns via market data service"""
        try:
            data = await self._get_historical_prices(None, self.market_symbol, num_days + 50)
            if not data:
                return np.array([])

            sorted_dates = sorted(data.keys())
            market_prices = [data[date]["close"] for date in sorted_dates]
            
            market_returns = []
            for i in range(1, len(market_prices)):
                daily_return = (market_prices[i] - market_prices[i-1]) / market_prices[i-1]
                market_returns.append(daily_return)

            return np.array(market_returns[-num_days:])
        except Exception as e:
            logger.error(f"Error getting market returns: {e}")
            return np.array([])

    async def _calculate_volatility(self, returns: np.ndarray) -> float:
        if len(returns) == 0:
            return 0.0
        
        daily_volatility = np.std(returns, ddof=1)
        annualized_volatility = daily_volatility * np.sqrt(252)
        return round(float(annualized_volatility * 100), 2)

    async def _calculate_max_drawdown(self, returns: np.ndarray) -> float:
        if len(returns) == 0:
            return 0.0
        
        cumulative_returns = np.cumprod(1 + returns)
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = np.min(drawdown)
        return round(float(abs(max_drawdown) * 100), 2)

    async def _calculate_sortino_ratio(self, returns: np.ndarray) -> float:
        if len(returns) == 0:
            return 0.0
        
        annual_return = np.mean(returns) * 252
        daily_risk_free = self.risk_free_rate / 252
        downside_returns = returns[returns < daily_risk_free]
        
        if len(downside_returns) == 0:
            return 100.0
        
        downside_variance = np.mean((downside_returns - daily_risk_free) ** 2)
        downside_deviation = np.sqrt(downside_variance) * np.sqrt(252)
        
        if downside_deviation == 0:
            return 0.0
        
        sortino = (annual_return - self.risk_free_rate) / downside_deviation
        return round(float(sortino), 3)

    async def calculate_sector_allocation(self, db: Session, user_id: int) -> List[SectorAllocation]:
        portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
        if not portfolio:
            return []

        holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio.id).all()
        if not holdings:
            return []

        total_value = 0
        sector_data = {}
        symbols = [h.symbol for h in holdings]
        current_prices = await self._get_current_prices(db, symbols)

        for holding in holdings:
            current_price = current_prices.get(holding.symbol, holding.current_price)
            market_value = holding.shares * current_price
            total_value += market_value

            sector = holding.sector or "Other"
            sector_data[sector] = sector_data.get(sector, 0) + market_value

        if total_value == 0:
            return []

        allocation = []
        for sector, value in sector_data.items():
            percentage = (value / total_value) * 100
            allocation.append(SectorAllocation(
                sector=sector,
                percentage=round(percentage, 2),
                value=round(value, 2)
            ))

        return sorted(allocation, key=lambda x: x.percentage, reverse=True)

    async def calculate_correlation_matrix(self, db: Session, user_id: int) -> Optional[CorrelationMatrix]:
        portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
        if not portfolio:
            return None

        holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio.id).all()
        if len(holdings) < 2:
            return None

        symbols = [h.symbol for h in holdings]
        n = len(symbols)
        matrix = []

        for i in range(n):
            row = []
            for j in range(n):
                if i == j:
                    row.append(1.0)
                else:
                    correlation = await self._calculate_correlation(db, symbols[i], symbols[j])
                    row.append(correlation)
            matrix.append(row)

        return CorrelationMatrix(symbols=symbols, matrix=matrix)

    async def calculate_diversification_score(self, db: Session, user_id: int) -> float:
        portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
        if not portfolio:
            return 0.0

        holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio.id).all()
        if not holdings:
            return 0.0

        symbols = [h.symbol for h in holdings]
        current_prices = await self._get_current_prices(db, symbols)

        total_value = 0
        market_values = []

        for holding in holdings:
            current_price = current_prices.get(holding.symbol, holding.current_price)
            market_value = holding.shares * current_price
            total_value += market_value
            market_values.append(market_value)

        if total_value == 0:
            return 0.0

        weights = [mv / total_value for mv in market_values]
        hhi = sum(w**2 for w in weights)

        n = len(holdings)
        min_hhi = 1/n if n > 0 else 1
        max_hhi = 1

        if max_hhi == min_hhi:
            return 1.0

        normalized_hhi = (hhi - min_hhi) / (max_hhi - min_hhi)
        diversification_score = 1 - normalized_hhi

        return round(max(0, min(1, diversification_score)), 3)

    def _default_metrics(self) -> PerformanceMetrics:
        return PerformanceMetrics(
            sharpe_ratio=0.0,
            alpha=0.0,
            beta=1.0,
            volatility=0.0,
            max_drawdown=0.0,
            sortino_ratio=0.0
        )

analytics_engine = AnalyticsEngine()
