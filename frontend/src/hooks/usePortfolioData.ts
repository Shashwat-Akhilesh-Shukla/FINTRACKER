// src/hooks/usePortfolioData.ts
import { useQuery } from 'react-query';
import { portfolioService } from '../services/portfolioService';
import { PortfolioSummary } from '../types/portfolio';

export const usePortfolioData = () => {
  const { data, isLoading, error, refetch } = useQuery<PortfolioSummary>(
    'portfolioSummary',
    portfolioService.getPortfolioSummary,
    {
      refetchInterval: 60000, // Refresh every minute
      staleTime: 30000,
    }
  );

  return {
    portfolioData: data,
    loading: isLoading,
    error,
    refresh: refetch
  };
};