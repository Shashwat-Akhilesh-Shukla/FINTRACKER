// src/store/api/apiSlice.ts
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { BASE_URL } from '../../constants/api';
import { RootState } from '../store';

export const apiSlice = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({
    baseUrl: BASE_URL,
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.user ? 
        localStorage.getItem('accessToken') : null;
      
      if (token) {
        headers.set('authorization', `Bearer ${token}`);
      }
      
      headers.set('content-type', 'application/json');
      return headers;
    },
  }),
  tagTypes: ['Portfolio', 'Holdings', 'Transactions', 'News', 'Quotes'],
  endpoints: (builder) => ({
    // Portfolio endpoints
    getPortfolioSummary: builder.query({
      query: () => '/portfolio/summary',
      providesTags: ['Portfolio'],
    }),
    getHoldings: builder.query({
      query: () => '/portfolio/holdings',
      providesTags: ['Holdings'],
    }),
    addHolding: builder.mutation({
      query: (data) => ({
        url: '/portfolio/holdings',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Holdings', 'Portfolio'],
    }),
    updateHolding: builder.mutation({
      query: ({ id, ...data }) => ({
        url: `/portfolio/holdings/${id}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: ['Holdings', 'Portfolio'],
    }),
    deleteHolding: builder.mutation({
      query: (id) => ({
        url: `/portfolio/holdings/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Holdings', 'Portfolio'],
    }),
    // Market endpoints
    getQuote: builder.query({
      query: (symbol) => `/market/quote/${symbol}`,
      providesTags: ['Quotes'],
    }),
    getNews: builder.query({
      query: (query = '') => `/market/news?q=${query}`,
      providesTags: ['News'],
    }),
  }),
});

export const {
  useGetPortfolioSummaryQuery,
  useGetHoldingsQuery,
  useAddHoldingMutation,
  useUpdateHoldingMutation,
  useDeleteHoldingMutation,
  useGetQuoteQuery,
  useGetNewsQuery,
} = apiSlice;
