// src/store/slices/marketSlice.ts
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { MarketState, Quote, NewsItem } from '../../types/market';
import { marketService } from '../../services/marketService';

const initialState: MarketState = {
  quotes: {},
  news: [],
  predictions: {},
  watchlist: JSON.parse(localStorage.getItem('watchlist') || '[]'),
  isLoading: false,
  error: null,
};

export const fetchQuote = createAsyncThunk(
  'market/fetchQuote',
  async (symbol: string, { rejectWithValue }) => {
    try {
      return await marketService.getQuote(symbol);
    } catch (error: any) {
      return rejectWithValue(error.message);
    }
  }
);

export const fetchNews = createAsyncThunk(
  'market/fetchNews',
  async (query: string = '', { rejectWithValue }) => {
    try {
      return await marketService.getNews(query);
    } catch (error: any) {
      return rejectWithValue(error.message);
    }
  }
);

export const fetchPrediction = createAsyncThunk(
  'market/fetchPrediction',
  async (data: { symbol: string; timeframe: string }, { rejectWithValue }) => {
    try {
      return await marketService.getPrediction(data.symbol, data.timeframe);
    } catch (error: any) {
      return rejectWithValue(error.message);
    }
  }
);

const marketSlice = createSlice({
  name: 'market',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    addToWatchlist: (state, action: PayloadAction<string>) => {
      if (!state.watchlist.includes(action.payload)) {
        state.watchlist.push(action.payload);
        localStorage.setItem('watchlist', JSON.stringify(state.watchlist));
      }
    },
    removeFromWatchlist: (state, action: PayloadAction<string>) => {
      state.watchlist = state.watchlist.filter(symbol => symbol !== action.payload);
      localStorage.setItem('watchlist', JSON.stringify(state.watchlist));
    },
    updateQuote: (state, action: PayloadAction<Quote>) => {
      state.quotes[action.payload.symbol] = action.payload;
    },
    setNews: (state, action: PayloadAction<NewsItem[]>) => {
      state.news = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch Quote
      .addCase(fetchQuote.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchQuote.fulfilled, (state, action) => {
        state.isLoading = false;
        state.quotes[action.payload.symbol] = action.payload;
      })
      .addCase(fetchQuote.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Fetch News
      .addCase(fetchNews.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchNews.fulfilled, (state, action) => {
        state.isLoading = false;
        state.news = action.payload;
      })
      .addCase(fetchNews.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Fetch Prediction
      .addCase(fetchPrediction.fulfilled, (state, action) => {
        state.predictions[action.payload.symbol] = action.payload;
      });
  },
});

export const { 
  clearError, 
  addToWatchlist, 
  removeFromWatchlist, 
  updateQuote, 
  setNews 
} = marketSlice.actions;

export { marketSlice };
