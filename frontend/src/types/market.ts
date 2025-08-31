// src/types/market.ts
export interface Quote {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap: number;
  pe: number;
  dividend: number;
  dividendYield: number;
  high52Week: number;
  low52Week: number;
  lastUpdated: string;
}

export interface NewsItem {
  id: string;
  title: string;
  summary: string;
  content: string;
  source: string;
  author: string;
  publishedAt: string;
  url: string;
  imageUrl?: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  sentimentScore: number;
  symbols: string[];
  tags: string[];
}

export interface PredictionResult {
  symbol: string;
  timeframe: string;
  prediction: number;
  confidence: number;
  direction: 'up' | 'down' | 'neutral';
  factors: string[];
  generatedAt: string;
}

export interface MarketState {
  quotes: Record<string, Quote>;
  news: NewsItem[];
  predictions: Record<string, PredictionResult>;
  watchlist: string[];
  isLoading: boolean;
  error: string | null;
}
