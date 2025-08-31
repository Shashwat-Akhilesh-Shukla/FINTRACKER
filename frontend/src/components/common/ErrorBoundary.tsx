import React from 'react';
import { Alert, Button, Box, Typography } from '@mui/material';

export class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error: Error | null }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return (
        <Box p={3}>
          <Alert severity="error">
            <Typography variant="h6">Something went wrong</Typography>
            <Typography variant="body2">{this.state.error?.message}</Typography>
            <Button
              onClick={() => window.location.reload()}
              variant="contained"
              color="primary"
              sx={{ mt: 2 }}
            >
              Refresh Page
            </Button>
          </Alert>
        </Box>
      );
    }

    return this.props.children;
  }
}