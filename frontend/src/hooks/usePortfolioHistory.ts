// src/hooks/usePortfolioHistory.ts
import { useState, useEffect } from 'react';
import { apiClient } from '../services/apiClient';
import { API_ENDPOINTS } from '../constants/api';

interface Transaction {
  id: number;
  portfolio_id: number;
  symbol: string;
  type: 'BUY' | 'SELL';
  shares: number;
  price: number;
  total_amount: number;
  fees: number;
  transaction_date: string;
  note?: string;
  created_at: string;
}

interface PortfolioValue {
  date: string;
  value: number;
  holdings: Map<string, { shares: number; avgPrice: number }>;
}

export const usePortfolioHistory = (timeframe: string) => {
  const [historyData, setHistoryData] = useState<{ date: string; value: number }[]>([]);
  const [allocationData, setAllocationData] = useState<{ name: string; value: number }[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAndCalculateHistory = async () => {
      try {
        setLoading(true);
        
        // Get start date based on timeframe
        const startDate = getStartDate(timeframe);
        
        // Use apiClient instead of axios directly to include JWT token
        const response = await apiClient.get(API_ENDPOINTS.PORTFOLIO.TRANSACTIONS);
        const transactions: Transaction[] = response.data;
        
        // Filter transactions by timeframe
        const filteredTransactions = transactions.filter(tx => 
          new Date(tx.transaction_date) >= startDate
        );

        // Sort transactions by date
        const sortedTransactions = filteredTransactions.sort(
          (a, b) => new Date(a.transaction_date).getTime() - new Date(b.transaction_date).getTime()
        );

        // Calculate daily portfolio values
        const dailyValues = calculateDailyValues(sortedTransactions, startDate);
        
        // Calculate asset allocation from latest portfolio state
        const allocation = calculateAllocation(sortedTransactions);

        setHistoryData(dailyValues);
        setAllocationData(allocation);
        setError(null);

      } catch (err) {
        console.error('Error fetching portfolio history:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch portfolio history');
      } finally {
        setLoading(false);
      }
    };

    fetchAndCalculateHistory();
  }, [timeframe]);

  return { historyData, allocationData, loading, error };
};

const getStartDate = (timeframe: string): Date => {
  const now = new Date();
  switch (timeframe) {
    case '1D':
      return new Date(now.setDate(now.getDate() - 1));
    case '1W':
      return new Date(now.setDate(now.getDate() - 7));
    case '1M':
      return new Date(now.setMonth(now.getMonth() - 1));
    case '3M':
      return new Date(now.setMonth(now.getMonth() - 3));
    case '1Y':
      return new Date(now.setFullYear(now.getFullYear() - 1));
    default:
      return new Date(now.setMonth(now.getMonth() - 1)); // Default to 1M
  }
};

const calculateDailyValues = (transactions: Transaction[], startDate: Date): { date: string; value: number }[] => {
  const dailyValues: { date: string; value: number }[] = [];
  const holdings = new Map<string, { shares: number; avgPrice: number }>();
  let currentDate = new Date(startDate);
  const endDate = new Date();
  
  // Initialize with first day
  let dateStr = currentDate.toISOString().split('T')[0];
  dailyValues.push({ date: dateStr, value: 0 });

  // Process each day
  while (currentDate <= endDate) {
    dateStr = currentDate.toISOString().split('T')[0];
    
    // Process transactions for this day
    const dayTransactions = transactions.filter(tx => 
      tx.transaction_date.split('T')[0] === dateStr
    );

    // Update holdings based on transactions
    dayTransactions.forEach(tx => {
      const holding = holdings.get(tx.symbol) || { shares: 0, avgPrice: 0 };
      
      if (tx.type === 'BUY') {
        const newShares = holding.shares + tx.shares;
        const newCost = (holding.shares * holding.avgPrice) + tx.total_amount;
        holdings.set(tx.symbol, {
          shares: newShares,
          avgPrice: newCost / newShares
        });
      } else { // SELL
        const remainingShares = holding.shares - tx.shares;
        holdings.set(tx.symbol, {
          shares: remainingShares,
          avgPrice: remainingShares > 0 ? holding.avgPrice : 0
        });
      }
    });

    // Calculate portfolio value for this day
    const portfolioValue = Array.from(holdings.entries()).reduce((total, [_, holding]) => {
      return total + (holding.shares * holding.avgPrice);
    }, 0);

    dailyValues.push({
      date: dateStr,
      value: portfolioValue
    });

    // Move to next day
    currentDate.setDate(currentDate.getDate() + 1);
  }

  return dailyValues;
};

const calculateAllocation = (transactions: Transaction[]): { name: string; value: number }[] => {
  const holdings = new Map<string, { shares: number, avgPrice: number }>();
  
  // Calculate final holdings
  transactions.forEach(tx => {
    const holding = holdings.get(tx.symbol) || { shares: 0, avgPrice: 0 };
    
    if (tx.type === 'BUY') {
      const newShares = holding.shares + tx.shares;
      const newCost = (holding.shares * holding.avgPrice) + tx.total_amount;
      holdings.set(tx.symbol, {
        shares: newShares,
        avgPrice: newCost / newShares
      });
    } else { // SELL
      const remainingShares = holding.shares - tx.shares;
      holdings.set(tx.symbol, {
        shares: remainingShares,
        avgPrice: remainingShares > 0 ? holding.avgPrice : 0
      });
    }
  });

  // Convert holdings to allocation data
  const allocation = Array.from(holdings.entries())
    .filter(([_, holding]) => holding.shares > 0)
    .map(([symbol, holding]) => ({
      name: symbol,
      value: holding.shares * holding.avgPrice
    }));

  return allocation;
};
