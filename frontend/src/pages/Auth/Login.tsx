// src/pages/Auth/Login.tsx
import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Link,
  Grid,
  Paper,
  Alert
} from '@mui/material';
import { Formik, Form } from 'formik';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { FormField } from '../../components/common/FormField';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { loginAsync } from '../../store/slices/authSlice';
import { loginSchema } from '../../utils/validators';
import { RootState, AppDispatch } from '../../store/store';
import { ROUTES } from '../../constants/routes';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch<AppDispatch>();
  const { isLoading, error } = useSelector((state: RootState) => state.auth);

  const handleSubmit = async (values: { email: string; password: string }) => {
    const result = await dispatch(loginAsync(values));
    if (loginAsync.fulfilled.match(result)) {
      navigate(ROUTES.DASHBOARD);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        p: 2
      }}
    >
      <Card elevation={10} sx={{ maxWidth: 400, width: '100%', borderRadius: 3 }}>
        <CardContent sx={{ p: 4 }}>
          <Box textAlign="center" mb={3}>
            <Typography variant="h4" fontWeight={700} color="primary" gutterBottom>
              FinTracker Pro
            </Typography>
            <Typography variant="body1" color="textSecondary">
              Welcome back! Please sign in to your account.
            </Typography>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Formik
            initialValues={{ email: '', password: '' }}
            validationSchema={loginSchema}
            onSubmit={handleSubmit}
          >
            {({ isValid, dirty }) => (
              <Form>
                <FormField
                  name="email"
                  label="Email Address"
                  type="email"
                  autoComplete="email"
                  autoFocus
                />
                <FormField
                  name="password"
                  label="Password"
                  type="password"
                  autoComplete="current-password"
                />
                
                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  size="large"
                  disabled={!isValid || !dirty || isLoading}
                  sx={{ mt: 3, mb: 2, py: 1.5 }}
                >
                  {isLoading ? <LoadingSpinner size={24} message="" /> : 'Sign In'}
                </Button>

                <Grid container justifyContent="center">
                  <Grid item>
                    <Link
                      component={RouterLink}
                      to={ROUTES.REGISTER}
                      variant="body2"
                      underline="hover"
                    >
                      Don't have an account? Sign up
                    </Link>
                  </Grid>
                </Grid>
              </Form>
            )}
          </Formik>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Login;
