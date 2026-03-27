import { errorLogger } from './errorLogger';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const TOKEN_KEY = 'auth_token';

export function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(TOKEN_KEY, token);
}

export function removeToken(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(TOKEN_KEY);
}

interface FetchOptions extends RequestInit {
  requiresAuth?: boolean;
}

export async function apiClient<T>(
  endpoint: string,
  options: FetchOptions = {}
): Promise<T> {
  const { requiresAuth = true, headers = {}, ...restOptions } = options;

  const config: RequestInit = {
    ...restOptions,
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
  };

  if (requiresAuth) {
    const token = getToken();
    if (token) {
      config.headers = {
        ...config.headers,
        Authorization: `Bearer ${token}`,
      };
    }
  }

  const url = `${API_BASE_URL}${endpoint}`;
  
  try {
    const response = await fetch(url, config);

    if (response.status === 401) {
      removeToken();
      if (typeof window !== 'undefined') {
        window.location.href = '/';
      }
      const error = new Error('Unauthorized');
      errorLogger.logApiError(endpoint, config.method || 'GET', 401, error);
      throw error;
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
      
      // Handle error detail that might be a string or object
      let errorMessage: string;
      if (typeof error.detail === 'string') {
        errorMessage = error.detail;
      } else if (typeof error.detail === 'object' && error.detail !== null) {
        // If detail is an object (e.g., validation errors), stringify it
        errorMessage = JSON.stringify(error.detail);
      } else {
        errorMessage = `HTTP ${response.status}`;
      }
      
      // Provide more specific error messages based on status code
      let specificError: Error;
      if (response.status === 400) {
        specificError = new Error(`Bad Request: ${errorMessage}`);
      } else if (response.status === 403) {
        specificError = new Error(`Forbidden: ${errorMessage}`);
      } else if (response.status === 404) {
        specificError = new Error(`Not Found: ${errorMessage}`);
      } else if (response.status === 409) {
        specificError = new Error(`Conflict: ${errorMessage}`);
      } else if (response.status === 422) {
        specificError = new Error(`Validation Error: ${errorMessage}`);
      } else if (response.status === 429) {
        specificError = new Error(`Rate Limit Exceeded: ${errorMessage}`);
      } else if (response.status >= 500) {
        specificError = new Error(`Server Error: ${errorMessage}`);
      } else {
        specificError = new Error(errorMessage);
      }
      
      errorLogger.logApiError(endpoint, config.method || 'GET', response.status, specificError, options.body);
      throw specificError;
    }

    return response.json();
  } catch (error) {
    // Log network errors
    if (error instanceof TypeError && error.message.includes('fetch')) {
      const networkError = new Error('Network error: Unable to connect to server');
      errorLogger.logApiError(endpoint, config.method || 'GET', 0, networkError);
      throw networkError;
    }
    throw error;
  }
}
