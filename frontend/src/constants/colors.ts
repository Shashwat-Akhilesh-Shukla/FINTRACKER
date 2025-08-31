/**
 * Color constants module that:
 * - Defines consistent color scheme for charts
 * - Maintains sector-specific color mapping
 * - Provides gradient color arrays
 * - Ensures color consistency across app
 */

// src/constants/colors.ts
export const CHART_COLORS = {
  PRIMARY: '#1e3c72',
  SECONDARY: '#2a5298',
  SUCCESS: '#00c851',
  ERROR: '#ff4444',
  WARNING: '#ffbb33',
  INFO: '#33b5e5',
  GRADIENT: ['#1e3c72', '#2a5298', '#4a69bd', '#5b7bc0', '#7b8ad1'],
} as const;

export const SECTOR_COLORS = {
  TECHNOLOGY: '#1e3c72',
  HEALTHCARE: '#00c851',
  FINANCE: '#2a5298',
  ENERGY: '#ff4444',
  CONSUMER: '#ffbb33',
  INDUSTRIALS: '#33b5e5',
  UTILITIES: '#aa66cc',
  MATERIALS: '#ff8800',
  REAL_ESTATE: '#99cc00',
  TELECOMMUNICATIONS: '#ff6699',
} as const;
