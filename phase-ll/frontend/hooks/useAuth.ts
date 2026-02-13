/*
useAuth hook for accessing authentication state and methods.

[Task]: T027
[From]: specs/001-fullstack-web-app/plan.md
*/

'use client';

import { useContext } from 'react';
import { AuthContext } from '@/contexts/AuthContext';

/**
 * Hook to access authentication context.
 * Must be used within AuthProvider.
 */
export function useAuth() {
  const context = useContext(AuthContext);

  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }

  return context;
}
