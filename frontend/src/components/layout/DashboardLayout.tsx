// src/components/layout/DashboardLayout.tsx
import React from 'react';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  Typography,
  Grid,
  Paper,
  Container
} from '@mui/material';
import { styled } from '@mui/material/styles';
import PortfolioSummary from '../portfolio/PortfolioSummary';
import NewsPanel from '../news/NewsPanel';
import PerformanceCharts from '../charts/PerformanceCharts';
import MetricsGrid from '../portfolio/MetricsGrid';

const StyledAppBar = styled(AppBar)(({ theme }) => ({
  background: 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)',
  boxShadow: '0 4px 20px 0 rgba(0,0,0,0.12)',
}));

const DashboardLayout: React.FC = () => {
  return (
    <Box sx={{ display: 'flex' }}>
      <StyledAppBar position="fixed" sx={{ zIndex: 1300 }}>
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 600 }}>
            FinTracker Pro
          </Typography>
        </Toolbar>
      </StyledAppBar>
      
      <Container maxWidth={false} sx={{ mt: 8, p: 3 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} lg={8}>
            <PortfolioSummary />
            <Box sx={{ mt: 3 }}>
              <PerformanceCharts />
            </Box>
            <Box sx={{ mt: 3 }}>
              <MetricsGrid />
            </Box>
          </Grid>
          <Grid item xs={12} lg={4}>
            <NewsPanel />
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default DashboardLayout;
