from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class PerformanceMetrics(BaseModel):
    sharpe_ratio: float
    alpha: float
    beta: float
    volatility: float
    max_drawdown: float
    sortino_ratio: float
    
class BenchmarkData(BaseModel):
    date: str
    portfolio_value: float
    benchmark_value: float

class CorrelationMatrix(BaseModel):
    symbols: List[str]
    matrix: List[List[float]]
    
class SectorAllocation(BaseModel):
    sector: str
    percentage: float
    value: float

class AnalyticsResponse(BaseModel):
    user_id: int
    performance_metrics: PerformanceMetrics
    sector_allocation: List[SectorAllocation]
    correlation_matrix: Optional[CorrelationMatrix]
    diversification_score: float
    last_updated: datetime

class BenchmarkComparison(BaseModel):
    timeframe: str
    portfolio_data: List[BenchmarkData]
    benchmark_returns: Dict[str, float]
    
class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
