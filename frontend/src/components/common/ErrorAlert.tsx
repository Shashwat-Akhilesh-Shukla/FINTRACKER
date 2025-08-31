// src/components/common/ErrorAlert.tsx
import React from 'react';
import { Alert, AlertTitle, Box } from '@mui/material';

interface ErrorAlertProps {
  error: Error | string;
  onRetry?: () => void;
}

export const ErrorAlert: React.FC<ErrorAlertProps> = ({ error, onRetry }) => {
  const errorMessage = typeof error === 'string' ? error : error.message;

  return (
    <Box sx={{ mb: 2 }}>
      <Alert severity="error" action={onRetry && (
        <button onClick={onRetry}>Retry</button>
      )}>
        <AlertTitle>Error</AlertTitle>
        {errorMessage}
      </Alert>
    </Box>
  );
};
