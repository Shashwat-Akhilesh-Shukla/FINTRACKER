// src/services/apiClient.ts
import axios from 'axios';
import { BASE_URL } from '../constants/api';

export const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 180000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true
});

// Add request interceptor to log requests (for debugging)
apiClient.interceptors.request.use(
  (config) => {
    console.log('Making request to:', config.url);
    console.log('Request data:', config.data);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to log responses (for debugging)
apiClient.interceptors.response.use(
  (response) => {
    console.log('Response from:', response.config.url);
    console.log('Response data:', response.data);
    return response;
  },
  (error) => {
    console.error('API Error:', {
      url: error.config?.url,
      status: error.response?.status,
      data: error.response?.data
    });
    return Promise.reject(error);
  }
);

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    config.withCredentials = true;
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling and token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        if (refreshToken) {
          const response = await axios.post(`${BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken
          });
          
          const newAccessToken = response.data.access_token;
          localStorage.setItem('accessToken', newAccessToken);
          
          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);
