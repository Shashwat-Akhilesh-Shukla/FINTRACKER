// src/utils/validators.ts
import * as Yup from 'yup';

export const loginSchema = Yup.object({
  email: Yup.string()
    .email('Invalid email address')
    .required('Email is required'),
  password: Yup.string()
    .min(6, 'Password must be at least 6 characters')
    .required('Password is required'),
});

export const registerSchema = Yup.object({
  firstName: Yup.string()
    .min(2, 'First name must be at least 2 characters')
    .required('First name is required'),
  lastName: Yup.string()
    .min(2, 'Last name must be at least 2 characters')
    .required('Last name is required'),
  email: Yup.string()
    .email('Invalid email address')
    .required('Email is required'),
  password: Yup.string()
    .min(8, 'Password must be at least 8 characters')
    .matches(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .matches(/[a-z]/, 'Password must contain at least one lowercase letter')
    .matches(/\d/, 'Password must contain at least one number')
    .required('Password is required'),
  confirmPassword: Yup.string()
    .oneOf([Yup.ref('password')], 'Passwords must match')
    .required('Confirm password is required'),
});

export const addHoldingSchema = Yup.object({
  symbol: Yup.string()
    .matches(/^[A-Z]{1,5}$/, 'Symbol must be 1-5 uppercase letters')
    .required('Symbol is required'),
  shares: Yup.number()
    .positive('Shares must be positive')
    .required('Shares is required'),
  price: Yup.number()
    .positive('Price must be positive')
    .required('Price is required'),
});

export const validateSymbol = (symbol: string): boolean => {
  return /^[A-Z]{1,5}$/.test(symbol);
};

export const validateEmail = (email: string): boolean => {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
};
