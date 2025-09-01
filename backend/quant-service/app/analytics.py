import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from .models import Portfolio, Holding, Transaction
from .schemas import PerformanceMetrics, SectorAllocation, CorrelationMatrix
from datetime import datetime, timedelta
import yfinance as yf
import asyncio

class AnalyticsEngine:
    def __init__(self):
        self.risk_free_rate = 0.05  # 5% annual risk-free rate
        self.market_symbol = "^GSPC"  # S&P 500 as market benchmark
    
    def calculate_performance_metrics(self, db: Session, user_id: int) -> PerformanceMetrics:
        """Calculate all performance metrics for user's portfolio - REAL CALCULATIONS"""
        portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
        if not portfolio:
            return self._default_metrics()
        
        # Get REAL portfolio returns from actual transactions
        returns = self._calculate_portfolio_returns(db, portfolio.id)
        if len(returns) < 30:  # Need minimum data points
            return self._default_metrics()
        
        returns_array = np.array(returns)
        
        # Calculate ALL metrics with proper formulas
        sharpe_ratio = self._calculate_sharpe_ratio(returns_array)
        alpha = self._calculate_alpha(returns_array, portfolio.id)
        beta = self._calculate_beta(returns_array)
        volatility = self._calculate_volatility(returns_array)
        max_drawdown = self._calculate_max_drawdown(returns_array)
        sortino_ratio = self._calculate_sortino_ratio(returns_array)
        
        return PerformanceMetrics(
            sharpe_ratio=sharpe_ratio,
            alpha=alpha,
            beta=beta,
            volatility=volatility,
            max_drawdown=max_drawdown,
            sortino_ratio=sortino_ratio
        )
    
    def _calculate_portfolio_returns(self, db: Session, portfolio_id: int) -> List[float]:
        """REAL CALCULATION: Calculate actual daily portfolio returns from transactions"""
        # Get all transactions ordered by date
        transactions = db.query(Transaction).filter(
            Transaction.portfolio_id == portfolio_id
        ).order_by(Transaction.transaction_date).all()
        
        if len(transactions) < 2:
            return []
        
        # Build portfolio positions over time
        daily_portfolio_values = {}
        holdings_tracker = {}  # symbol -> {shares, avg_cost}
        
        for tx in transactions:
            date_key = tx.transaction_date.date()
            
            if tx.type == "BUY":
                if tx.symbol not in holdings_tracker:
                    holdings_tracker[tx.symbol] = {"shares": 0, "total_cost": 0}
                
                # Update position
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
                # Proportionally reduce total cost
                if holdings_tracker[tx.symbol]["shares"] > 0:
                    cost_per_share = holdings_tracker[tx.symbol]["total_cost"] / (holdings_tracker[tx.symbol]["shares"] + tx.shares)
                    holdings_tracker[tx.symbol]["total_cost"] -= (tx.shares * cost_per_share)
                else:
                    # Sold all shares
                    del holdings_tracker[tx.symbol]
            
            # Calculate portfolio value for this date using CURRENT MARKET PRICES
            portfolio_value = 0
            symbols = list(holdings_tracker.keys())
            
            if symbols:
                # Get current prices for all symbols
                try:
                    current_prices = self._get_current_prices(symbols)
                    for symbol, position in holdings_tracker.items():
                        if symbol in current_prices and position["shares"] > 0:
                            portfolio_value += position["shares"] * current_prices[symbol]
                except Exception as e:
                    print(f"Error getting prices: {e}")
                    # Fallback to cost basis
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
    
    def _get_current_prices(self, symbols: List[str]) -> Dict[str, float]:
        """Get current market prices for symbols"""
        prices = {}
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="2d")
                if not hist.empty:
                    prices[symbol] = float(hist['Close'].iloc[-1])
            except Exception as e:
                print(f"Error fetching price for {symbol}: {e}")
                prices[symbol] = 100.0  # Fallback
        return prices
    
    def _calculate_sharpe_ratio(self, returns: np.ndarray) -> float:
        """REAL Sharpe Ratio: (Portfolio Return - Risk Free Rate) / Portfolio Volatility"""
        if len(returns) == 0:
            return 0.0
        
        # Annualized calculations
        annual_return = np.mean(returns) * 252
        annual_volatility = np.std(returns, ddof=1) * np.sqrt(252)
        
        if annual_volatility == 0:
            return 0.0
        
        sharpe = (annual_return - self.risk_free_rate) / annual_volatility
        return round(float(sharpe), 3)
    
    def _calculate_alpha(self, returns: np.ndarray, portfolio_id: int) -> float:
        """REAL Jensen's Alpha: Portfolio Return - [Risk Free Rate + Beta * (Market Return - Risk Free Rate)]"""
        if len(returns) == 0:
            return 0.0
        
        try:
            # Get market returns for same period
            market_returns = self._get_market_returns(len(returns))
            
            if len(market_returns) != len(returns):
                return 0.0
            
            # Calculate portfolio metrics
            portfolio_return = np.mean(returns)
            market_return = np.mean(market_returns)
            beta = self._calculate_beta_with_market(returns, market_returns)
            daily_risk_free = self.risk_free_rate / 252
            
            # Jensen's Alpha formula
            expected_return = daily_risk_free + beta * (market_return - daily_risk_free)
            alpha = portfolio_return - expected_return
            
            # Annualize and convert to percentage
            alpha_annualized = alpha * 252 * 100
            return round(float(alpha_annualized), 3)
            
        except Exception as e:
            print(f"Error calculating alpha: {e}")
            return 0.0
    
    def _calculate_beta(self, returns: np.ndarray) -> float:
        """REAL Beta: Covariance(Portfolio, Market) / Variance(Market)"""
        if len(returns) == 0:
            return 1.0
        
        try:
            market_returns = self._get_market_returns(len(returns))
            return self._calculate_beta_with_market(returns, market_returns)
        except Exception as e:
            print(f"Error calculating beta: {e}")
            return 1.0
    
    def _calculate_beta_with_market(self, portfolio_returns: np.ndarray, market_returns: np.ndarray) -> float:
        """Calculate beta using actual market data"""
        if len(portfolio_returns) != len(market_returns) or len(portfolio_returns) == 0:
            return 1.0
        
        # Calculate covariance and variance
        covariance_matrix = np.cov(portfolio_returns, market_returns)
        covariance = covariance_matrix[0, 1]
        market_variance = np.var(market_returns, ddof=1)
        
        if market_variance == 0:
            return 1.0
        
        beta = covariance / market_variance
        return round(float(beta), 3)
    
    def _get_market_returns(self, num_days: int) -> np.ndarray:
        """Get actual market returns (S&P 500) for the last num_days"""
        try:
            # Get market data
            market_ticker = yf.Ticker(self.market_symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=num_days + 50)  # Buffer for weekends
            
            market_hist = market_ticker.history(start=start_date, end=end_date)
            
            if market_hist.empty:
                return np.array([])
            
            # Calculate daily returns
            market_prices = market_hist['Close'].values
            market_returns = []
            
            for i in range(1, len(market_prices)):
                daily_return = (market_prices[i] - market_prices[i-1]) / market_prices[i-1]
                market_returns.append(daily_return)
            
            # Return the most recent num_days returns
            return np.array(market_returns[-num_days:])
            
        except Exception as e:
            print(f"Error getting market returns: {e}")
            return np.array([])
    
    def _calculate_volatility(self, returns: np.ndarray) -> float:
        """REAL Volatility: Standard deviation of returns, annualized"""
        if len(returns) == 0:
            return 0.0
        
        # Standard deviation with sample correction (ddof=1)
        daily_volatility = np.std(returns, ddof=1)
        
        # Annualize: multiply by sqrt(trading days per year)
        annualized_volatility = daily_volatility * np.sqrt(252)
        
        # Convert to percentage
        return round(float(annualized_volatility * 100), 2)
    
    def _calculate_max_drawdown(self, returns: np.ndarray) -> float:
        """REAL Max Drawdown: Maximum peak-to-trough decline"""
        if len(returns) == 0:
            return 0.0
        
        # Calculate cumulative returns
        cumulative_returns = np.cumprod(1 + returns)
        
        # Calculate running maximum (peak)
        running_max = np.maximum.accumulate(cumulative_returns)
        
        # Calculate drawdown at each point
        drawdown = (cumulative_returns - running_max) / running_max
        
        # Maximum drawdown (most negative value)
        max_drawdown = np.min(drawdown)
        
        # Convert to positive percentage
        return round(float(abs(max_drawdown) * 100), 2)
    
    def _calculate_sortino_ratio(self, returns: np.ndarray) -> float:
        """REAL Sortino Ratio: (Portfolio Return - Risk Free Rate) / Downside Deviation"""
        if len(returns) == 0:
            return 0.0
        
        # Annualized return
        annual_return = np.mean(returns) * 252
        daily_risk_free = self.risk_free_rate / 252
        
        # Calculate downside deviation (only negative returns)
        downside_returns = returns[returns < daily_risk_free]
        
        if len(downside_returns) == 0:
            return 100.0  # No downside risk
        
        # Downside deviation
        downside_variance = np.mean((downside_returns - daily_risk_free) ** 2)
        downside_deviation = np.sqrt(downside_variance) * np.sqrt(252)  # Annualized
        
        if downside_deviation == 0:
            return 0.0
        
        sortino = (annual_return - self.risk_free_rate) / downside_deviation
        return round(float(sortino), 3)
    
    def _calculate_symbol_correlation(self, symbol1: str, symbol2: str) -> float:
        """REAL Correlation: Calculate actual price correlation between two symbols"""
        try:
            # Get historical data for both symbols
            ticker1 = yf.Ticker(symbol1)
            ticker2 = yf.Ticker(symbol2)
            
            # Get 1 year of data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            hist1 = ticker1.history(start=start_date, end=end_date)
            hist2 = ticker2.history(start=start_date, end=end_date)
            
            if hist1.empty or hist2.empty:
                return 0.0
            
            # Align dates and calculate returns
            combined_df = pd.DataFrame({
                symbol1: hist1['Close'],
                symbol2: hist2['Close']
            }).dropna()
            
            if len(combined_df) < 20:  # Need minimum data points
                return 0.0
            
            # Calculate daily returns
            returns1 = combined_df[symbol1].pct_change().dropna()
            returns2 = combined_df[symbol2].pct_change().dropna()
            
            # Calculate correlation
            correlation = np.corrcoef(returns1, returns2)[0, 1]
            
            if np.isnan(correlation):
                return 0.0
            
            return round(float(correlation), 3)
            
        except Exception as e:
            print(f"Error calculating correlation between {symbol1} and {symbol2}: {e}")
            return 0.0
    
    def calculate_sector_allocation(self, db: Session, user_id: int) -> List[SectorAllocation]:
        """REAL sector allocation from actual holdings"""
        portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
        if not portfolio:
            return []
        
        holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio.id).all()
        if not holdings:
            return []
        
        # Use REAL market values, not stored values
        total_value = 0
        sector_data = {}
        
        # Get current prices for all holdings
        symbols = [h.symbol for h in holdings]
        current_prices = self._get_current_prices(symbols)
        
        for holding in holdings:
            current_price = current_prices.get(holding.symbol, holding.current_price)
            market_value = holding.shares * current_price
            total_value += market_value
            
            sector = holding.sector or "Other"
            if sector not in sector_data:
                sector_data[sector] = 0
            sector_data[sector] += market_value
        
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
    
    def calculate_correlation_matrix(self, db: Session, user_id: int) -> Optional[CorrelationMatrix]:
        """REAL correlation matrix using actual price correlations"""
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
                    # REAL correlation calculation
                    correlation = self._calculate_symbol_correlation(symbols[i], symbols[j])
                    row.append(correlation)
            matrix.append(row)
        
        return CorrelationMatrix(symbols=symbols, matrix=matrix)
    
    def calculate_diversification_score(self, db: Session, user_id: int) -> float:
        """REAL diversification score using current market values"""
        portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
        if not portfolio:
            return 0.0
        
        holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio.id).all()
        if not holdings:
            return 0.0
        
        # Use REAL current market values
        symbols = [h.symbol for h in holdings]
        current_prices = self._get_current_prices(symbols)
        
        total_value = 0
        market_values = []
        
        for holding in holdings:
            current_price = current_prices.get(holding.symbol, holding.current_price)
            market_value = holding.shares * current_price
            total_value += market_value
            market_values.append(market_value)
        
        if total_value == 0:
            return 0.0
        
        # Calculate Herfindahl-Hirschman Index
        weights = [mv / total_value for mv in market_values]
        hhi = sum(w**2 for w in weights)
        
        # Diversification score: 1 = perfectly diversified, 0 = concentrated
        n = len(holdings)
        min_hhi = 1/n if n > 0 else 1  # Equal weights
        max_hhi = 1  # All in one holding
        
        if max_hhi == min_hhi:
            return 1.0
        
        normalized_hhi = (hhi - min_hhi) / (max_hhi - min_hhi)
        diversification_score = 1 - normalized_hhi
        
        return round(max(0, min(1, diversification_score)), 3)
    
    def _default_metrics(self) -> PerformanceMetrics:
        """Return default metrics when no data available"""
        return PerformanceMetrics(
            sharpe_ratio=0.0,
            alpha=0.0,
            beta=1.0,
            volatility=0.0,
            max_drawdown=0.0,
            sortino_ratio=0.0
        )

analytics_engine = AnalyticsEngine()
