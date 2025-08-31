// src/components/portfolio/PortfolioSummary.tsx
import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Grid,
  Box,
  LinearProgress,
} from '@mui/material';
import { TrendingUp, TrendingDown } from '@mui/icons-material';
import { usePortfolioData } from '../../hooks/usePortfolioData';
import { formatCurrency, formatPercentage } from '../../utils/formatters';

interface MetricCardProps {
  title: string;
  value: string;
  change: number;
  changePercent: number;
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value, change, changePercent }) => {
  const isPositive = change >= 0;
  
  return (
    <Card elevation={2} sx={{ height: '100%', borderRadius: 2 }}>
      <CardContent>
        <Typography variant="subtitle2" color="textSecondary" gutterBottom>
          {title}
        </Typography>
        <Typography variant="h4" sx={{ fontWeight: 600, mb: 1 }}>
          {value}
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          {isPositive ? <TrendingUp color="success" /> : <TrendingDown color="error" />}
          <Typography
            variant="body2"
            color={isPositive ? 'success.main' : 'error.main'}
            sx={{ ml: 0.5, fontWeight: 500 }}
          >
            {formatPercentage(changePercent)}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

const PortfolioSummary: React.FC = () => {
  const { portfolioData, loading, error } = usePortfolioData();
  
  if (loading) return <LinearProgress />;
  
  if (error) {
    return (
      <Card>
        <CardContent>
          <Typography color="error">
            Error loading portfolio data: {error instanceof Error ? error.message : 'Unknown error'}
          </Typography>
        </CardContent>
      </Card>
    );
  }
  
  if (!portfolioData) {
    return (
      <Card>
        <CardContent>
          <Typography>
            No portfolio data available
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} sm={6} md={3}>
        <MetricCard
          title="Total Value"
          value={formatCurrency(portfolioData.total_value)}
          change={portfolioData.total_return}
          changePercent={portfolioData.total_return_percent}
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <MetricCard
          title="Day's Change"
          value={formatCurrency(portfolioData.day_change)}
          change={portfolioData.day_change}
          changePercent={portfolioData.day_change_percent}
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <MetricCard
          title="Total Return"
          value={formatCurrency(portfolioData.total_return)}
          change={portfolioData.total_return}
          changePercent={portfolioData.total_return_percent}
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <MetricCard
          title="Cash Balance"
          value={formatCurrency(portfolioData.cash_balance)}
          change={0}
          changePercent={0}
        />
      </Grid>
    </Grid>
  );
};

export default PortfolioSummary;
