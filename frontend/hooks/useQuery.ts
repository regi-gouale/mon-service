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
  departmentId: string,
  year: number,
  month: number,
  options?: Omit<UseQueryOptions<unknown, ApiError>, "queryKey" | "queryFn">
) {
  const monthStr = `${year}-${String(month).padStart(2, "0")}`;
  return useQuery({
    queryKey: queryKeys.availabilities.member(departmentId, monthStr),
    queryFn: () =>
      api.get(`/departments/${departmentId}/members/me/availabilities?year=${year}&month=${month}`),
    enabled: !!departmentId && !!year && !!month,
    ...options,
  });
}

/**
 * Hook for fetching my availabilities (current user)
 */
export function useMyAvailabilities(
  departmentId: string,
  year: number,
  month: number,
  options?: Omit<UseQueryOptions<unknown, ApiError>, "queryKey" | "queryFn">
) {
  const monthStr = `${year}-${String(month).padStart(2, "0")}`;
  return useQuery({
    queryKey: ["my-availabilities", departmentId, monthStr],
    queryFn: () =>
      api.get(`/departments/${departmentId}/members/me/availabilities?year=${year}&month=${month}`),
    enabled: !!departmentId && !!year && !!month,
    ...options,
  });
}

/**
 * Hook for fetching department availabilities
 */
export function useDepartmentAvailabilities(
  departmentId: string,
  year: number,
  month: number,
  options?: Omit<UseQueryOptions<unknown, ApiError>, "queryKey" | "queryFn">
) {
  const monthStr = `${year}-${String(month).padStart(2, "0")}`;
  return useQuery({
    queryKey: queryKeys.availabilities.department(departmentId, monthStr),
    queryFn: () =>
      api.get(`/departments/${departmentId}/availabilities?year=${year}&month=${month}`),
    enabled: !!departmentId && !!year && !!month,
    ...options,
  });
}

/**
 * Hook for fetching availability deadline
 */
export function useAvailabilityDeadline(
  departmentId: string,
  year: number,
  month: number,
  options?: Omit<UseQueryOptions<unknown, ApiError>, "queryKey" | "queryFn">
) {
  const monthStr = `${year}-${String(month).padStart(2, "0")}`;
  return useQuery({
    queryKey: ["availability-deadline", departmentId, monthStr],
    queryFn: () =>
      api.get(`/departments/${departmentId}/availabilities/deadline?year=${year}&month=${month}`),
    enabled: !!departmentId && !!year && !!month,
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
 * Hook for updating member availabilities (current user) with optimistic updates
 */
export function useUpdateMyAvailabilities(departmentId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      year: number;
      month: number;
      unavailableDates: Array<{ date: string; reason?: string; isAllDay: boolean }>;
    }) => api.put(`/departments/${departmentId}/members/me/availabilities`, data),

    // Optimistic update
    onMutate: async (newData) => {
      const monthStr = `${newData.year}-${String(newData.month).padStart(2, "0")}`;
      const queryKey = ["my-availabilities", departmentId, monthStr];

      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey });

      // Snapshot the previous value
      const previousData = queryClient.getQueryData(queryKey);

      // Optimistically update to the new value
      queryClient.setQueryData(queryKey, (old: unknown) => {
        if (!old || typeof old !== "object") {
          return {
            memberId: "",
            memberName: "",
            year: newData.year,
            month: newData.month,
            unavailableDates: newData.unavailableDates,
          };
        }
        return {
          ...old,
          unavailableDates: newData.unavailableDates,
        };
      });

      // Return context with the previous value
      return { previousData, queryKey };
    },

    // If the mutation fails, rollback to the previous value
    onError: (_err, _newData, context) => {
      if (context?.previousData !== undefined) {
        queryClient.setQueryData(context.queryKey, context.previousData);
      }
    },

    // Always refetch after error or success
    onSettled: (_, __, variables) => {
      const monthStr = `${variables.year}-${String(variables.month).padStart(2, "0")}`;
      // Invalidate my availabilities
      queryClient.invalidateQueries({
        queryKey: ["my-availabilities", departmentId, monthStr],
      });
      // Invalidate department availabilities
      queryClient.invalidateQueries({
        queryKey: queryKeys.availabilities.department(departmentId, monthStr),
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
