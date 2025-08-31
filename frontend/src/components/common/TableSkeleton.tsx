/**
 * Table loading placeholder that:
 * - Displays animated loading state for tables
 * - Supports customizable rows and columns
 * - Provides visual feedback during data fetch
 * - Maintains consistent loading UI pattern
 */

// src/components/common/TableSkeleton.tsx
import React from 'react';
import { Skeleton, TableRow, TableCell } from '@mui/material';

interface TableSkeletonProps {
  rows?: number;
  columns?: number;
}

export const TableSkeleton: React.FC<TableSkeletonProps> = ({ 
  rows = 5, 
  columns = 6 
}) => (
  <>
    {Array.from({ length: rows }).map((_, index) => (
      <TableRow key={index}>
        {Array.from({ length: columns }).map((_, colIndex) => (
          <TableCell key={colIndex}>
            <Skeleton variant="text" />
          </TableCell>
        ))}
      </TableRow>
    ))}
  </>
);
