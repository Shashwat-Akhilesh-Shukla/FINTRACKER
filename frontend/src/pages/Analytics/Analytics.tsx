// src/pages/Analytics/Analytics.tsx
import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  ToggleButton,
  ToggleButtonGroup,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  LinearProgress,
  Divider
} from '@mui/material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  ScatterChart,
  Scatter
} from 'recharts';
import { useDispatch, useSelector } from 'react-redux';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { ErrorAlert } from '../../components/common/ErrorAlert';
import { fetchPortfolioMetrics } from '../../store/slices/portfolioSlice';
import { RootState, AppDispatch } from '../../store/store';
import { SECTOR_COLORS } from '../../constants/colors';
import { formatCurrency, formatPercentage } from '../../utils/formatters';

const RiskMetricsCard: React.FC = () => {
  const { metrics } = useSelector((state: RootState) => state.portfolio);

  if (!metrics) return <LoadingSpinner />;

  const riskMetrics = [
    { label: 'Sharpe Ratio', value: metrics.sharpeRatio.toFixed(2), description: 'Risk-adjusted return' },
    { label: 'Beta', value: metrics.beta.toFixed(2), description: 'Market sensitivity' },
    { label: 'Alpha', value: `${metrics.alpha.toFixed(2)}%`, description: 'Excess return' },
    { label: 'Max Drawdown', value: `${metrics.maxDrawdown.toFixed(2)}%`, description: 'Largest peak-to-trough decline' },
    { label: 'Volatility', value: `${metrics.volatility.toFixed(2)}%`, description: 'Price fluctuation measure' },
    { label: 'VaR (95%)', value: formatCurrency(metrics.var95), description: 'Value at Risk' },
  ];

  return (
    <Card elevation={2}>
      <CardContent>
        <Typography variant="h6" fontWeight={600} gutterBottom>
          Risk Metrics
        </Typography>
        <Divider sx={{ mb: 2 }} />
        <Grid container spacing={3}>
          {riskMetrics.map((metric, index) => (
            <Grid item xs={12} sm={6} key={index}>
              <Box>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2" color="textSecondary">
                    {metric.label}
                  </Typography>
                  <Typography variant="subtitle2" fontWeight={600}>
                    {metric.value}
                  </Typography>
                </Box>
                <Typography variant="caption" color="textSecondary">
                  {metric.description}
                </Typography>
              </Box>
            </Grid>
          ))}
        </Grid>
      </CardContent>
    </Card>
  );
};

const PerformanceMetricsCard: React.FC = () => {
  const performanceData = [
    { period: '1M', return: 2.5, benchmark: 1.8 },
    { period: '3M', return: 7.2, benchmark: 5.4 },
    { period: '6M', return: 12.8, benchmark: 9.6 },
    { period: '1Y', return: 18.5, benchmark: 15.2 },
    { period: '2Y', return: 34.7, benchmark: 28.9 },
  ];

  return (
    <Card elevation={2}>
      <CardContent>
        <Typography variant="h6" fontWeight={600} gutterBottom>
          Performance vs Benchmark
        </Typography>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={performanceData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="period" />
            <YAxis />
            <Tooltip formatter={(value: number) => `${value}%`} />
            <Bar dataKey="return" fill="#1e3c72" name="Portfolio" />
            <Bar dataKey="benchmark" fill="#2a5298" name="S&P 500" />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

const SectorAnalysisCard: React.FC = () => {
  const { sectorAllocation } = useSelector((state: RootState) => state.portfolio);

  const mockSectorData = [
    { sector: 'Technology', value: 45000, percentage: 35, count: 8 },
    { sector: 'Healthcare', value: 25000, percentage: 20, count: 5 },
    { sector: 'Finance', value: 20000, percentage: 16, count: 4 },
    { sector: 'Consumer', value: 15000, percentage: 12, count: 3 },
    { sector: 'Energy', value: 12000, percentage: 9, count: 2 },
    { sector: 'Industrials', value: 10000, percentage: 8, count: 2 },
  ];

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card elevation={2}>
          <CardContent>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Sector Allocation
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={mockSectorData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ sector, percentage }) => `${sector} ${percentage}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {mockSectorData.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={Object.values(SECTOR_COLORS)[index] || '#8884d8'} 
                    />
                  ))}
                </Pie>
                <Tooltip formatter={(value: number) => formatCurrency(value)} />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <Card elevation={2}>
          <CardContent>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Sector Breakdown
            </Typography>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Sector</TableCell>
                    <TableCell align="right">Value</TableCell>
                    <TableCell align="right">Weight</TableCell>
                    <TableCell align="right">Holdings</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {mockSectorData.map((sector) => (
                    <TableRow key={sector.sector}>
                      <TableCell>{sector.sector}</TableCell>
                      <TableCell align="right">
                        {formatCurrency(sector.value)}
                      </TableCell>
                      <TableCell align="right">
                        <Box display="flex" alignItems="center">
                          <LinearProgress
                            variant="determinate"
                            value={sector.percentage}
                            sx={{ width: 50, mr: 1 }}
                          />
                          {sector.percentage}%
                        </Box>
                      </TableCell>
                      <TableCell align="right">{sector.count}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

const CorrelationAnalysis: React.FC = () => {
  const correlationData = [
    { asset1: 'AAPL', asset2: 'MSFT', correlation: 0.85, risk: 'High' },
    { asset1: 'GOOGL', asset2: 'AMZN', correlation: 0.78, risk: 'High' },
    { asset1: 'TSLA', asset2: 'F', correlation: 0.45, risk: 'Medium' },
    { asset1: 'JPM', asset2: 'BAC', correlation: 0.92, risk: 'High' },
    { asset1: 'JNJ', asset2: 'PFE', correlation: 0.65, risk: 'Medium' },
  ];

  return (
    <Card elevation={2}>
      <CardContent>
        <Typography variant="h6" fontWeight={600} gutterBottom>
          Asset Correlation Analysis
        </Typography>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Asset Pair</TableCell>
                <TableCell align="right">Correlation</TableCell>
                <TableCell align="right">Risk Level</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {correlationData.map((row, index) => (
                <TableRow key={index}>
                  <TableCell>
                    <Typography variant="body2">
                      {row.asset1} - {row.asset2}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="subtitle2" fontWeight={600}>
                      {row.correlation.toFixed(2)}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Chip
                      label={row.risk}
                      color={
                        row.risk === 'High' ? 'error' : 
                        row.risk === 'Medium' ? 'warning' : 'success'
                      }
                      size="small"
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );
};

const Analytics: React.FC = () => {
  const [timeframe, setTimeframe] = useState('1Y');
  const dispatch = useDispatch<AppDispatch>();
  const { metrics, isLoading, error } = useSelector((state: RootState) => state.portfolio);

  useEffect(() => {
    dispatch(fetchPortfolioMetrics());
  }, [dispatch]);

  if (isLoading) return <LoadingSpinner message="Loading analytics..." />;
  if (error) return <ErrorAlert error={error} />;

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      {/* Header */}
      <Box mb={4}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Box>
            <Typography variant="h4" fontWeight={700} gutterBottom>
              Portfolio Analytics
            </Typography>
            <Typography variant="body1" color="textSecondary">
              Advanced analysis and risk metrics for your portfolio
            </Typography>
          </Box>
          <ToggleButtonGroup
            value={timeframe}
            exclusive
            onChange={(_, value) => value && setTimeframe(value)}
            size="small"
          >
            <ToggleButton value="1M">1M</ToggleButton>
            <ToggleButton value="3M">3M</ToggleButton>
            <ToggleButton value="6M">6M</ToggleButton>
            <ToggleButton value="1Y">1Y</ToggleButton>
            <ToggleButton value="2Y">2Y</ToggleButton>
          </ToggleButtonGroup>
        </Box>
      </Box>

      {/* Analytics Content */}
      <Grid container spacing={3}>
        {/* Risk Metrics */}
        <Grid item xs={12} lg={6}>
          <RiskMetricsCard />
        </Grid>

        {/* Performance vs Benchmark */}
        <Grid item xs={12} lg={6}>
          <PerformanceMetricsCard />
        </Grid>

        {/* Sector Analysis */}
        <Grid item xs={12}>
          <SectorAnalysisCard />
        </Grid>

        {/* Correlation Analysis */}
        <Grid item xs={12}>
          <CorrelationAnalysis />
        </Grid>
      </Grid>
    </Container>
  );
};

export default Analytics;
