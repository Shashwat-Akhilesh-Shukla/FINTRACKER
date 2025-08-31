// src/App.tsx - UPDATED to initialize auth
import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { Provider, useDispatch } from 'react-redux';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { PrivateRoute } from './components/common/PrivateRoute';
import { theme } from './theme/theme';
import { store } from './store/store';
import { ROUTES } from './constants/routes';
import { initializeAuth } from './store/slices/authSlice';
import { ReactQueryDevtools } from 'react-query/devtools';

// Pages
import { Login, Register } from './pages/Auth';
import { Dashboard } from './pages/Dashboard';
import { PortfolioPage } from './pages/Portfolio';
import { Analytics } from './pages/Analytics';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: true,
      refetchOnMount: true,
      refetchOnReconnect: true,
      retry: 1,
      staleTime: 30000,
    },
  },
});

// App content component to use hooks inside Provider
const AppContent: React.FC = () => {
  const dispatch = useDispatch();

  useEffect(() => {
    // Initialize authentication state on app start
    dispatch(initializeAuth() as any);
  }, [dispatch]);

  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path={ROUTES.LOGIN} element={<Login />} />
        <Route path={ROUTES.REGISTER} element={<Register />} />
        
        {/* Private Routes */}
        <Route path={ROUTES.DASHBOARD} element={
          <PrivateRoute>
            <Dashboard />
          </PrivateRoute>
        } />
        <Route path={ROUTES.PORTFOLIO} element={
          <PrivateRoute>
            <PortfolioPage />
          </PrivateRoute>
        } />
        <Route path={ROUTES.ANALYTICS} element={
          <PrivateRoute>
            <Analytics />
          </PrivateRoute>
        } />
        
        {/* Default Route */}
        <Route path={ROUTES.HOME} element={<Navigate to={ROUTES.DASHBOARD} replace />} />
        <Route path="*" element={<Navigate to={ROUTES.DASHBOARD} replace />} />
      </Routes>
    </Router>
  );
};

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <Provider store={store}>
        <QueryClientProvider client={queryClient}>
          <ThemeProvider theme={theme}>
            <CssBaseline />
            <AppContent />
          </ThemeProvider>
          {process.env.NODE_ENV === 'development' && <ReactQueryDevtools />}
        </QueryClientProvider>
      </Provider>
    </ErrorBoundary>
  );
};

export default App;