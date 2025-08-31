// src/pages/Portfolio/PortfolioPage.tsx
import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Fab,
  Tab,
  Tabs,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Chip
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  TrendingUp,
  TrendingDown
} from '@mui/icons-material';
import { Formik, Form } from 'formik';
import { useDispatch, useSelector } from 'react-redux';
import { FormField } from '../../components/common/FormField';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { ErrorAlert } from '../../components/common/ErrorAlert';
import { TableSkeleton } from '../../components/common/TableSkeleton';
import {
  fetchPortfolioHoldings,
  addHolding,
  fetchPortfolioSummary
} from '../../store/slices/portfolioSlice';
import { addHoldingSchema } from '../../utils/validators';
import { formatCurrency, formatPercentage } from '../../utils/formatters';
import { RootState, AppDispatch } from '../../store/store';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <div hidden={value !== index}>
    {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
  </div>
);

const AddHoldingDialog: React.FC<{
  open: boolean;
  onClose: () => void;
}> = ({ open, onClose }) => {
  const dispatch = useDispatch<AppDispatch>();
  const { isLoading } = useSelector((state: RootState) => state.portfolio);

  const handleSubmit = async (values: { symbol: string; shares: number; price: number }) => {
    const result = await dispatch(addHolding(values));
    if (addHolding.fulfilled.match(result)) {
      onClose();
      dispatch(fetchPortfolioSummary());
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Add New Holding</DialogTitle>
      <Formik
        initialValues={{ symbol: '', shares: 0, price: 0 }}
        validationSchema={addHoldingSchema}
        onSubmit={handleSubmit}
      >
        {({ isValid, dirty }) => (
          <Form>
            <DialogContent>
              <FormField
                name="symbol"
                label="Stock Symbol"
                placeholder="e.g., AAPL"
                autoFocus
              />
              <FormField
                name="shares"
                label="Number of Shares"
                type="number"
              />
              <FormField
                name="price"
                label="Purchase Price"
                type="number"
                inputProps={{ step: 0.01 }}
              />
            </DialogContent>
            <DialogActions sx={{ p: 2 }}>
              <Button onClick={onClose}>Cancel</Button>
              <Button
                type="submit"
                variant="contained"
                disabled={!isValid || !dirty || isLoading}
              >
                {isLoading ? 'Adding...' : 'Add Holding'}
              </Button>
            </DialogActions>
          </Form>
        )}
      </Formik>
    </Dialog>
  );
};

const HoldingsTable: React.FC = () => {
  const { holdings, isLoading } = useSelector((state: RootState) => state.portfolio);

  if (isLoading) {
    return (
      <TableContainer component={Paper}>
        <Table>
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
              <TableCell align="right">Weight</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            <TableSkeleton rows={5} columns={10} />
          </TableBody>
        </Table>
      </TableContainer>
    );
  }

  return (
    <TableContainer component={Paper} elevation={2}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell sx={{ fontWeight: 600 }}>Symbol</TableCell>
            <TableCell sx={{ fontWeight: 600 }}>Name</TableCell>
            <TableCell align="right" sx={{ fontWeight: 600 }}>Shares</TableCell>
            <TableCell align="right" sx={{ fontWeight: 600 }}>Avg Cost</TableCell>
            <TableCell align="right" sx={{ fontWeight: 600 }}>Current Price</TableCell>
            <TableCell align="right" sx={{ fontWeight: 600 }}>Market Value</TableCell>
            <TableCell align="right" sx={{ fontWeight: 600 }}>Day Change</TableCell>
            <TableCell align="right" sx={{ fontWeight: 600 }}>Total Return</TableCell>
            <TableCell align="right" sx={{ fontWeight: 600 }}>Weight</TableCell>
            <TableCell align="right" sx={{ fontWeight: 600 }}>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {holdings.map((holding) => (
            <TableRow key={holding.id} hover>
              <TableCell>
                <Typography variant="subtitle2" fontWeight={600}>
                  {holding.symbol}
                </Typography>
              </TableCell>
              <TableCell>
                <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
                  {holding.name}
                </Typography>
              </TableCell>
              <TableCell align="right">{holding.shares}</TableCell>
              <TableCell align="right">
                {formatCurrency(holding.avgCost)}
              </TableCell>
              <TableCell align="right">
                <Box display="flex" alignItems="center" justifyContent="flex-end">
                  {formatCurrency(holding.currentPrice)}
                  {holding.dayChangePercent !== 0 && (
                    <Box ml={1}>
                      {holding.dayChangePercent > 0 ? (
                        <TrendingUp color="success" fontSize="small" />
                      ) : (
                        <TrendingDown color="error" fontSize="small" />
                      )}
                    </Box>
                  )}
                </Box>
              </TableCell>
              <TableCell align="right">
                <Typography variant="subtitle2" fontWeight={600}>
                  {formatCurrency(holding.marketValue)}
                </Typography>
              </TableCell>
              <TableCell align="right">
                <Chip
                  label={formatPercentage(holding.dayChangePercent)}
                  color={holding.dayChangePercent >= 0 ? 'success' : 'error'}
                  size="small"
                />
              </TableCell>
              <TableCell align="right">
                <Chip
                  label={formatPercentage(holding.totalReturnPercent)}
                  color={holding.totalReturnPercent >= 0 ? 'success' : 'error'}
                  size="small"
                />
              </TableCell>
              <TableCell align="right">
                {holding.weight.toFixed(1)}%
              </TableCell>
              <TableCell align="right">
                <IconButton size="small" sx={{ mr: 1 }}>
                  <Edit fontSize="small" />
                </IconButton>
                <IconButton size="small" color="error">
                  <Delete fontSize="small" />
                </IconButton>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

const TransactionsTable: React.FC = () => {
  const { transactions, isLoading } = useSelector((state: RootState) => state.portfolio);
  const dispatch = useDispatch<AppDispatch>();
  useEffect(() => {
    dispatch(fetchTransactions());
  }, [dispatch]);

  if (isLoading) return <TableSkeleton />;
  return (
    <TableContainer component={Paper} elevation={2}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell sx={{ fontWeight: 600 }}>Date</TableCell>
            <TableCell sx={{ fontWeight: 600 }}>Type</TableCell>
            <TableCell sx={{ fontWeight: 600 }}>Symbol</TableCell>
            <TableCell align="right" sx={{ fontWeight: 600 }}>Shares</TableCell>
            <TableCell align="right" sx={{ fontWeight: 600 }}>Price</TableCell>
            <TableCell align="right" sx={{ fontWeight: 600 }}>Total Amount</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {transactions.map((transaction) => (
            <TableRow key={transaction.id} hover>
              <TableCell>
                {new Date(transaction.date).toLocaleDateString()}
              </TableCell>
              <TableCell>
                <Chip
                  label={transaction.type}
                  color={transaction.type === 'BUY' ? 'success' : 'error'}
                  size="small"
                />
              </TableCell>
              <TableCell>
                <Typography variant="subtitle2" fontWeight={600}>
                  {transaction.symbol}
                </Typography>
              </TableCell>
              <TableCell align="right">{transaction.shares}</TableCell>
              <TableCell align="right">
                {formatCurrency(transaction.price)}
              </TableCell>
              <TableCell align="right">
                <Typography variant="subtitle2" fontWeight={600}>
                  {formatCurrency(transaction.amount)}
                </Typography>
              </TableCell>
              <TableCell align="right">
                <IconButton size="small" color="error">
                  <Delete fontSize="small" />
                </IconButton>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

const PortfolioPage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const dispatch = useDispatch<AppDispatch>();
  const { summary, isLoading, error } = useSelector((state: RootState) => state.portfolio);

  useEffect(() => {
    // Add interval for real-time updates
    const interval = setInterval(() => {
      dispatch(fetchPortfolioSummary());
      dispatch(fetchPortfolioHoldings());
    }, APP_CONFIG.REFRESH_INTERVALS.PORTFOLIO);

    return () => clearInterval(interval);
  }, [dispatch]);

  if (error) return <ErrorAlert error={error} />;

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            My Portfolio
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Manage your investments and track performance
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setAddDialogOpen(true)}
          sx={{ borderRadius: 2 }}
        >
          Add Investment
        </Button>
      </Box>

      {/* Portfolio Summary Cards */}
      {summary && (
        <Grid container spacing={3} mb={4}>
          <Grid item xs={12} sm={6} md={3}>
            <Card elevation={2}>
              <CardContent>
                <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                  Total Value
                </Typography>
                <Typography variant="h4" fontWeight={700}>
                  {formatCurrency(summary.totalValue)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card elevation={2}>
              <CardContent>
                <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                  Total Return
                </Typography>
                <Typography variant="h4" fontWeight={700}>
                  {formatCurrency(summary.totalReturn)}
                </Typography>
                <Chip
                  label={formatPercentage(summary.totalReturnPercent)}
                  color={summary.totalReturn >= 0 ? 'success' : 'error'}
                  size="small"
                  sx={{ mt: 1 }}
                />
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card elevation={2}>
              <CardContent>
                <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                  Day Change
                </Typography>
                <Typography variant="h4" fontWeight={700}>
                  {formatCurrency(summary.dayChange)}
                </Typography>
                <Chip
                  label={formatPercentage(summary.dayChangePercent)}
                  color={summary.dayChange >= 0 ? 'success' : 'error'}
                  size="small"
                  sx={{ mt: 1 }}
                />
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card elevation={2}>
              <CardContent>
                <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                  Cash Balance
                </Typography>
                <Typography variant="h4" fontWeight={700}>
                  {formatCurrency(summary.cashBalance)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Tabs */}
      <Card elevation={2}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs
            value={tabValue}
            onChange={(_, newValue) => setTabValue(newValue)}
            sx={{ px: 3 }}
          >
            <Tab label="Holdings" />
            <Tab label="Transactions" />
            <Tab label="Performance" />
          </Tabs>
        </Box>

        <TabPanel value={tabValue} index={0}>
          <HoldingsTable />
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <TransactionsTable />
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <Typography variant="h6">Performance analysis coming soon...</Typography>
        </TabPanel>
      </Card>

      {/* Floating Add Button */}
      <Fab
        color="primary"
        aria-label="add"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        onClick={() => setAddDialogOpen(true)}
      >
        <Add />
      </Fab>

      {/* Add Holding Dialog */}
      <AddHoldingDialog
        open={addDialogOpen}
        onClose={() => setAddDialogOpen(false)}
      />
    </Container>
  );
};

export default PortfolioPage;
