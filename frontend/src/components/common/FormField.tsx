/**
 * Reusable form field component that:
 * - Integrates Material-UI TextField with Formik
 * - Handles form validation states and errors
 * - Provides consistent styling and layout
 * - Simplifies form field implementation across app
 */

// src/components/common/FormField.tsx
import React from 'react';
import { TextField, TextFieldProps } from '@mui/material';
import { useField } from 'formik';

type FormFieldProps = {
  name: string;
} & Omit<TextFieldProps, 'name' | 'value' | 'onChange'>;

export const FormField: React.FC<FormFieldProps> = ({ name, ...props }) => {
  const [field, meta] = useField(name);
  
  return (
    <TextField
      {...field}
      {...props}
      error={meta.touched && Boolean(meta.error)}
      helperText={meta.touched && meta.error}
      fullWidth
      margin="normal"
    />
  );
};
