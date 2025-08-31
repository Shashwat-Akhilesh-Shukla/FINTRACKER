// src/services/marketService.ts
import { apiClient } from './apiClient';
import { API_ENDPOINTS } from '../constants/api';
import { Quote, NewsItem, PredictionResult } from '../types/market';

export const marketService = {
  getQuote: async (symbol: string): Promise<Quote> => {
    try {
      // Call the portfolio service via API Gateway for market quotes
      const response = await apiClient.get(`/portfolio/market/quote/${encodeURIComponent(symbol)}`);
      return response.data;
    } catch (error: any) {
      console.error(`Failed to fetch quote for ${symbol}:`, error);
      throw new Error(`Failed to fetch quote for ${symbol}: ${error.response?.data?.detail || error.message}`);
    }
  },

  getNews: async (query?: string): Promise<NewsItem[]> => {
    try {
      // Call the news service via API Gateway
      const params = new URLSearchParams();
      if (query) {
        params.append('q', query);
      }
      const response = await apiClient.get(`/market/news?${params.toString()}`);
      return response.data;
    } catch (error: any) {
      console.error('Failed to fetch news:', error);
      return []; // Return empty array on error instead of throwing
    }
  },

  getPrediction: async (symbol: string, timeframe: string): Promise<PredictionResult> => {
    try {
      // Call the portfolio service for predictions
      const response = await apiClient.get(
        `/portfolio/predictions/${encodeURIComponent(symbol)}?timeframe=${encodeURIComponent(timeframe)}`
      );
      return response.data;
    } catch (error: any) {
      console.error(`Failed to get prediction for ${symbol}:`, error);
      
      // Return a fallback prediction object instead of throwing
      return {
        symbol,
        timeframe,
        prediction: 0,
        confidence: 0,
        direction: 'neutral' as 'up' | 'down' | 'neutral',
        factors: ['Prediction temporarily unavailable'],
        generatedAt: new Date().toISOString()
      };
    }
  },

  searchSymbols: async (query: string): Promise<{ symbol: string; name: string }[]> => {
    try {
      // Call the portfolio service for symbol search
      const response = await apiClient.get(`/portfolio/search/symbols?q=${encodeURIComponent(query)}`);
      return response.data;
    } catch (error: any) {
      console.error('Failed to search symbols:', error);
      
      // Return fallback search results for common stocks
      const fallbackResults = [
        { symbol: 'AAPL', name: 'Apple Inc.' },
        { symbol: 'GOOGL', name: 'Alphabet Inc.' },
        { symbol: 'MSFT', name: 'Microsoft Corporation' },
        { symbol: 'AMZN', name: 'Amazon.com Inc.' },
        { symbol: 'TSLA', name: 'Tesla Inc.' },
      ].filter(stock => 
        stock.symbol.toLowerCase().includes(query.toLowerCase()) ||
        stock.name.toLowerCase().includes(query.toLowerCase())
      );
      
      return fallbackResults;
    }
  },

  // Add method to get multiple quotes efficiently
  getMultipleQuotes: async (symbols: string[]): Promise<Record<string, Quote>> => {
    try {
      const response = await apiClient.post('/portfolio/market/quotes', { symbols });
      return response.data;
    } catch (error: any) {
      console.error('Failed to fetch multiple quotes:', error);
      
      // Fallback: fetch quotes individually
      const quotes: Record<string, Quote> = {};
      for (const symbol of symbols.slice(0, 5)) { // Limit to 5 to avoid too many requests
        try {
          quotes[symbol] = await marketService.getQuote(symbol);
        } catch (e) {
          console.error(`Failed to fetch quote for ${symbol}:`, e);
        }
      }
      return quotes;
    }
  },

  // Add method to get historical data
  getHistoricalData: async (symbol: string, period: string = '1y'): Promise<any[]> => {
    try {
      const response = await apiClient.get(
        `/portfolio/market/history/${encodeURIComponent(symbol)}?period=${period}`
      );
      return response.data;
    } catch (error: any) {
      console.error(`Failed to fetch historical data for ${symbol}:`, error);
      return [];
    }
  }
};
