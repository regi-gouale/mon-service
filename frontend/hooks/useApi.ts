/**
 * useApi Hook
 * Generic API request hook with loading and error states
 */

import { apiClient, type ApiError, type ApiRequestConfig } from "@/lib/api";
import { useCallback, useState } from "react";
import { toast } from "sonner";

interface UseApiOptions {
  showSuccessToast?: boolean;
  showErrorToast?: boolean;
  successMessage?: string;
  errorMessage?: string;
  /** API request configuration (retries, timeout, etc.) */
  requestConfig?: ApiRequestConfig;
}

interface UseApiState<T> {
  data: T | null;
  error: ApiError | null;
  isLoading: boolean;
}

export function useApi<T = unknown>(options: UseApiOptions = {}) {
  const {
    showSuccessToast = false,
    showErrorToast = true,
    successMessage = "Opération réussie",
    errorMessage = "Une erreur est survenue",
  } = options;

  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    error: null,
    isLoading: false,
  });

  const execute = useCallback(
    async (requestFn: () => Promise<T>, customOptions?: UseApiOptions): Promise<T | null> => {
      setState({ data: null, error: null, isLoading: true });

      try {
        const data = await requestFn();
        setState({ data, error: null, isLoading: false });

        if (customOptions?.showSuccessToast ?? showSuccessToast) {
          toast.success(customOptions?.successMessage ?? successMessage);
        }

        return data;
      } catch (error) {
        const apiError = error as ApiError;
        setState({ data: null, error: apiError, isLoading: false });

        if (customOptions?.showErrorToast ?? showErrorToast) {
          toast.error(apiError.message || (customOptions?.errorMessage ?? errorMessage));
        }

        return null;
      }
    },
    [showSuccessToast, showErrorToast, successMessage, errorMessage]
  );

  const reset = useCallback(() => {
    setState({ data: null, error: null, isLoading: false });
  }, []);

  return {
    ...state,
    execute,
    reset,
  };
}

// Specific hooks for common operations
export function useGet<T = unknown>(endpoint: string, options?: UseApiOptions) {
  const { execute, ...state } = useApi<T>(options);

  const get = useCallback(
    (customOptions?: UseApiOptions) => execute(() => apiClient.get<T>(endpoint), customOptions),
    [endpoint, execute]
  );

  return { get, ...state };
}

export function usePost<T = unknown>(endpoint: string, options?: UseApiOptions) {
  const { execute, ...state } = useApi<T>(options);

  const post = useCallback(
    (data?: unknown, customOptions?: UseApiOptions) =>
      execute(() => apiClient.post<T>(endpoint, data), customOptions),
    [endpoint, execute]
  );

  return { post, ...state };
}

export function usePut<T = unknown>(endpoint: string, options?: UseApiOptions) {
  const { execute, ...state } = useApi<T>(options);

  const put = useCallback(
    (data?: unknown, customOptions?: UseApiOptions) =>
      execute(() => apiClient.put<T>(endpoint, data), customOptions),
    [endpoint, execute]
  );

  return { put, ...state };
}

export function useDelete<T = unknown>(endpoint: string, options?: UseApiOptions) {
  const { execute, ...state } = useApi<T>(options);

  const del = useCallback(
    (customOptions?: UseApiOptions) => execute(() => apiClient.delete<T>(endpoint), customOptions),
    [endpoint, execute]
  );

  return { delete: del, ...state };
}
