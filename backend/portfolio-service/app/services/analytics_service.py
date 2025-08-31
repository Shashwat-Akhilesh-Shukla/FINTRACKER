import numpy as np
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.portfolio import Portfolio
from app.models.holding import Holding
from app.models.transaction import Transaction
from app.core.external_apis import market_data_api

class AnalyticsService:
    """Portfolio analytics service that:
    - Calculates advanced portfolio metrics
    - Provides risk analysis
    - Generates performance analytics
    - Computes sector allocation and diversification metrics
    """
    
    def __init__(self, db: Session):
        self.db = db

    def calculate_portfolio_metrics(self, portfolio_id: int) -> Dict:
        """Calculate comprehensive portfolio metrics"""
        portfolio = self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if not portfolio:
            return {}

        holdings = self.db.query(Holding).filter(Holding.portfolio_id == portfolio_id).all()
        if not holdings:
            return self._default_metrics()

        # Get historical returns for calculations
        returns_data = self._get_portfolio_returns(holdings)
        
        return {
            "sharpe_ratio": self._calculate_sharpe_ratio(returns_data),
            "beta": self._calculate_beta(returns_data),
            "alpha": self._calculate_alpha(returns_data),
            "var_95": self._calculate_var(returns_data),
            "max_drawdown": self._calculate_max_drawdown(returns_data),
            "volatility": self._calculate_volatility(returns_data),
            "annualized_return": self._calculate_annualized_return(returns_data),
            "information_ratio": self._calculate_information_ratio(returns_data)
        }

    def calculate_sector_allocation(self, portfolio_id: int) -> List[Dict]:
        """Calculate sector allocation breakdown"""
        holdings = self.db.query(Holding).filter(Holding.portfolio_id == portfolio_id).all()
        total_value = sum(h.market_value for h in holdings)
        
        if total_value == 0:
            return []

        sector_data = {}
        for holding in holdings:
            sector = holding.sector or "Other"
            if sector not in sector_data:
                sector_data[sector] = {"value": 0, "count": 0}
            
            sector_data[sector]["value"] += holding.market_value
            sector_data[sector]["count"] += 1

        allocation = []
        for sector, data in sector_data.items():
            percentage = (data["value"] / total_value * 100)
            allocation.append({
                "sector": sector,
                "value": data["value"],
                "percentage": percentage,
                "count": data["count"]
            })

        return sorted(allocation, key=lambda x: x["percentage"], reverse=True)

    def calculate_risk_metrics(self, portfolio_id: int) -> Dict:
        """Calculate risk-specific metrics"""
        holdings = self.db.query(Holding).filter(Holding.portfolio_id == portfolio_id).all()
        
        if not holdings:
            return {}

        total_value = sum(h.market_value for h in holdings)
        weights = [h.market_value / total_value for h in holdings if total_value > 0]
        
        # Portfolio concentration risk
        concentration_risk = self._calculate_concentration_risk(weights)
        
        # Correlation analysis would require historical data
        correlation_matrix = self._calculate_correlation_matrix(holdings)
        
        return {
            "concentration_risk": concentration_risk,
            "diversification_ratio": self._calculate_diversification_ratio(weights),
            "correlation_matrix": correlation_matrix
        }

    def _get_portfolio_returns(self, holdings: List[Holding]) -> List[float]:
        """Get historical portfolio returns (simplified)"""
        # In a real implementation, this would use stored daily portfolio values
        # For now, return mock data based on current holdings
        return [0.01, -0.005, 0.015, 0.008, -0.012, 0.020, 0.003, -0.008, 0.012, 0.007]

    def _calculate_sharpe_ratio(self, returns: List[float], risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        if not returns:
            return 0.0
        
        returns_array = np.array(returns)
        excess_returns = returns_array - (risk_free_rate / 252)  # Daily risk-free rate
        
        if np.std(excess_returns) == 0:
            return 0.0
        
        return float(np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252))

    def _calculate_beta(self, returns: List[float], market_returns: Optional[List[float]] = None) -> float:
        """Calculate portfolio beta"""
        if not returns:
            return 1.0
        
        # Mock market returns (S&P 500)
        if not market_returns:
            market_returns = [0.008, -0.003, 0.012, 0.005, -0.008, 0.015, 0.001, -0.005, 0.009, 0.004]
        
        if len(returns) != len(market_returns):
            return 1.0
        
        returns_array = np.array(returns)
        market_array = np.array(market_returns)
        
        covariance = np.cov(returns_array, market_array)[0, 1]
        market_variance = np.var(market_array)
        
        return float(covariance / market_variance) if market_variance > 0 else 1.0

    def _calculate_alpha(self, returns: List[float]) -> float:
        """Calculate Jensen's alpha"""
        beta = self._calculate_beta(returns)
        portfolio_return = np.mean(returns) if returns else 0
        market_return = 0.008  # Mock market return
        risk_free_rate = 0.02 / 252  # Daily risk-free rate
        
        alpha = portfolio_return - (risk_free_rate + beta * (market_return - risk_free_rate))
        return float(alpha * 252 * 100)  # Annualized percentage

    def _calculate_var(self, returns: List[float], confidence_level: float = 0.95) -> float:
        """Calculate Value at Risk"""
        if not returns:
            return 0.0
        
        returns_array = np.array(returns)
        return float(np.percentile(returns_array, (1 - confidence_level) * 100) * -1)

    def _calculate_max_drawdown(self, returns: List[float]) -> float:
        """Calculate maximum drawdown"""
        if not returns:
            return 0.0
        
        cumulative_returns = np.cumprod(1 + np.array(returns))
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdowns = (cumulative_returns - running_max) / running_max
        
        return float(np.min(drawdowns) * 100)  # Percentage

    def _calculate_volatility(self, returns: List[float]) -> float:
        """Calculate annualized volatility"""
        if not returns:
            return 0.0
        
        returns_array = np.array(returns)
        return float(np.std(returns_array) * np.sqrt(252) * 100)  # Annualized percentage

    def _calculate_annualized_return(self, returns: List[float]) -> float:
        """Calculate annualized return"""
        if not returns:
            return 0.0
        
        cumulative_return = np.prod(1 + np.array(returns))
        periods = len(returns)
        annualized = (cumulative_return ** (252 / periods)) - 1
        
        return float(annualized * 100)  # Percentage

    def _calculate_information_ratio(self, returns: List[float]) -> float:
        """Calculate information ratio"""
        if not returns:
            return 0.0
        
        # Mock benchmark returns
        benchmark_returns = [0.007] * len(returns)
        excess_returns = np.array(returns) - np.array(benchmark_returns)
        
        tracking_error = np.std(excess_returns)
        return float(np.mean(excess_returns) / tracking_error) if tracking_error > 0 else 0.0

    def _calculate_concentration_risk(self, weights: List[float]) -> float:
        """Calculate concentration risk using Herfindahl index"""
        if not weights:
            return 0.0
        
        return float(sum(w ** 2 for w in weights))

    def _calculate_diversification_ratio(self, weights: List[float]) -> float:
        """Calculate diversification ratio"""
        if not weights:
            return 0.0
        
        # Simplified calculation
        n = len(weights)
        equal_weight = 1 / n if n > 0 else 0
        concentration = sum(w ** 2 for w in weights)
        
        return float(1 - concentration) if concentration > 0 else 0.0

    def _calculate_correlation_matrix(self, holdings: List[Holding]) -> Dict:
        """Calculate correlation matrix (simplified)"""
        symbols = [h.symbol for h in holdings]
        n = len(symbols)
        
        # Mock correlation matrix
        correlation_matrix = {}
        for i, symbol1 in enumerate(symbols):
            correlation_matrix[symbol1] = {}
            for j, symbol2 in enumerate(symbols):
                if i == j:
                    correlation_matrix[symbol1][symbol2] = 1.0
                else:
                    # Mock correlation (in reality, calculate from historical data)
                    correlation_matrix[symbol1][symbol2] = 0.3 + (hash(symbol1 + symbol2) % 40) / 100
        
        return correlation_matrix

    def _default_metrics(self) -> Dict:
        """Return default metrics when no data available"""
        return {
            "sharpe_ratio": 0.0,
            "beta": 1.0,
            "alpha": 0.0,
            "var_95": 0.0,
            "max_drawdown": 0.0,
            "volatility": 0.0,
            "annualized_return": 0.0,
            "information_ratio": 0.0
        }
