/**
 * Portfolio type definitions that:
 * - Define holding and transaction structures
 * - Specify portfolio metrics and summary interfaces
 * - Manage historical data point types
 * - Handle portfolio state management types
 */

// src/types/portfolio.ts
export interface Holding {
  id: string;
  symbol: string;
  name: string;
  shares: number;
  avg_cost: number;
  current_price: number;
  market_value: number;
  day_change: number;
  day_change_percent: number;
  total_return: number;
  total_return_percent: number;
  weight: number;
  sector: string;
  industry: string;
  last_price_update: string;
}

export interface Transaction {
  id: string;
  symbol: string;
  type: 'BUY' | 'SELL';
  shares: number;
  price: number;
  amount: number;
  fees: number;
  date: string;
  note?: string;
}

export interface PortfolioSummary {
  total_value: number;
  total_cost: number;
  total_return: number;
  total_return_percent: number;
  day_change: number;
  day_change_percent: number;
  cash_balance: number;
  dividend_income: number;
  last_sync: string;
}

export interface PortfolioMetrics {
  sharpeRatio: number;
  beta: number;
  alpha: number;
  var95: number;
  maxDrawdown: number;
  volatility: number;
  annualizedReturn: number;
  informationRatio: number;
  treynorRatio: number;
  calmarRatio: number;
}

export interface HistoricalDataPoint {
  date: string;
  value: number;
  change: number;
  changePercent: number;
}

export interface SectorAllocation {
  sector: string;
  value: number;
  percentage: number;
  count: number;
}

export interface PortfolioState {
  summary: PortfolioSummary | null;
  holdings: Holding[];
  transactions: Transaction[];
  metrics: PortfolioMetrics | null;
  history: HistoricalDataPoint[];
  sectorAllocation: SectorAllocation[];
  isLoading: boolean;
  error: string | null;
}
