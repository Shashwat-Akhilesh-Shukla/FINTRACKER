// src/utils/formatters.ts - FIXED VERSION

export const formatCurrency = (
  amount?: number | null,
  currency: string = 'INR',
  locale: string = 'en-IN'
): string => {
  if (typeof amount !== 'number' || isNaN(amount) || amount == null) {
    return '₹0.00';
  }
  
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
};

export const formatPercentage = (
  value?: number | null,
  decimalPlaces: number = 2
): string => {
  if (typeof value !== 'number' || isNaN(value) || value == null) {
    return '0.00%';
  }
  
  return `${value >= 0 ? '+' : ''}${value.toFixed(decimalPlaces)}%`;
};

export const formatNumber = (
  num?: number | null,
  options?: Intl.NumberFormatOptions
): string => {
  if (typeof num !== 'number' || isNaN(num) || num == null) {
    return '0';
  }
  
  return new Intl.NumberFormat('en-IN', options).format(num);
};

export const formatLargeNumber = (num?: number | null): string => {
  if (typeof num !== 'number' || isNaN(num) || num == null) {
    return '0';
  }
  
  if (num >= 1e12) {
    return `${(num / 1e12).toFixed(1)}T`;
  }
  if (num >= 1e9) {
    return `${(num / 1e9).toFixed(1)}B`;
  }
  if (num >= 1e6) {
    return `${(num / 1e6).toFixed(1)}M`;
  }
  if (num >= 1e3) {
    return `${(num / 1e3).toFixed(1)}K`;
  }
  return num.toFixed(0);
};

export const formatDate = (
  date?: string | Date | null,
  options?: Intl.DateTimeFormatOptions
): string => {
  if (!date) return 'N/A';
  
  try {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    if (isNaN(dateObj.getTime())) return 'Invalid Date';
    
    return dateObj.toLocaleDateString('en-US', options);
  } catch {
    return 'Invalid Date';
  }
};

export const formatDateTime = (date?: string | Date | null): string => {
  if (!date) return 'N/A';
  
  try {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    if (isNaN(dateObj.getTime())) return 'Invalid Date';
    
    return dateObj.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return 'Invalid Date';
  }
};
