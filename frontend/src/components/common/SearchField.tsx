/**
 * Search input component that:
 * - Provides styled search field with icon
 * - Handles search input changes
 * - Supports custom placeholder text
 * - Maintains consistent search UI across app
 */

// src/components/common/SearchField.tsx
import React from 'react';
import { TextField, InputAdornment } from '@mui/material';
import { Search } from '@mui/icons-material';

interface SearchFieldProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

export const SearchField: React.FC<SearchFieldProps> = ({
  value,
  onChange,
  placeholder = 'Search...'
}) => (
  <TextField
    fullWidth
    size="small"
    placeholder={placeholder}
    value={value}
    onChange={(e) => onChange(e.target.value)}
    InputProps={{
      startAdornment: (
        <InputAdornment position="start">
          <Search />
        </InputAdornment>
      ),
    }}
  />
);
