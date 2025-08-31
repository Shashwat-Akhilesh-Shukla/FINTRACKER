// src/store/slices/portfolioSlice.ts

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { PortfolioState, Holding, Transaction, TransactionCreate } from '../../types/portfolio';
import { portfolioService } from '../../services/portfolioService';

const initialState: PortfolioState = {
  summary: null,
  holdings: [],
  transactions: [],
  metrics: null,
  history: [],
  sectorAllocation: [],
  isLoading: false,
  error: null, // Track when data was last fetched
};

export const fetchPortfolioSummary = createAsyncThunk(
  'portfolio/fetchSummary',
  async (_, { rejectWithValue }) => {
    try {
      const data = await portfolioService.getPortfolioSummary();
      return data;
    } catch (error: any) {
      return rejectWithValue(error.message);
    }
  }
);

export const fetchPortfolioTransactions = createAsyncThunk(
  'portfolio/fetchTransactions',
  async (_, { rejectWithValue }) => {
    try {
      const data = await portfolioService.getTransactions();
      return data;
    } catch (error: any) {
      return rejectWithValue(error.message);
    }
  }
);

export const fetchPortfolioHoldings = createAsyncThunk(
  'portfolio/fetchHoldings',
  async (_, { rejectWithValue }) => {
    try {
      const holdings = await portfolioService.getHoldings();
      return holdings;
    } catch (error: any) {
      return rejectWithValue(error.message);
    }
  }
);

export const fetchPortfolioMetrics = createAsyncThunk(
  'portfolio/fetchMetrics',
  async (_, { rejectWithValue }) => {
    try {
      const data = await portfolioService.getPortfolioMetrics();
      return data;
    } catch (error: any) {
      return rejectWithValue(error.message);
    }
  }
);

export const fetchPortfolioHistory = createAsyncThunk(
  'portfolio/fetchHistory',
  async (timeframe: string, { rejectWithValue }) => {
    try {
      const data = await portfolioService.getPortfolioHistory(timeframe);
      return data;
    } catch (error: any) {
      return rejectWithValue(error.message);
    }
  }
);

export const addHolding = createAsyncThunk(
  'portfolio/addHolding',
  async (data: { symbol: string; shares: number; price: number }, { rejectWithValue, dispatch }) => {
    try {
      const holding = await portfolioService.addHolding(data.symbol, data.shares, data.avgCost);
      // Refresh summary after adding holding
      dispatch(fetchPortfolioSummary());
      return holding;
    } catch (error: any) {
      return rejectWithValue(error.message);
    }
  }
);

export const addTransaction = createAsyncThunk(
  'portfolio/addTransaction',
  async (data: TransactionCreate, { rejectWithValue, dispatch }) => {
    try {
      const transaction = await portfolioService.addTransaction(data);
      // Refresh summary after adding transaction
      dispatch(fetchPortfolioSummary());
      return transaction;
    } catch (error: any) {
      return rejectWithValue(error.message);
    }
  }
);

const portfolioSlice = createSlice({
  name: 'portfolio',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    // Optimistic updates for better UX
    updateHoldingPrice: (state, action: PayloadAction<{ symbol: string; price: number }>) => {
      const holding = state.holdings.find(h => h.symbol === action.payload.symbol);
      if (holding) {
        holding.currentPrice = action.payload.price;
        holding.marketValue = holding.shares * action.payload.price;
        holding.totalReturn = holding.marketValue - (holding.shares * holding.avgCost);
        holding.totalReturnPercent = (holding.totalReturn / (holding.shares * holding.avgCost)) * 100;
      }
    },
    // Set loading state manually if needed
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    }
  },
  extraReducers: (builder) => {
    builder
      // Fetch Summary
      .addCase(fetchPortfolioSummary.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchPortfolioSummary.fulfilled, (state, action) => {
        state.isLoading = false;
        state.summary = action.payload;
        state.error = null;
      })
      .addCase(fetchPortfolioSummary.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
        // Don't clear existing summary on error - keep showing last known values
      })

      // Fetch Holdings
      .addCase(fetchPortfolioHoldings.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchPortfolioHoldings.fulfilled, (state, action) => {
        state.isLoading = false;
        state.holdings = action.payload;
        state.error = null;
      })
      .addCase(fetchPortfolioHoldings.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })

      // Fetch Metrics
      .addCase(fetchPortfolioMetrics.fulfilled, (state, action) => {
        state.metrics = action.payload.metrics;
        state.sectorAllocation = action.payload.sectorAllocation;
      })

      // Fetch History
      .addCase(fetchPortfolioHistory.fulfilled, (state, action) => {
        state.history = action.payload;
      })

      // Add Holding
      .addCase(addHolding.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(addHolding.fulfilled, (state, action) => {
        state.isLoading = false;
        // Don't add to holdings array here - let fetchPortfolioSummary refresh everything
        state.error = null;
      })
      .addCase(addHolding.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })

      // Add Transaction
      .addCase(addTransaction.fulfilled, (state, action) => {
        state.transactions.push(action.payload);
      });
  },
});

export const { clearError, updateHoldingPrice, setLoading } = portfolioSlice.actions;
export { portfolioSlice };
