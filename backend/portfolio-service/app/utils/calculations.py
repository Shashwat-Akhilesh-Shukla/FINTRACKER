# app/utils/calculations.py
import numpy as np
from typing import List, Dict

class PortfolioCalculations:
    
    def calculate_metrics(self, portfolio_returns: List[float], market_returns: List[float], risk_free_rate: float = 0.02) -> Dict:
        """Calculate advanced portfolio metrics"""
        if not portfolio_returns or len(portfolio_returns) < 30:
            return self._default_metrics()

        portfolio_returns = np.array(portfolio_returns)
        market_returns = np.array(market_returns[:len(portfolio_returns)])
        
        # Basic statistics
        mean_return = np.mean(portfolio_returns)
        std_return = np.std(portfolio_returns)
        
        # Annualized metrics
        annualized_return = (1 + mean_return) ** 252 - 1
        annualized_volatility = std_return * np.sqrt(252)
        
        # Sharpe Ratio
        daily_risk_free = risk_free_rate / 252
        sharpe_ratio = (mean_return - daily_risk_free) / std_return if std_return > 0 else 0
        
        # Beta and Alpha
        if len(market_returns) == len(portfolio_returns):
            covariance = np.cov(portfolio_returns, market_returns)[0][1]
            market_variance = np.var(market_returns)
            beta = covariance / market_variance if market_variance > 0 else 1
            
            market_mean = np.mean(market_returns)
            alpha = mean_return - (daily_risk_free + beta * (market_mean - daily_risk_free))
            alpha_annualized = alpha * 252
        else:
            beta = 1.0
            alpha_annualized = 0.0
        
        # Max Drawdown
        cumulative_returns = np.cumprod(1 + portfolio_returns)
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdowns = (cumulative_returns - running_max) / running_max
        max_drawdown = np.min(drawdowns) * 100
        
        # Value at Risk (95%)
        var_95 = np.percentile(portfolio_returns, 5) * 100
        
        # Information Ratio
        if len(market_returns) == len(portfolio_returns):
            excess_returns = portfolio_returns - market_returns
            tracking_error = np.std(excess_returns)
            information_ratio = np.mean(excess_returns) / tracking_error if tracking_error > 0 else 0
        else:
            information_ratio = 0.0

        return {
            "sharpeRatio": float(sharpe_ratio),
            "beta": float(beta),
            "alpha": float(alpha_annualized * 100),  # Convert to percentage
            "var95": float(var_95),
            "maxDrawdown": float(abs(max_drawdown)),
            "volatility": float(annualized_volatility * 100),  # Convert to percentage
            "annualizedReturn": float(annualized_return * 100),  # Convert to percentage
            "informationRatio": float(information_ratio)
        }

    def _default_metrics(self) -> Dict:
        """Return default metrics when insufficient data"""
        return {
            "sharpeRatio": 0.0,
            "beta": 1.0,
            "alpha": 0.0,
            "var95": 0.0,
            "maxDrawdown": 0.0,
            "volatility": 0.0,
            "annualizedReturn": 0.0,
            "informationRatio": 0.0
        }
