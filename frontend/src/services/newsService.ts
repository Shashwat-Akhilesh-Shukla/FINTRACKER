// src/services/newsService.ts
import { apiClient } from './apiClient';
import { API_ENDPOINTS } from '../constants/api';
import { NewsItem } from '../types/market';

export const newsService = {
  getFinancialNews: async (query: string = ''): Promise<NewsItem[]> => {
    try {
      // In a real application, this would call your backend API
      // For now, returning mock data that matches the NewsItem interface
      const mockNews: NewsItem[] = [
        {
          id: '1',
          title: 'Market Rally Continues as Tech Stocks Surge Higher',
          summary: 'Technology stocks led the market higher today with strong earnings reports from major companies including Apple, Microsoft, and Google.',
          content: 'Full article content would go here...',
          source: 'Financial Times',
          author: 'John Smith',
          publishedAt: new Date().toISOString(),
          url: 'https://example.com/news/1',
          imageUrl: 'https://via.placeholder.com/60x60/1e3c72/white?text=FT',
          sentiment: 'positive',
          sentimentScore: 0.8,
          symbols: ['AAPL', 'MSFT', 'GOOGL'],
          tags: ['technology', 'earnings', 'market']
        },
        {
          id: '2',
          title: 'Federal Reserve Hints at Potential Rate Changes',
          summary: 'The Federal Reserve is considering adjustments to interest rates based on recent inflation data and economic indicators.',
          content: 'Full article content would go here...',
          source: 'Reuters',
          author: 'Jane Doe',
          publishedAt: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
          url: 'https://example.com/news/2',
          imageUrl: 'https://via.placeholder.com/60x60/2a5298/white?text=R',
          sentiment: 'neutral',
          sentimentScore: 0.1,
          symbols: [],
          tags: ['fed', 'interest rates', 'inflation']
        },
        {
          id: '3',
          title: 'Energy Sector Faces Headwinds as Oil Prices Decline',
          summary: 'Oil prices dropped 3% today following concerns about global demand and increased production from major oil-producing nations.',
          content: 'Full article content would go here...',
          source: 'Bloomberg',
          author: 'Mike Johnson',
          publishedAt: new Date(Date.now() - 7200000).toISOString(), // 2 hours ago
          url: 'https://example.com/news/3',
          imageUrl: 'https://via.placeholder.com/60x60/ff4444/white?text=B',
          sentiment: 'negative',
          sentimentScore: -0.6,
          symbols: ['XOM', 'CVX', 'SLB'],
          tags: ['energy', 'oil', 'commodities']
        },
        {
          id: '4',
          title: 'Healthcare Stocks Gain on Positive Drug Trial Results',
          summary: 'Several pharmaceutical companies saw significant gains after announcing positive results from clinical trials for new medications.',
          content: 'Full article content would go here...',
          source: 'Wall Street Journal',
          author: 'Sarah Wilson',
          publishedAt: new Date(Date.now() - 10800000).toISOString(), // 3 hours ago
          url: 'https://example.com/news/4',
          imageUrl: 'https://via.placeholder.com/60x60/00c851/white?text=WSJ',
          sentiment: 'positive',
          sentimentScore: 0.7,
          symbols: ['JNJ', 'PFE', 'MRK'],
          tags: ['healthcare', 'pharmaceuticals', 'clinical trials']
        },
        {
          id: '5',
          title: 'Cryptocurrency Market Shows Mixed Signals',
          summary: 'Bitcoin and other major cryptocurrencies are trading sideways as investors await regulatory clarity from government officials.',
          content: 'Full article content would go here...',
          source: 'CNBC',
          author: 'Alex Brown',
          publishedAt: new Date(Date.now() - 14400000).toISOString(), // 4 hours ago
          url: 'https://example.com/news/5',
          imageUrl: 'https://via.placeholder.com/60x60/ffbb33/white?text=CNBC',
          sentiment: 'neutral',
          sentimentScore: 0.0,
          symbols: [],
          tags: ['cryptocurrency', 'bitcoin', 'regulation']
        },
        {
          id: '6',
          title: 'Consumer Spending Data Beats Expectations',
          summary: 'Latest consumer spending figures show resilience in the economy despite inflation concerns, boosting consumer discretionary stocks.',
          content: 'Full article content would go here...',
          source: 'MarketWatch',
          author: 'Lisa Davis',
          publishedAt: new Date(Date.now() - 18000000).toISOString(), // 5 hours ago
          url: 'https://example.com/news/6',
          imageUrl: 'https://via.placeholder.com/60x60/33b5e5/white?text=MW',
          sentiment: 'positive',
          sentimentScore: 0.5,
          symbols: ['AMZN', 'TGT', 'WMT'],
          tags: ['consumer spending', 'retail', 'economy']
        }
      ];

      // Filter news based on query if provided
      if (query && query.trim()) {
        const filteredNews = mockNews.filter(news => 
          news.title.toLowerCase().includes(query.toLowerCase()) ||
          news.summary.toLowerCase().includes(query.toLowerCase()) ||
          news.tags.some(tag => tag.toLowerCase().includes(query.toLowerCase())) ||
          news.symbols.some(symbol => symbol.toLowerCase().includes(query.toLowerCase()))
        );
        return filteredNews;
      }

      return mockNews;

    } catch (error) {
      console.error('Error fetching news:', error);
      // Return fallback data in case of error
      return [
        {
          id: 'fallback-1',
          title: 'Financial News Unavailable',
          summary: 'Unable to fetch latest financial news. Please check your connection.',
          content: '',
          source: 'System',
          author: 'System',
          publishedAt: new Date().toISOString(),
          url: '',
          sentiment: 'neutral',
          sentimentScore: 0,
          symbols: [],
          tags: []
        }
      ];
    }
  },

  // Method to get news for specific symbols
  getNewsForSymbols: async (symbols: string[]): Promise<NewsItem[]> => {
    const allNews = await newsService.getFinancialNews();
    return allNews.filter(news => 
      news.symbols.some(symbol => symbols.includes(symbol))
    );
  },

  // Method to get news by sentiment
  getNewsBySentiment: async (sentiment: 'positive' | 'negative' | 'neutral'): Promise<NewsItem[]> => {
    const allNews = await newsService.getFinancialNews();
    return allNews.filter(news => news.sentiment === sentiment);
  }
};
