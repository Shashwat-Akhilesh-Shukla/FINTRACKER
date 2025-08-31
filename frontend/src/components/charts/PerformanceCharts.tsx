// src/components/charts/PerformanceCharts.tsx
import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  ToggleButton,
  ToggleButtonGroup,
  Box,
  Grid,
  CircularProgress,
  Alert,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { usePortfolioHistory } from '../../hooks/usePortfolioHistory';
import { portfolioService } from '../../services/portfolioService';
import { APP_CONFIG } from '../../constants/config';
import { useQuery } from 'react-query';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82ca9d', '#ffc658', '#8884d8', '#ff7300', '#413ea0'];

const PerformanceCharts: React.FC = () => {
  const [timeframe, setTimeframe] = useState('1M');
  const [showIndustry, setShowIndustry] = useState(false);
  const { historyData, loading: historyLoading, error: historyError } = usePortfolioHistory(timeframe);

  // Fetch holdings data
  const { data: holdings, isLoading: holdingsLoading, error: holdingsError } = useQuery(
    'holdings',
    portfolioService.getHoldings
  );

  const handleTimeframeChange = (_: React.MouseEvent<HTMLElement>, newTimeframe: string | null) => {
    if (newTimeframe) {
      setTimeframe(newTimeframe);
    }
  };

  const calculateAllocationData = () => {
    if (!holdings) return [];

    const allocationMap = new Map<string, number>();

    holdings.forEach(holding => {
      const category = showIndustry ? holding.industry : holding.sector;
      if (category) {
        const currentValue = allocationMap.get(category) || 0;
        allocationMap.set(category, currentValue + holding.marketValue);
      }
    });

    return Array.from(allocationMap.entries())
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value);
  };

  const renderPerformanceChart = () => {
    if (historyLoading) {
      return (
        <Box display="flex" justifyContent="center" alignItems="center" height={400}>
          <CircularProgress />
        </Box>
      );
    }

    if (historyError) {
      return (
        <Box display="flex" justifyContent="center" alignItems="center" height={400}>
          <Alert severity="error">{historyError}</Alert>
        </Box>
      );
    }

    return (
      <ResponsiveContainer width="100%" height={400}>
        <AreaChart data={historyData}>
          <defs>
            <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#8884d8" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12 }}
            tickFormatter={(value) => new Date(value).toLocaleDateString()}
          />
          <YAxis
            tick={{ fontSize: 12 }}
            tickFormatter={(value) => `₹${value.toLocaleString()}`}
          />
          <CartesianGrid strokeDasharray="3 3" />
          <Tooltip
            formatter={(value: number) => [`₹${value.toLocaleString()}`, 'Portfolio Value']}
            labelFormatter={(label) => new Date(label).toLocaleDateString()}
          />
          <Area
            type="monotone"
            dataKey="value"
            stroke="#8884d8"
            fillOpacity={1}
            fill="url(#colorValue)"
          />
        </AreaChart>
      </ResponsiveContainer>
    );
  };

  const renderAllocationChart = () => {
    if (holdingsLoading) {
      return (
        <Box display="flex" justifyContent="center" alignItems="center" height={400}>
          <CircularProgress />
        </Box>
      );
    }

    if (holdingsError) {
      return (
        <Box display="flex" justifyContent="center" alignItems="center" height={400}>
          <Alert severity="error">Error loading allocation data</Alert>
        </Box>
      );
    }

    const allocationData = calculateAllocationData();

    return (
      <ResponsiveContainer width="100%" height={400}>
        <PieChart>
          <Pie
            data={allocationData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
            outerRadius={120}
            fill="#8884d8"
            dataKey="value"
          >
            {allocationData.map((_, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value: number) => [`₹${value.toLocaleString()}`, 'Value']}
          />
        </PieChart>
      </ResponsiveContainer>
    );
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Card elevation={2}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Typography variant="h6" fontWeight={600}>
                Portfolio Performance
              </Typography>
              <ToggleButtonGroup
                value={timeframe}
                exclusive
                onChange={handleTimeframeChange}
                size="small"
              >
                {APP_CONFIG.CHART_TIMEFRAMES.map((tf) => (
                  <ToggleButton key={tf} value={tf}>
                    {tf}
                  </ToggleButton>
                ))}
              </ToggleButtonGroup>
            </Box>
            {renderPerformanceChart()}
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12}>
        <Card elevation={2}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" fontWeight={600}>
                {showIndustry ? 'Industry' : 'Sector'} Allocation
              </Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={showIndustry}
                    onChange={(e) => setShowIndustry(e.target.checked)}
                  />
                }
                label={showIndustry ? "Show Sectors" : "Show Industries"}
              />
            </Box>
            {renderAllocationChart()}
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export default PerformanceCharts;
