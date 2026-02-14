/*
API client utility for making authenticated requests to backend.

[Task]: T012
[From]: specs/001-fullstack-web-app/plan.md
*/

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface RequestOptions extends RequestInit {
  token?: string;
}

/**
 * Make an authenticated API request
 */
export async function apiRequest<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { token, ...fetchOptions } = options;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(fetchOptions.headers as Record<string, string>),
  };

  // Add Authorization header if token provided
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const url = `${API_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    ...fetchOptions,
    headers,
  });

  // Handle 204 No Content responses (e.g., DELETE operations)
  if (response.status === 204) {
    return {} as T;
  }

  // Handle non-JSON responses
  const contentType = response.headers.get('content-type');
  if (!contentType || !contentType.includes('application/json')) {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return {} as T;
  }

  const data = await response.json();

  if (!response.ok) {
    // FastAPI returns errors in 'detail' field
    throw new Error(data.detail || data.error || data.message || `HTTP error! status: ${response.status}`);
  }

  return data;
}

/**
 * GET request
 */
export async function apiGet<T>(endpoint: string, token?: string): Promise<T> {
  return apiRequest<T>(endpoint, { method: 'GET', token });
}

/**
 * POST request
 */
export async function apiPost<T>(
  endpoint: string,
  body: any,
  token?: string
): Promise<T> {
  return apiRequest<T>(endpoint, {
    method: 'POST',
    body: JSON.stringify(body),
    token,
  });
}

/**
 * PUT request
 */
export async function apiPut<T>(
  endpoint: string,
  body: any,
  token?: string
): Promise<T> {
  return apiRequest<T>(endpoint, {
    method: 'PUT',
    body: JSON.stringify(body),
    token,
  });
}

/**
 * PATCH request
 */
export async function apiPatch<T>(
  endpoint: string,
  body: any,
  token?: string
): Promise<T> {
  return apiRequest<T>(endpoint, {
    method: 'PATCH',
    body: JSON.stringify(body),
    token,
  });
}

/**
 * DELETE request
 */
export async function apiDelete<T>(
  endpoint: string,
  token?: string
): Promise<T> {
  return apiRequest<T>(endpoint, { method: 'DELETE', token });
}
