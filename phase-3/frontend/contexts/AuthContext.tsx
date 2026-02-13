/*
Authentication context provider for managing user state.

[Task]: T026
[From]: specs/001-fullstack-web-app/plan.md
*/

'use client';

import React, { createContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { apiPost } from '@/lib/api-client';
import {
  setAuthToken,
  getAuthToken,
  removeAuthToken,
  setAuthUser,
  getAuthUser,
} from '@/lib/auth';

interface User {
  id: string;
  email: string;
  created_at: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  signup: (email: string, password: string) => Promise<void>;
  signin: (email: string, password: string) => Promise<void>;
  signout: () => void;
  isAuthenticated: boolean;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  // Load user from localStorage on mount
  useEffect(() => {
    const storedToken = getAuthToken();
    const storedUser = getAuthUser();

    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(storedUser);
    }

    setLoading(false);
  }, []);

  const signup = async (email: string, password: string) => {
    try {
      const response = await apiPost<{ token: string; user: User }>(
        '/api/auth/signup',
        { email, password }
      );

      setAuthToken(response.token);
      setAuthUser(response.user);
      setToken(response.token);
      setUser(response.user);

      router.push('/dashboard');
    } catch (error) {
      throw error;
    }
  };

  const signin = async (email: string, password: string) => {
    try {
      const response = await apiPost<{ token: string; user: User }>(
        '/api/auth/signin',
        { email, password }
      );

      setAuthToken(response.token);
      setAuthUser(response.user);
      setToken(response.token);
      setUser(response.user);

      router.push('/dashboard');
    } catch (error) {
      throw error;
    }
  };

  const signout = () => {
    removeAuthToken();
    setToken(null);
    setUser(null);
    router.push('/');
  };

  const value: AuthContextType = {
    user,
    token,
    loading,
    signup,
    signin,
    signout,
    isAuthenticated: !!token && !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
