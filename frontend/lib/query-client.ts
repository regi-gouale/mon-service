/**
 * TanStack Query Client Configuration
 * Centralized configuration for React Query with optimized defaults
 */

import { MutationCache, QueryCache, QueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import type { ApiError } from "./api";

/**
 * Default configuration for TanStack Query
 */
const queryConfig = {
  queries: {
    // Cache time: 5 minutes - How long unused data stays in cache
    gcTime: 1000 * 60 * 5,
    // Stale time: 30 seconds - Data is fresh for 30s, then marked stale
    staleTime: 1000 * 30,
    // Retry failed queries 1 time with exponential backoff
    retry: 1,
    // Don't refetch on window focus in development to reduce noise
    refetchOnWindowFocus: process.env.NODE_ENV === "production",
    // Don't refetch on reconnect
    refetchOnReconnect: false,
    // Don't refetch on mount if data exists
    refetchOnMount: false,
  },
  mutations: {
    // Retry mutations 0 times by default
    retry: 0,
  },
};

/**
 * Global error handler for queries
 */
const queryCache = new QueryCache({
  onError: (error, query) => {
    // Only show error toasts if we already have data in the cache
    // which indicates a failed background update
    if (query.state.data !== undefined) {
      const apiError = error as unknown as ApiError;
      toast.error(
        apiError.message || "Une erreur est survenue lors de la récupération des données"
      );
    }
  },
});

/**
 * Global error handler for mutations
 */
const mutationCache = new MutationCache({
  onError: (error) => {
    const apiError = error as unknown as ApiError;
    toast.error(apiError.message || "Une erreur est survenue lors de l'opération");
  },
});

/**
 * Create a new QueryClient instance with default configuration
 */
export const queryClient = new QueryClient({
  queryCache,
  mutationCache,
  defaultOptions: queryConfig,
});

/**
 * Query key factory helpers
 * Provides consistent query key structure across the app
 */
export const queryKeys = {
  // Auth
  auth: {
    me: ["auth", "me"] as const,
  },
  // Users
  users: {
    all: ["users"] as const,
    detail: (id: string) => ["users", id] as const,
  },
  // Departments
  departments: {
    all: ["departments"] as const,
    detail: (id: string) => ["departments", id] as const,
    members: (id: string) => ["departments", id, "members"] as const,
  },
  // Availabilities
  availabilities: {
    member: (memberId: string, month: string) =>
      ["availabilities", "member", memberId, month] as const,
    department: (deptId: string, month: string) =>
      ["availabilities", "department", deptId, month] as const,
  },
  // Plannings
  plannings: {
    all: (deptId: string) => ["plannings", deptId] as const,
    detail: (id: string) => ["plannings", id] as const,
  },
  // Notifications
  notifications: {
    all: ["notifications"] as const,
    unread: ["notifications", "unread"] as const,
  },
};
