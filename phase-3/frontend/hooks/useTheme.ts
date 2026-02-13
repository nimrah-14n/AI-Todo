/*
useTheme hook for accessing theme state and methods.

Provides access to current theme mode, resolved theme, and theme setter.
*/

'use client';

import { useContext } from 'react';
import { ThemeContext } from '@/contexts/ThemeContext';

/**
 * Hook to access theme context.
 * Must be used within ThemeProvider.
 */
export function useTheme() {
  const context = useContext(ThemeContext);

  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }

  return context;
}
