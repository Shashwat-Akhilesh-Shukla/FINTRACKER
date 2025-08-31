/**
 * Application configuration that:
 * - Defines app-wide settings and constants
 * - Sets data refresh intervals
 * - Configures pagination defaults
 * - Specifies chart timeframe options
 */

// src/constants/config.ts
export const APP_CONFIG = {
  NAME: 'FinTracker Pro',
  VERSION: '1.0.0',
  REFRESH_INTERVALS: {
    PORTFOLIO: 60000, // 1 minute
    NEWS: 300000, // 5 minutes
    MARKET_DATA: 30000, // 30 seconds
  },
  PAGINATION: {
    DEFAULT_PAGE_SIZE: 20,
    PAGE_SIZE_OPTIONS: [10, 20, 50, 100],
  },
  CHART_TIMEFRAMES: ['1D', '1W', '1M', '3M', '6M', '1Y', '2Y', '5Y'],
} as const;
