// src/pages/Auth/Register.tsx
import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Link,
  Grid,
  Alert
} from '@mui/material';
import { Formik, Form } from 'formik';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { FormField } from '../../components/common/FormField';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { registerAsync } from '../../store/slices/authSlice';
import { registerSchema } from '../../utils/validators';
import { RootState, AppDispatch } from '../../store/store';
import { ROUTES } from '../../constants/routes';
import { RegisterData } from '../../types/auth';

const Register: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch<AppDispatch>();
  const { isLoading, error } = useSelector((state: RootState) => state.auth);

  const handleSubmit = async (values: RegisterData & { confirmPassword: string }) => {
    const { confirmPassword, ...registerData } = values;
    const result = await dispatch(registerAsync(registerData));
    if (registerAsync.fulfilled.match(result)) {
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
      <Card elevation={10} sx={{ maxWidth: 450, width: '100%', borderRadius: 3 }}>
        <CardContent sx={{ p: 4 }}>
          <Box textAlign="center" mb={3}>
            <Typography variant="h4" fontWeight={700} color="primary" gutterBottom>
              Join FinTracker Pro
            </Typography>
            <Typography variant="body1" color="textSecondary">
              Create your account and start tracking your portfolio
            </Typography>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Formik
            initialValues={{
              firstName: '',
              lastName: '',
              email: '',
              password: '',
              confirmPassword: ''
            }}
            validationSchema={registerSchema}
            onSubmit={handleSubmit}
          >
            {({ isValid, dirty }) => (
              <Form>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <FormField
                      name="firstName"
                      label="First Name"
                      autoComplete="given-name"
                      autoFocus
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <FormField
                      name="lastName"
                      label="Last Name"
                      autoComplete="family-name"
                    />
                  </Grid>
                </Grid>
                
                <FormField
                  name="email"
                  label="Email Address"
                  type="email"
                  autoComplete="email"
                />
                <FormField
                  name="password"
                  label="Password"
                  type="password"
                  autoComplete="new-password"
                />
                <FormField
                  name="confirmPassword"
                  label="Confirm Password"
                  type="password"
                  autoComplete="new-password"
                />
                
                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  size="large"
                  disabled={!isValid || !dirty || isLoading}
                  sx={{ mt: 3, mb: 2, py: 1.5 }}
                >
                  {isLoading ? <LoadingSpinner size={24} message="" /> : 'Create Account'}
                </Button>

                <Grid container justifyContent="center">
                  <Grid item>
                    <Link
                      component={RouterLink}
                      to={ROUTES.LOGIN}
                      variant="body2"
                      underline="hover"
                    >
                      Already have an account? Sign in
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

export default Register;
