/**
 * Custom React Query Hooks
 * Reusable hooks for common API operations with TanStack Query
 */

import { api, type ApiError } from "@/lib/api";
import { queryKeys } from "@/lib/query-client";
import {
  useMutation,
  useQuery,
  useQueryClient,
  type MutationFunctionContext,
  type UseMutationOptions,
  type UseQueryOptions,
} from "@tanstack/react-query";

/**
 * Hook for fetching the current authenticated user
 */
export function useCurrentUser(
  options?: Omit<UseQueryOptions<unknown, ApiError>, "queryKey" | "queryFn">
) {
  return useQuery({
    queryKey: queryKeys.auth.me,
    queryFn: () => api.get("/users/me"),
    ...options,
  });
}

/**
 * Hook for fetching a user by ID
 */
export function useUser(
  userId: string,
  options?: Omit<UseQueryOptions<unknown, ApiError>, "queryKey" | "queryFn">
) {
  return useQuery({
    queryKey: queryKeys.users.detail(userId),
    queryFn: () => api.get(`/users/${userId}`),
    enabled: !!userId,
    ...options,
  });
}

/**
 * Hook for fetching all departments
 */
export function useDepartments(
  options?: Omit<UseQueryOptions<unknown[], ApiError>, "queryKey" | "queryFn">
) {
  return useQuery({
    queryKey: queryKeys.departments.all,
    queryFn: () => api.get<unknown[]>("/departments"),
    ...options,
  });
}

/**
 * Hook for fetching a single department
 */
export function useDepartment(
  departmentId: string,
  options?: Omit<UseQueryOptions<unknown, ApiError>, "queryKey" | "queryFn">
) {
  return useQuery({
    queryKey: queryKeys.departments.detail(departmentId),
    queryFn: () => api.get(`/departments/${departmentId}`),
    enabled: !!departmentId,
    ...options,
  });
}

/**
 * Hook for fetching department members
 */
export function useDepartmentMembers(
  departmentId: string,
  options?: Omit<UseQueryOptions<unknown[], ApiError>, "queryKey" | "queryFn">
) {
  return useQuery({
    queryKey: queryKeys.departments.members(departmentId),
    queryFn: () => api.get<unknown[]>(`/departments/${departmentId}/members`),
    enabled: !!departmentId,
    ...options,
  });
}

/**
 * Hook for fetching member availabilities
 */
export function useMemberAvailabilities(
  memberId: string,
  month: string,
  options?: Omit<UseQueryOptions<unknown, ApiError>, "queryKey" | "queryFn">
) {
  return useQuery({
    queryKey: queryKeys.availabilities.member(memberId, month),
    queryFn: () => api.get(`/availabilities/members/${memberId}?month=${month}`),
    enabled: !!memberId && !!month,
    ...options,
  });
}

/**
 * Hook for fetching department availabilities
 */
export function useDepartmentAvailabilities(
  departmentId: string,
  month: string,
  options?: Omit<UseQueryOptions<unknown, ApiError>, "queryKey" | "queryFn">
) {
  return useQuery({
    queryKey: queryKeys.availabilities.department(departmentId, month),
    queryFn: () => api.get(`/departments/${departmentId}/availabilities?month=${month}`),
    enabled: !!departmentId && !!month,
    ...options,
  });
}

/**
 * Hook for fetching plannings
 */
export function usePlannings(
  departmentId: string,
  options?: Omit<UseQueryOptions<unknown[], ApiError>, "queryKey" | "queryFn">
) {
  return useQuery({
    queryKey: queryKeys.plannings.all(departmentId),
    queryFn: () => api.get<unknown[]>(`/departments/${departmentId}/plannings`),
    enabled: !!departmentId,
    ...options,
  });
}

/**
 * Hook for fetching a single planning
 */
export function usePlanning(
  planningId: string,
  options?: Omit<UseQueryOptions<unknown, ApiError>, "queryKey" | "queryFn">
) {
  return useQuery({
    queryKey: queryKeys.plannings.detail(planningId),
    queryFn: () => api.get(`/plannings/${planningId}`),
    enabled: !!planningId,
    ...options,
  });
}

/**
 * Hook for fetching notifications
 */
export function useNotifications(
  options?: Omit<UseQueryOptions<unknown[], ApiError>, "queryKey" | "queryFn">
) {
  return useQuery({
    queryKey: queryKeys.notifications.all,
    queryFn: () => api.get<unknown[]>("/notifications"),
    ...options,
  });
}

/**
 * Hook for fetching unread notification count
 */
export function useUnreadNotifications(
  options?: Omit<UseQueryOptions<number, ApiError>, "queryKey" | "queryFn">
) {
  return useQuery({
    queryKey: queryKeys.notifications.unread,
    queryFn: () => api.get<number>("/notifications/unread/count"),
    // Refetch more frequently for notifications
    refetchInterval: 60000, // 1 minute
    ...options,
  });
}

/**
 * Generic mutation hook for POST requests
 */
/**
 * Generic mutation hook for POST requests
 */
export function useCreateMutation<TData = unknown, TVariables = unknown>(
  endpoint: string,
  invalidateKeys?: readonly unknown[][],
  options?: Omit<UseMutationOptions<TData, ApiError, TVariables>, "mutationFn">
) {
  const queryClient = useQueryClient();

  const { onSuccess, ...restOptions } = options || {};

  return useMutation<TData, ApiError, TVariables>({
    mutationFn: (data: TVariables) => api.post<TData>(endpoint, data),
    onSuccess: (data, variables, context) => {
      // Invalidate specified query keys
      if (invalidateKeys) {
        invalidateKeys.forEach((key) => {
          queryClient.invalidateQueries({ queryKey: key as unknown[] });
        });
      }
      // Call custom onSuccess if provided
      if (onSuccess) {
        onSuccess(data, variables, undefined, context as MutationFunctionContext);
      }
    },
    ...restOptions,
  });
}

/**
 * Generic mutation hook for PATCH/PUT requests
 */
/**
 * Generic mutation hook for PATCH/PUT requests
 */
export function useUpdateMutation<TData = unknown, TVariables = unknown>(
  endpoint: string | ((variables: TVariables) => string),
  invalidateKeys?: readonly unknown[][],
  options?: Omit<UseMutationOptions<TData, ApiError, TVariables>, "mutationFn">
) {
  const queryClient = useQueryClient();

  const { onSuccess, ...restOptions } = options || {};

  return useMutation<TData, ApiError, TVariables>({
    mutationFn: (data: TVariables) => {
      const url = typeof endpoint === "function" ? endpoint(data) : endpoint;
      return api.patch<TData>(url, data);
    },
    onSuccess: (data, variables, context) => {
      if (invalidateKeys) {
        invalidateKeys.forEach((key) => {
          queryClient.invalidateQueries({ queryKey: key as unknown[] });
        });
      }
      if (onSuccess) {
        onSuccess(data, variables, undefined, context as MutationFunctionContext);
      }
    },
    ...restOptions,
  });
}

/**
 * Generic mutation hook for DELETE requests
 */
/**
 * Generic mutation hook for DELETE requests
 */
export function useDeleteMutation<TData = void, TVariables = string>(
  endpoint: string | ((id: TVariables) => string),
  invalidateKeys?: readonly unknown[][],
  options?: Omit<UseMutationOptions<TData, ApiError, TVariables>, "mutationFn">
) {
  const queryClient = useQueryClient();

  const { onSuccess, ...restOptions } = options || {};

  return useMutation<TData, ApiError, TVariables>({
    mutationFn: (id: TVariables) => {
      const url = typeof endpoint === "function" ? endpoint(id) : `${endpoint}/${id}`;
      return api.delete<TData>(url);
    },
    onSuccess: (data, variables, context) => {
      if (invalidateKeys) {
        invalidateKeys.forEach((key) => {
          queryClient.invalidateQueries({ queryKey: key as unknown[] });
        });
      }
      if (onSuccess) {
        onSuccess(data, variables, undefined, context as MutationFunctionContext);
      }
    },
    ...restOptions,
  });
}

/**
 * Hook for updating member availabilities
 */
export function useUpdateAvailabilities(departmentId: string, memberId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { month: string; dates: string[] }) =>
      api.put(`/departments/${departmentId}/members/me/availabilities`, data),
    onSuccess: (_, variables) => {
      // Invalidate both member and department availabilities
      queryClient.invalidateQueries({
        queryKey: queryKeys.availabilities.member(memberId, variables.month),
      });
      queryClient.invalidateQueries({
        queryKey: queryKeys.availabilities.department(departmentId, variables.month),
      });
    },
  });
}

/**
 * Hook for marking notifications as read
 */
export function useMarkNotificationRead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (notificationId: string) => api.patch(`/notifications/${notificationId}/read`),
    onSuccess: () => {
      // Invalidate both all notifications and unread count
      queryClient.invalidateQueries({ queryKey: queryKeys.notifications.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.notifications.unread });
    },
  });
}
