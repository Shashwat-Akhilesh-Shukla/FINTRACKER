// frontend/src/services/portfolioService.ts
import { apiClient } from './apiClient';
import { API_ENDPOINTS } from '../constants/api';

const handleApiError = (error: any, defaultMessage: string) => {
  console.error(defaultMessage, error);
  throw new Error(error?.response?.data?.detail || defaultMessage);
};

export const portfolioService = {
  getPortfolioSummary: async () => {
    try {
      console.log('Fetching portfolio summary...');
      const response = await apiClient.get(API_ENDPOINTS.PORTFOLIO.SUMMARY);
      console.log('Portfolio summary response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error fetching portfolio summary:', error);
      throw error;
    }
  },

  getHoldings: async () => {
    try {
      console.log('Fetching holdings...');
      const response = await apiClient.get(API_ENDPOINTS.PORTFOLIO.HOLDINGS);
      console.log('Holdings response:', response.data);
      
      // Transform the data if needed to match the frontend Holding type
      const holdings = response.data.map((holding: any) => ({
        id: holding.id,
        symbol: holding.symbol,
        name: holding.name,
        shares: holding.shares,
        avgCost: holding.avg_cost,
        currentPrice: holding.current_price,
        marketValue: holding.market_value,
        dayChange: holding.day_change,
        dayChangePercent: holding.day_change_percent,
        totalReturn: holding.total_return,
        totalReturnPercent: holding.total_return_percent,
        sector: holding.sector,
        industry: holding.industry,
        lastUpdated: holding.last_updated
      }));
      
      return holdings;
    } catch (error) {
      console.error('Error fetching holdings:', error);
      throw error;
    }
  },

  addHolding: async (data: { symbol: string; shares: number; avgCost: number }) => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.PORTFOLIO.HOLDINGS, data);
      return response.data;
    } catch (error: any) {
      handleApiError(error, 'Failed to add holding');
    }
  },

  getTransactions: async () => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.PORTFOLIO.TRANSACTIONS);
      return response.data;
    } catch (error: any) {
      handleApiError(error, 'Failed to fetch transactions');
    }
  },

  getPortfolioHistory: async (timeframe: string) => {
    try {
      const response = await apiClient.get(`${API_ENDPOINTS.PORTFOLIO.HISTORY}?timeframe=${timeframe}`);
      return response.data;
    } catch (error: any) {
      handleApiError(error, 'Failed to fetch portfolio history');
    }
  },

  getPortfolioMetrics: async () => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.PORTFOLIO.METRICS);
      return response.data;
    } catch (error: any) {
      handleApiError(error, 'Failed to fetch portfolio metrics');
    }
  },

  updateHolding: async (id: number, data: { shares?: number; avgCost?: number }) => {
    try {
      const response = await apiClient.put(`${API_ENDPOINTS.PORTFOLIO.HOLDINGS}/${id}`, data);
      return response.data;
    } catch (error: any) {
      handleApiError(error, 'Failed to update holding');
    }
  },

  deleteHolding: async (id: number) => {
    try {
      await apiClient.delete(`${API_ENDPOINTS.PORTFOLIO.HOLDINGS}/${id}`);
    } catch (error: any) {
      handleApiError(error, 'Failed to delete holding');
    }
  },

  addTransaction: async (data: { 
    symbol: string;
    type: 'BUY' | 'SELL';
    shares: number;
    price: number;
    date?: string;
  }) => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.PORTFOLIO.TRANSACTIONS, data);
      return response.data;
    } catch (error: any) {
      handleApiError(error, 'Failed to add transaction');
    }
  }
};
