// src/services/authService.ts - UPDATED for real backend
import { apiClient } from './apiClient';
import { API_ENDPOINTS } from '../constants/api';
import { LoginCredentials, RegisterData, AuthResponse } from '../types/auth';

export const authService = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.AUTH.LOGIN, credentials);
      
      const backendData = response.data;
      return {
        user: {
          id: backendData.user?.id || '1',
          email: credentials.email,
          firstName: backendData.user?.first_name || 'User',
          lastName: backendData.user?.last_name || 'Name',
          avatar: backendData.user?.avatar,
          createdAt: backendData.user?.created_at || new Date().toISOString(),
          lastLogin: backendData.user?.last_login
        },
        accessToken: backendData.access_token,
        refreshToken: backendData.refresh_token
      };
    } catch (error: any) {
      if (error.response?.status === 401) {
        throw new Error('Invalid email or password');
      }
      if (error.code === 'ERR_NETWORK') {
        throw new Error('Unable to connect to server. Please check your connection.');
      }
      throw new Error(error.response?.data?.detail || 'Login failed. Please try again.');
    }
  },

  register: async (data: RegisterData): Promise<AuthResponse> => {
    try {
      const registerPayload = {
        email: data.email,
        password: data.password,
        first_name: data.firstName,
        last_name: data.lastName
      };
      
      const response = await apiClient.post(API_ENDPOINTS.AUTH.REGISTER, registerPayload);
      const backendData = response.data;
      
      return {
        user: {
          id: backendData.user?.id || '1',
          email: data.email,
          firstName: data.firstName,
          lastName: data.lastName,
          avatar: backendData.user?.avatar,
          createdAt: backendData.user?.created_at || new Date().toISOString(),
          lastLogin: backendData.user?.last_login
        },
        accessToken: backendData.access_token,
        refreshToken: backendData.refresh_token
      };
    } catch (error: any) {
      if (error.response?.status === 400) {
        throw new Error('Email already registered');
      }
      if (error.code === 'ERR_NETWORK') {
        throw new Error('Unable to connect to server. Please check your connection.');
      }
      throw new Error(error.response?.data?.detail || 'Registration failed. Please try again.');
    }
  },

  logout: async (): Promise<void> => {
    try {
      await apiClient.post(API_ENDPOINTS.AUTH.LOGOUT);
    } catch (error) {
      // Logout should succeed even if API call fails
      console.warn('Logout API call failed, but proceeding with local logout');
    }
  },

  refreshToken: async (): Promise<AuthResponse> => {
    try {
      const refreshToken = localStorage.getItem('refreshToken');
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await apiClient.post(API_ENDPOINTS.AUTH.REFRESH, {
        refresh_token: refreshToken
      });
      
      const backendData = response.data;
      
      return {
        user: {
          id: backendData.user?.id || '1',
          email: backendData.user?.email || '',
          firstName: backendData.user?.first_name || 'User',
          lastName: backendData.user?.last_name || 'Name',
          avatar: backendData.user?.avatar,
          createdAt: backendData.user?.created_at || new Date().toISOString(),
          lastLogin: backendData.user?.last_login
        },
        accessToken: backendData.access_token,
        refreshToken: backendData.refresh_token
      };
    } catch (error: any) {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      throw new Error('Session expired. Please login again.');
    }
  },

  // New method to get current user profile
  getCurrentUser: async (): Promise<any> => {
    try {
      const response = await apiClient.get('/auth/me');
      return response.data;
    } catch (error) {
      throw new Error('Failed to get user profile');
    }
  },

  verifyToken: async (): Promise<boolean> => {
    try {
      const token = localStorage.getItem('accessToken');
      if (!token) return false;

      const response = await apiClient.get(API_ENDPOINTS.AUTH.VERIFY, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      return response.status === 200;
    } catch (error) {
      return false;
    }
  }
};
