// src/constants/api.ts - FIXED VERSION
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    REFRESH: '/auth/refresh',
    LOGOUT: '/auth/logout',
    VERIFY: '/auth/verify',
    ME: '/auth/me'
  },
  PORTFOLIO: {
    SUMMARY: '/portfolio/summary',
    HISTORY: '/portfolio/history',
    METRICS: '/portfolio/metrics',
    HOLDINGS: '/portfolio/holdings',
    TRANSACTIONS: '/portfolio/get_transactions',
  },
  MARKET: {
    QUOTE: '/market/quote',
    SEARCH: '/market/search',
    NEWS: '/market/news',
    PREDICTION: '/market/prediction',
  },
} as const;

// FIXED: Use import.meta.env instead of process.env for Vite
export const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
export const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';
