/**
 * Route configuration that:
 * - Defines application routing paths
 * - Centralizes route management
 * - Ensures consistent navigation
 * - Prevents routing string duplication
 */

// src/constants/routes.ts
export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  DASHBOARD: '/dashboard',
  PORTFOLIO: '/portfolio',
  ANALYTICS: '/analytics',
  SETTINGS: '/settings',
  PROFILE: '/profile',
} as const;
