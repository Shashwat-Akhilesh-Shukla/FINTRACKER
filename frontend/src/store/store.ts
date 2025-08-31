/**
 * Redux store configuration that:
 * - Sets up global state management
 * - Combines all feature reducers
 * - Configures middleware and dev tools
 * - Exports type definitions for TypeScript
 */

// src/store/store.ts
import { configureStore } from '@reduxjs/toolkit';
import { authSlice } from './slices/authSlice';
import { portfolioSlice } from './slices/portfolioSlice';
import { marketSlice } from './slices/marketSlice';
import { apiSlice } from './api/apiSlice';

export const store = configureStore({
  reducer: {
    auth: authSlice.reducer,
    portfolio: portfolioSlice.reducer,
    market: marketSlice.reducer,
    api: apiSlice.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
      },
    }).concat(apiSlice.middleware),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
