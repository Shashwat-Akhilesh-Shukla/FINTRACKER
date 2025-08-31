/**
 * Loading indicator component that:
 * - Displays a centered loading spinner
 * - Shows customizable loading message
 * - Provides consistent loading state UI
 * - Supports configurable spinner size
 */

// src/components/common/LoadingSpinner.tsx
import React from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';

interface LoadingSpinnerProps {
  size?: number;
  message?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 40, 
  message = 'Loading...' 
}) => (
  <Box
    display="flex"
    flexDirection="column"
    alignItems="center"
    justifyContent="center"
    minHeight="200px"
    gap={2}
  >
    <CircularProgress size={size} />
    <Typography variant="body2" color="textSecondary">
      {message}
    </Typography>
  </Box>
);
