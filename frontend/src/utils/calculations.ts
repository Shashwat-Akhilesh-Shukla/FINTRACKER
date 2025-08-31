// src/utils/calculations.ts
import { Holding, PortfolioMetrics } from '../types/portfolio';

export const calculatePortfolioValue = (holdings: Holding[]): number => {
  return holdings.reduce((total, holding) => total + holding.marketValue, 0);
};

export const calculatePortfolioReturn = (holdings: Holding[]): number => {
  return holdings.reduce((total, holding) => total + holding.totalReturn, 0);
};

export const calculatePortfolioReturnPercent = (holdings: Holding[]): number => {
  const totalCost = holdings.reduce((total, holding) => 
    total + (holding.shares * holding.avgCost), 0);
  const totalReturn = calculatePortfolioReturn(holdings);
  
  return totalCost > 0 ? (totalReturn / totalCost) * 100 : 0;
};

export const calculateWeight = (holding: Holding, totalValue: number): number => {
  return totalValue > 0 ? (holding.marketValue / totalValue) * 100 : 0;
};

export const calculateSharpeRatio = (
  returns: number[],
  riskFreeRate: number = 0.02
): number => {
  if (returns.length === 0) return 0;
  
  const avgReturn = returns.reduce((sum, r) => sum + r, 0) / returns.length;
  const variance = returns.reduce((sum, r) => sum + Math.pow(r - avgReturn, 2), 0) / returns.length;
  const stdDev = Math.sqrt(variance);
  
  return stdDev > 0 ? (avgReturn - riskFreeRate) / stdDev : 0;
};

export const calculateBeta = (
  portfolioReturns: number[],
  marketReturns: number[]
): number => {
  if (portfolioReturns.length !== marketReturns.length || portfolioReturns.length === 0) {
    return 1; // Default beta
  }
  
  const portfolioAvg = portfolioReturns.reduce((sum, r) => sum + r, 0) / portfolioReturns.length;
  const marketAvg = marketReturns.reduce((sum, r) => sum + r, 0) / marketReturns.length;
  
  let covariance = 0;
  let marketVariance = 0;
  
  for (let i = 0; i < portfolioReturns.length; i++) {
    const portfolioDiff = portfolioReturns[i] - portfolioAvg;
    const marketDiff = marketReturns[i] - marketAvg;
    
    covariance += portfolioDiff * marketDiff;
    marketVariance += marketDiff * marketDiff;
  }
  
  return marketVariance > 0 ? covariance / marketVariance : 1;
};

export const calculateMaxDrawdown = (values: number[]): number => {
  if (values.length === 0) return 0;
  
  let maxDrawdown = 0;
  let peak = values[0];
  
  for (let i = 1; i < values.length; i++) {
    if (values[i] > peak) {
      peak = values[i];
    } else {
      const drawdown = ((peak - values[i]) / peak) * 100;
      maxDrawdown = Math.max(maxDrawdown, drawdown);
    }
  }
  
  return maxDrawdown;
};

export const calculateVaR = (
  returns: number[],
  confidenceLevel: number = 0.95
): number => {
  if (returns.length === 0) return 0;
  
  const sortedReturns = [...returns].sort((a, b) => a - b);
  const index = Math.floor((1 - confidenceLevel) * returns.length);
  
  return Math.abs(sortedReturns[index] || 0);
};
