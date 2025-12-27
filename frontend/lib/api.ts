/**
 * API Client Configuration
 * Provides centralized API request handling with authentication,
 * retry logic, and error handling
 */

import { API_URL, ERROR_MESSAGES } from "./constants";

// ============================================================================
// Types & Interfaces
// ============================================================================

export interface ApiError {
  message: string;
  status: number;
  code?: string;
  details?: unknown;
  retryable: boolean;
}

export interface ApiRequestConfig extends RequestInit {
  /** Skip authentication header */
  skipAuth?: boolean;
  /** Number of retry attempts (default: 3 for GET, 0 for mutations) */
  retries?: number;
  /** Base delay in ms for exponential backoff (default: 1000) */
  retryDelay?: number;
  /** Timeout in ms (default: 30000) */
  timeout?: number;
  /** Skip automatic token refresh on 401 */
  skipRefresh?: boolean;
}

export interface ApiResponse<T> {
  data: T;
  status: number;
  headers: Headers;
}

type TokenGetter = () => string | null;
type TokenRefresher = () => Promise<{ accessToken: string; refreshToken: string } | null>;
type OnUnauthorized = () => void;
type OnForbidden = () => void;

interface ApiClientConfig {
  baseURL: string;
  defaultTimeout: number;
  defaultRetries: number;
  retryDelay: number;
  retryStatusCodes: number[];
}

// ============================================================================
// Helpers
// ============================================================================

/**
 * Check if code is running on the server (SSR)
 */
export const isServer = typeof window === "undefined";

/**
 * Sleep utility for retry delays
 */
const sleep = (ms: number): Promise<void> => new Promise((resolve) => setTimeout(resolve, ms));

/**
 * Calculate delay with exponential backoff and jitter
 */
const getRetryDelay = (attempt: number, baseDelay: number): number => {
  const exponentialDelay = baseDelay * Math.pow(2, attempt);
  const jitter = Math.random() * 0.3 * exponentialDelay; // 0-30% jitter
  return exponentialDelay + jitter;
};

/**
 * Create an AbortController with timeout
 */
const createTimeoutController = (
  timeout: number,
  existingSignal?: AbortSignal | null
): { controller: AbortController; cleanup: () => void } => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  // If there's an existing signal, abort when it aborts
  if (existingSignal) {
    existingSignal.addEventListener("abort", () => controller.abort());
  }

  return {
    controller,
    cleanup: () => clearTimeout(timeoutId),
  };
};

/**
 * Create ApiError from response
 */
const createApiError = async (
  response: Response,
  retryable: boolean = false
): Promise<ApiError> => {
  const error: ApiError = {
    message: response.statusText || ERROR_MESSAGES.SERVER_ERROR,
    status: response.status,
    retryable,
  };

  try {
    const errorData = await response.json();
    error.message = errorData.detail || errorData.message || error.message;
    error.code = errorData.code;
    error.details = errorData;
  } catch {
    // Response is not JSON, use status text
  }

  // Map common status codes to user-friendly messages
  switch (response.status) {
    case 401:
      error.message = ERROR_MESSAGES.UNAUTHORIZED;
      break;
    case 403:
      error.message = ERROR_MESSAGES.FORBIDDEN;
      break;
    case 404:
      error.message = ERROR_MESSAGES.NOT_FOUND;
      break;
    case 422:
      error.message = ERROR_MESSAGES.VALIDATION_ERROR;
      break;
    case 500:
    case 502:
    case 503:
    case 504:
      error.message = ERROR_MESSAGES.SERVER_ERROR;
      error.retryable = true;
      break;
  }

  return error;
};

// ============================================================================
// API Client Class
// ============================================================================

export class ApiClient {
  private config: ApiClientConfig;
  private getToken: TokenGetter;
  private refreshToken: TokenRefresher | null = null;
  private onUnauthorized: OnUnauthorized | null = null;
  private onForbidden: OnForbidden | null = null;
  private isRefreshing = false;
  private refreshPromise: Promise<boolean> | null = null;

  constructor(config?: Partial<ApiClientConfig>) {
    this.config = {
      baseURL: config?.baseURL || API_URL,
      defaultTimeout: config?.defaultTimeout || 30000,
      defaultRetries: config?.defaultRetries || 3,
      retryDelay: config?.retryDelay || 1000,
      retryStatusCodes: config?.retryStatusCodes || [408, 429, 500, 502, 503, 504],
    };

    // Default token getter - works on client side only
    this.getToken = () => {
      if (isServer) return null;
      try {
        // Try to get token from zustand persisted storage
        const authStorage = localStorage.getItem("auth-storage");
        if (authStorage) {
          const parsed = JSON.parse(authStorage);
          return parsed?.state?.accessToken || null;
        }
        return null;
      } catch {
        return null;
      }
    };
  }

  // ============================================================================
  // Configuration Methods
  // ============================================================================

  /**
   * Set custom token getter function
   */
  setTokenGetter(getter: TokenGetter): void {
    this.getToken = getter;
  }

  /**
   * Set token refresh function for automatic 401 handling
   */
  setTokenRefresher(refresher: TokenRefresher): void {
    this.refreshToken = refresher;
  }

  /**
   * Set callback for unauthorized errors (after refresh fails)
   */
  setOnUnauthorized(callback: OnUnauthorized): void {
    this.onUnauthorized = callback;
  }

  /**
   * Set callback for forbidden errors
   */
  setOnForbidden(callback: OnForbidden): void {
    this.onForbidden = callback;
  }

  // ============================================================================
  // Core Request Method
  // ============================================================================

  private async request<T>(endpoint: string, options: ApiRequestConfig = {}): Promise<T> {
    const {
      skipAuth = false,
      retries = options.method === "GET" ? this.config.defaultRetries : 0,
      retryDelay = this.config.retryDelay,
      timeout = this.config.defaultTimeout,
      skipRefresh = false,
      ...fetchOptions
    } = options;

    const url = endpoint.startsWith("http") ? endpoint : `${this.config.baseURL}${endpoint}`;

    // Build headers
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...((fetchOptions.headers as Record<string, string>) || {}),
    };

    // Add Authorization header if not skipped
    if (!skipAuth) {
      const token = this.getToken();
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }
    }

    // Retry loop
    let lastError: ApiError | null = null;

    for (let attempt = 0; attempt <= retries; attempt++) {
      // Wait before retry (except first attempt)
      if (attempt > 0) {
        const delay = getRetryDelay(attempt - 1, retryDelay);
        await sleep(delay);
      }

      // Create timeout controller
      const { controller, cleanup } = createTimeoutController(timeout, fetchOptions.signal);

      try {
        const response = await fetch(url, {
          ...fetchOptions,
          headers,
          signal: controller.signal,
        });

        cleanup();

        // Handle successful response
        if (response.ok) {
          // Handle empty responses
          if (response.status === 204 || response.headers.get("content-length") === "0") {
            return {} as T;
          }

          const contentType = response.headers.get("content-type");
          if (contentType?.includes("application/json")) {
            return await response.json();
          }

          return (await response.text()) as unknown as T;
        }

        // Handle 401 - Unauthorized
        if (response.status === 401 && !skipRefresh && this.refreshToken) {
          const refreshed = await this.handleTokenRefresh();
          if (refreshed) {
            // Retry request with new token
            const newToken = this.getToken();
            if (newToken) {
              headers["Authorization"] = `Bearer ${newToken}`;
            }
            // Don't count this as a retry attempt
            attempt--;
            continue;
          }

          // Refresh failed, trigger unauthorized callback
          if (this.onUnauthorized) {
            this.onUnauthorized();
          }
        }

        // Handle 403 - Forbidden
        if (response.status === 403 && this.onForbidden) {
          this.onForbidden();
        }

        // Check if error is retryable
        const isRetryable = this.config.retryStatusCodes.includes(response.status);

        // If not retryable or last attempt, throw error
        if (!isRetryable || attempt === retries) {
          throw await createApiError(response, isRetryable);
        }

        // Store error for potential rethrow
        lastError = await createApiError(response, true);
      } catch (error) {
        cleanup();

        // Handle abort/timeout
        if (error instanceof DOMException && error.name === "AbortError") {
          lastError = {
            message: "Request timeout",
            status: 408,
            retryable: true,
          };

          if (attempt === retries) {
            throw lastError;
          }
          continue;
        }

        // Handle network errors
        if (error instanceof TypeError && error.message.includes("fetch")) {
          lastError = {
            message: ERROR_MESSAGES.NETWORK_ERROR,
            status: 0,
            retryable: true,
          };

          if (attempt === retries) {
            throw lastError;
          }
          continue;
        }

        // Rethrow API errors
        if ((error as ApiError).status !== undefined) {
          throw error;
        }

        // Unknown error
        throw {
          message: error instanceof Error ? error.message : ERROR_MESSAGES.NETWORK_ERROR,
          status: 0,
          retryable: false,
        } as ApiError;
      }
    }

    // Should not reach here, but throw last error if we do
    throw (
      lastError || {
        message: ERROR_MESSAGES.NETWORK_ERROR,
        status: 0,
        retryable: false,
      }
    );
  }

  // ============================================================================
  // Token Refresh Handler
  // ============================================================================

  private async handleTokenRefresh(): Promise<boolean> {
    // If already refreshing, wait for the existing refresh
    if (this.isRefreshing && this.refreshPromise) {
      return this.refreshPromise;
    }

    this.isRefreshing = true;
    this.refreshPromise = (async () => {
      try {
        if (!this.refreshToken) return false;

        const tokens = await this.refreshToken();
        if (tokens) {
          // Token refresh successful
          return true;
        }
        return false;
      } catch {
        return false;
      } finally {
        this.isRefreshing = false;
        this.refreshPromise = null;
      }
    })();

    return this.refreshPromise;
  }

  // ============================================================================
  // HTTP Methods
  // ============================================================================

  async get<T>(endpoint: string, options?: ApiRequestConfig): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: "GET" });
  }

  async post<T>(endpoint: string, data?: unknown, options?: ApiRequestConfig): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: "POST",
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(endpoint: string, data?: unknown, options?: ApiRequestConfig): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: "PUT",
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async patch<T>(endpoint: string, data?: unknown, options?: ApiRequestConfig): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: "PATCH",
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T>(endpoint: string, options?: ApiRequestConfig): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: "DELETE" });
  }

  // ============================================================================
  // Utility Methods
  // ============================================================================

  /**
   * Upload file with multipart/form-data
   */
  async upload<T>(endpoint: string, file: File | FormData, options?: ApiRequestConfig): Promise<T> {
    const formData = file instanceof FormData ? file : new FormData();
    if (file instanceof File) {
      formData.append("file", file);
    }

    // Don't set Content-Type header - browser will set it with boundary
    const headers = { ...((options?.headers as Record<string, string>) || {}) };
    delete headers["Content-Type"];

    return this.request<T>(endpoint, {
      ...options,
      method: "POST",
      body: formData,
      headers,
    });
  }

  /**
   * Create a new client instance for SSR with custom token
   */
  createServerClient(token?: string): ApiClient {
    const serverClient = new ApiClient(this.config);
    if (token) {
      serverClient.setTokenGetter(() => token);
    }
    return serverClient;
  }
}

// ============================================================================
// Singleton Instance & Configuration
// ============================================================================

export const apiClient = new ApiClient();

/**
 * Configure the API client with auth store integration
 * This should be called once in the app initialization
 */
export function configureApiClient(options: {
  getToken: TokenGetter;
  refreshToken: TokenRefresher;
  onUnauthorized: OnUnauthorized;
  onForbidden: OnForbidden;
}): void {
  apiClient.setTokenGetter(options.getToken);
  apiClient.setTokenRefresher(options.refreshToken);
  apiClient.setOnUnauthorized(options.onUnauthorized);
  apiClient.setOnForbidden(options.onForbidden);
}

// Named export for convenience
export const api = apiClient;

// Export default for convenience
export default apiClient;

// ============================================================================
// Server-side API Client Factory
// ============================================================================

/**
 * Create an API client for Server Components
 * Usage in Server Components:
 *
 * ```tsx
 * import { createServerApiClient } from '@/lib/api';
 * import { cookies } from 'next/headers';
 *
 * export default async function ServerComponent() {
 *   const cookieStore = await cookies();
 *   const token = cookieStore.get('accessToken')?.value;
 *   const api = createServerApiClient(token);
 *
 *   const data = await api.get('/api/v1/users/me');
 *   return <div>{data.name}</div>;
 * }
 * ```
 */
export function createServerApiClient(token?: string): ApiClient {
  return apiClient.createServerClient(token);
}
