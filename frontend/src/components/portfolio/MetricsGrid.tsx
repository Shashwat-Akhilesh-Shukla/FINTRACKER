// src/components/portfolio/MetricsGrid.tsx
import React from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import { usePortfolioMetrics } from '../../hooks/usePortfolioMetrics';

const MetricsGrid: React.FC = () => {
  const { metrics, holdings } = usePortfolioMetrics();

  return (
    <Grid container spacing={3}>
      {/* Risk Metrics */}
      <Grid item xs={12} md={4}>
        <Card elevation={2}>
          <CardContent>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Risk Metrics
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="textSecondary">
                Sharpe Ratio
              </Typography>
              <Typography variant="h5" fontWeight={500}>
                {metrics.sharpeRatio.toFixed(2)}
              </Typography>
            </Box>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="textSecondary">
                Beta
              </Typography>
              <Typography variant="h5" fontWeight={500}>
                {metrics.beta.toFixed(2)}
              </Typography>
            </Box>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="textSecondary">
                VaR (95%)
              </Typography>
              <Typography variant="h5" fontWeight={500}>
                ${metrics.var.toLocaleString()}
              </Typography>
            </Box>
            <Box>
              <Typography variant="body2" color="textSecondary">
                Max Drawdown
              </Typography>
              <Typography variant="h5" fontWeight={500} color="error.main">
                {metrics.maxDrawdown.toFixed(2)}%
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Performance Metrics */}
      <Grid item xs={12} md={4}>
        <Card elevation={2}>
          <CardContent>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Performance
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="textSecondary">
                Annualized Return
              </Typography>
              <Typography variant="h5" fontWeight={500}>
                {metrics.annualizedReturn.toFixed(2)}%
              </Typography>
            </Box>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="textSecondary">
                Volatility
              </Typography>
              <Typography variant="h5" fontWeight={500}>
                {metrics.volatility.toFixed(2)}%
              </Typography>
            </Box>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="textSecondary">
                Alpha
              </Typography>
              <Typography variant="h5" fontWeight={500}>
                {metrics.alpha.toFixed(2)}%
              </Typography>
            </Box>
            <Box>
              <Typography variant="body2" color="textSecondary">
                Information Ratio
              </Typography>
              <Typography variant="h5" fontWeight={500}>
                {metrics.informationRatio.toFixed(2)}
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export default MetricsGrid;
