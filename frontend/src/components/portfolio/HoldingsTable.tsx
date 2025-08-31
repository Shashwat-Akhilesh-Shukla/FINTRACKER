// src/components/portfolio/HoldingsTable.tsx
import React, { useEffect } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../../store/store';
import { fetchPortfolioHoldings } from '../../store/slices/portfolioSlice';
import { formatCurrency, formatPercentage } from '../../utils/formatters';
import { TableSkeleton } from '../common/TableSkeleton';

const HoldingsTable: React.FC = () => {
  const { holdings, isLoading } = useSelector((state: RootState) => state.portfolio);

  if (isLoading) {
    return <TableSkeleton rows={5} columns={8} />;
  }

  return (
    <TableContainer
      component={Paper}
      elevation={2}
      sx={{
        maxHeight: 500, // adjust height as needed
        overflowY: 'auto'
      }}
      >
      <Table stickyHeader>
        <TableHead>
          <TableRow>
            <TableCell>Symbol</TableCell>
            <TableCell>Name</TableCell>
            <TableCell align="right">Shares</TableCell>
            <TableCell align="right">Avg Cost</TableCell>
            <TableCell align="right">Current Price</TableCell>
            <TableCell align="right">Market Value</TableCell>
            <TableCell align="right">Day Change</TableCell>
            <TableCell align="right">Total Return</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {holdings.map((holding) => (
            <TableRow key={holding.symbol} hover>
              <TableCell>{holding.symbol}</TableCell>
              <TableCell>{holding.name}</TableCell>
              <TableCell align="right">{holding.shares}</TableCell>
              <TableCell align="right">{formatCurrency(holding.avgCost)}</TableCell>
              <TableCell align="right">{formatCurrency(holding.currentPrice)}</TableCell>
              <TableCell align="right">{formatCurrency(holding.marketValue)}</TableCell>
              <TableCell
                align="right"
                sx={{ color: holding.dayChange >= 0 ? 'success.main' : 'error.main' }}
              >
                {formatCurrency(holding.dayChange)} ({formatPercentage(holding.dayChangePercent)})
              </TableCell>
              <TableCell
                align="right"
                sx={{ color: holding.totalReturn >= 0 ? 'success.main' : 'error.main' }}
              >
                {formatCurrency(holding.totalReturn)} ({formatPercentage(holding.totalReturnPercent)})
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>

  );
};

export default HoldingsTable;
