// src/pages/Dashboard/Dashboard.tsx
import React, { useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Typography,
  Paper,
  Card,
  CardContent,
  Button,
  Chip,
  Avatar,
  Divider
} from '@mui/material';
import {
  TrendingUp,
  AccountBalance,
  ShowChart,
  Notifications,
  Add
} from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import PortfolioSummary from '../../components/portfolio/PortfolioSummary';
import HoldingsTable from '../../components/portfolio/HoldingsTable';
import PerformanceCharts from '../../components/charts/PerformanceCharts';
import NewsPanel from '../../components/news/NewsPanel';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { ErrorAlert } from '../../components/common/ErrorAlert';
import {
  fetchPortfolioSummary,
  fetchPortfolioHoldings
} from '../../store/slices/portfolioSlice';
import { RootState, AppDispatch } from '../../store/store';
import { ROUTES } from '../../constants/routes';
import { formatCurrency, formatPercentage } from '../../utils/formatters';

const RecentActivity: React.FC = () => {
  const activities = [
    { type: 'BUY', symbol: 'AAPL', shares: 10, price: 175.23, time: '2 hours ago' },
    { type: 'SELL', symbol: 'GOOGL', shares: 5, price: 2750.45, time: '1 day ago' },
    { type: 'DIVIDEND', symbol: 'MSFT', amount: 15.60, time: '3 days ago' },
  ];

  return (
    <Card elevation={2}>
      <CardContent>
        <Typography variant="h6" fontWeight={600} gutterBottom>
          Recent Activity
        </Typography>
        <Divider sx={{ mb: 2 }} />
        {activities.map((activity, index) => (
          <Box key={index} display="flex" justifyContent="space-between" py={1}>
            <Box>
              <Chip
                label={activity.type}
                color={activity.type === 'BUY' ? 'success' : activity.type === 'SELL' ? 'error' : 'info'}
                size="small"
                sx={{ mr: 1 }}
              />
              <Typography variant="body2" component="span">
                {activity.symbol}
                {activity.shares && ` - ${activity.shares} shares`}
                {activity.amount && ` - ${formatCurrency(activity.amount)}`}
              </Typography>
            </Box>
            <Typography variant="caption" color="textSecondary">
              {activity.time}
            </Typography>
          </Box>
        ))}
      </CardContent>
    </Card>
  );
};

const Dashboard: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const { user } = useSelector((state: RootState) => state.auth);
  const { isLoading, error } = useSelector((state: RootState) => state.portfolio);

  useEffect(() => {
  dispatch(fetchPortfolioSummary());
  dispatch(fetchPortfolioHoldings());

  const interval = setInterval(() => {
    dispatch(fetchPortfolioSummary());
    dispatch(fetchPortfolioHoldings());
  }, 300000); // refresh every 5 minutes

  return () => clearInterval(interval);
  }, [dispatch]);

  if (isLoading) return <LoadingSpinner message="Loading dashboard..." />;
  if (error) return <ErrorAlert error={error} />;

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      {/* Header */}
      <Box mb={4}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Box>
            <Typography variant="h4" fontWeight={700} gutterBottom>
              Welcome back {user?.firstName}!
            </Typography>
            <Typography variant="body1" color="textSecondary">
              Here's what's happening with your portfolio today.
            </Typography>
          </Box>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => navigate(ROUTES.PORTFOLIO)}
            sx={{ borderRadius: 2 }}
          >
            Add Investment
          </Button>
        </Box>
      </Box>

      {/* Main Content */}
      <Grid container spacing={3}>
        {/* Left Column */}
        <Grid item xs={12} lg={8}>
          {/* Portfolio Summary */}
          <Box mb={3}>
            <PortfolioSummary />
          </Box>

          {/* Performance Charts */}
          <Box mb={3}>
            <PerformanceCharts />
          </Box>

          {/* Holdings Table */}
          <Box mb={3}>
            <Card elevation={2}>
              <CardContent>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Portfolio Holdings
                </Typography>
                <HoldingsTable />
              </CardContent>
            </Card>
          </Box>          
        </Grid>

        {/* Right Column */}
        <Grid item xs={12} lg={4}>
          {/* News Panel */}
          <Box mb={3}>
            <NewsPanel />
          </Box>

          {/* Recent Activity */}
          <Box mb={3}>
            <RecentActivity />
          </Box>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;
