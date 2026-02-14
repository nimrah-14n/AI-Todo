/*
Better Auth configuration with JWT secret.

[Task]: T025
[From]: specs/001-fullstack-web-app/plan.md
*/

// Note: Better Auth is configured on the backend with JWT tokens.
// Frontend uses the JWT token from API responses for authentication.

export const AUTH_CONFIG = {
  apiUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  tokenKey: 'auth_token',
  userKey: 'auth_user',
};

/**
 * Store authentication token in localStorage
 */
export function setAuthToken(token: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(AUTH_CONFIG.tokenKey, token);
  }
}

/**
 * Get authentication token from localStorage
 */
export function getAuthToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem(AUTH_CONFIG.tokenKey);
  }
  return null;
}

/**
 * Remove authentication token from localStorage
 */
export function removeAuthToken(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(AUTH_CONFIG.tokenKey);
    localStorage.removeItem(AUTH_CONFIG.userKey);
  }
}

/**
 * Store user information in localStorage
 */
export function setAuthUser(user: any): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(AUTH_CONFIG.userKey, JSON.stringify(user));
  }
}

/**
 * Get user information from localStorage
 */
export function getAuthUser(): any | null {
  if (typeof window !== 'undefined') {
    const userStr = localStorage.getItem(AUTH_CONFIG.userKey);
    return userStr ? JSON.parse(userStr) : null;
  }
  return null;
}
