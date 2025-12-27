/**
 * API Provider Component
 * Configures the API client with authentication integration
 */

"use client";

import { configureApiClient } from "@/lib/api";
import { ENDPOINTS, ROUTES } from "@/lib/constants";
import { useAuthStore } from "@/stores/auth";
import { useRouter } from "next/navigation";
import { useEffect, useRef } from "react";

interface ApiProviderProps {
  children: React.ReactNode;
}

interface RefreshResponse {
  accessToken: string;
  refreshToken: string;
}

export function ApiProvider({ children }: ApiProviderProps) {
  const router = useRouter();
  const isConfigured = useRef(false);

  useEffect(() => {
    // Only configure once
    if (isConfigured.current) return;
    isConfigured.current = true;

    configureApiClient({
      // Get token from store
      getToken: () => {
        return useAuthStore.getState().accessToken;
      },

      // Refresh token function
      refreshToken: async () => {
        const currentRefreshToken = useAuthStore.getState().refreshToken;
        if (!currentRefreshToken) return null;

        try {
          const response = await fetch(
            `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}${ENDPOINTS.AUTH.REFRESH}`,
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({ refreshToken: currentRefreshToken }),
            }
          );

          if (!response.ok) return null;

          const data: RefreshResponse = await response.json();

          // Update store with new tokens
          useAuthStore.getState().setTokens(data.accessToken, data.refreshToken);

          return data;
        } catch (error) {
          console.error("Token refresh failed:", error);
          return null;
        }
      },

      // Handle unauthorized (after refresh fails)
      onUnauthorized: () => {
        // Clear auth state and redirect to login
        useAuthStore.getState().logout();
        router.push(ROUTES.LOGIN);
      },

      // Handle forbidden
      onForbidden: () => {
        // Redirect to dashboard with error message
        router.push(ROUTES.DASHBOARD);
      },
    });
  }, [router]);

  return <>{children}</>;
}
