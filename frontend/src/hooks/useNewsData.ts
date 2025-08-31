// src/hooks/useNewsData.ts
import { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import { newsService } from '../services/newsService';
import { NewsItem } from '../types/market';

export const useNewsData = (searchQuery: string = '') => {
  const { 
    data: newsData, 
    isLoading: loading, 
    refetch,
    error 
  } = useQuery(
    ['newsData', searchQuery],
    () => newsService.getFinancialNews(searchQuery),
    {
      refetchInterval: 300000, // Refresh every 5 minutes
      staleTime: 240000, // Consider data stale after 4 minutes
      cacheTime: 600000, // Keep in cache for 10 minutes
      retry: 3,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    }
  );

  return {
    newsData: newsData || [],
    loading,
    error,
    refreshNews: refetch,
  };
};

// Additional hook for symbol-specific news
export const useSymbolNews = (symbols: string[]) => {
  const { 
    data: newsData, 
    isLoading: loading, 
    refetch,
    error 
  } = useQuery(
    ['symbolNews', symbols],
    () => newsService.getNewsForSymbols(symbols),
    {
      enabled: symbols.length > 0,
      refetchInterval: 300000,
      staleTime: 240000,
    }
  );

  return {
    newsData: newsData || [],
    loading,
    error,
    refreshNews: refetch,
  };
};

// Hook for sentiment-based news
export const useSentimentNews = (sentiment: 'positive' | 'negative' | 'neutral') => {
  const { 
    data: newsData, 
    isLoading: loading, 
    refetch,
    error 
  } = useQuery(
    ['sentimentNews', sentiment],
    () => newsService.getNewsBySentiment(sentiment),
    {
      refetchInterval: 300000,
      staleTime: 240000,
    }
  );

  return {
    newsData: newsData || [],
    loading,
    error,
    refreshNews: refetch,
  };
};
