/**
 * useAuth Hook
 * Authentication logic and API calls
 */

import { apiClient } from "@/lib/api";
import { ENDPOINTS, ROUTES, SUCCESS_MESSAGES } from "@/lib/constants";
import { useAuthStore } from "@/stores/auth";
import { useRouter } from "next/navigation";
import { useCallback, useEffect } from "react";
import { toast } from "sonner";

interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterData {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
}

// Google OAuth configuration
const GOOGLE_CLIENT_ID = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "";

interface AuthResponse {
  user: {
    id: string;
    email: string;
    firstName: string;
    lastName: string;
    avatarUrl?: string;
    role: "admin" | "leader" | "member";
    organizationId: string;
    isEmailVerified: boolean;
  };
  accessToken: string;
  refreshToken: string;
}

export function useAuth() {
  const router = useRouter();
  const {
    user,
    isAuthenticated,
    isLoading,
    login: setLoginState,
    logout: clearAuthState,
    setLoading,
    setTokens,
  } = useAuthStore();

  // Login
  const login = useCallback(
    async (credentials: LoginCredentials) => {
      try {
        setLoading(true);
        const response = await apiClient.post<AuthResponse>(ENDPOINTS.AUTH.LOGIN, credentials);

        setLoginState(response.user, response.accessToken, response.refreshToken);
        toast.success(SUCCESS_MESSAGES.LOGIN_SUCCESS);
        router.push(ROUTES.DASHBOARD);
      } catch (error) {
        const apiError = error as { message: string };
        toast.error(apiError.message || "Erreur de connexion");
        throw error;
      } finally {
        setLoading(false);
      }
    },
    [router, setLoginState, setLoading]
  );

  // Register
  const register = useCallback(
    async (data: RegisterData) => {
      try {
        setLoading(true);
        console.log("Register request data:", JSON.stringify(data, null, 2));
        const response = await apiClient.post<AuthResponse>(ENDPOINTS.AUTH.REGISTER, data);
        console.log("Register response:", response);

        setLoginState(response.user, response.accessToken, response.refreshToken);
        toast.success(SUCCESS_MESSAGES.REGISTER_SUCCESS);
        router.push(ROUTES.DASHBOARD);
      } catch (error) {
        const apiError = error as {
          message: string;
          details?: { detail?: Array<{ loc: string[]; msg: string }> | string };
        };
        console.error("Register error details:", apiError);

        // Extract detailed error message
        let errorMessage = apiError.message || "Erreur d'inscription";
        if (apiError.details?.detail) {
          if (Array.isArray(apiError.details.detail)) {
            errorMessage = apiError.details.detail
              .map((e) => `${e.loc?.join(".")}: ${e.msg}`)
              .join(", ");
          } else if (typeof apiError.details.detail === "string") {
            errorMessage = apiError.details.detail;
          }
        }

        toast.error(errorMessage);
        throw error;
      } finally {
        setLoading(false);
      }
    },
    [router, setLoginState, setLoading]
  );

  // Logout
  const logout = useCallback(async () => {
    try {
      await apiClient.post(ENDPOINTS.AUTH.LOGOUT);
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      clearAuthState();
      router.push(ROUTES.LOGIN);
      toast.success("Déconnexion réussie");
    }
  }, [router, clearAuthState]);

  // Refresh token
  const refreshToken = useCallback(async () => {
    try {
      const currentRefreshToken = useAuthStore.getState().refreshToken;
      if (!currentRefreshToken) {
        throw new Error("No refresh token available");
      }

      const response = await apiClient.post<{ accessToken: string; refreshToken: string }>(
        ENDPOINTS.AUTH.REFRESH,
        { refreshToken: currentRefreshToken }
      );

      setTokens(response.accessToken, response.refreshToken);
      return response.accessToken;
    } catch (error) {
      console.error("Token refresh error:", error);
      clearAuthState();
      router.push(ROUTES.LOGIN);
      throw error;
    }
  }, [router, setTokens, clearAuthState]);

  // Forgot password
  const forgotPassword = useCallback(
    async (email: string) => {
      try {
        setLoading(true);
        await apiClient.post(ENDPOINTS.AUTH.FORGOT_PASSWORD, { email });
        toast.success("Email de réinitialisation envoyé");
      } catch (error) {
        const apiError = error as { message: string };
        toast.error(apiError.message || "Erreur lors de l'envoi de l'email");
        throw error;
      } finally {
        setLoading(false);
      }
    },
    [setLoading]
  );

  // Reset password
  const resetPassword = useCallback(
    async (token: string, newPassword: string) => {
      try {
        setLoading(true);
        await apiClient.post(ENDPOINTS.AUTH.RESET_PASSWORD, {
          token,
          newPassword,
        });
        toast.success("Mot de passe réinitialisé");
        router.push(ROUTES.LOGIN);
      } catch (error) {
        const apiError = error as { message: string };
        toast.error(apiError.message || "Erreur lors de la réinitialisation");
        throw error;
      } finally {
        setLoading(false);
      }
    },
    [router, setLoading]
  );

  // Verify email
  const verifyEmail = useCallback(
    async (token: string) => {
      try {
        setLoading(true);
        await apiClient.post(ENDPOINTS.AUTH.VERIFY_EMAIL, { token });
        toast.success("Email vérifié avec succès");
      } catch (error) {
        const apiError = error as { message: string };
        toast.error(apiError.message || "Erreur lors de la vérification");
        throw error;
      } finally {
        setLoading(false);
      }
    },
    [setLoading]
  );

  // Login with Google
  const loginWithGoogle = useCallback(async () => {
    if (!GOOGLE_CLIENT_ID) {
      toast.error("Google OAuth n'est pas configuré");
      return;
    }

    try {
      setLoading(true);

      // Create OAuth2 URL for Google Sign-In
      const redirectUri = `${window.location.origin}/api/auth/callback/google`;
      const scope = "openid email profile";
      const responseType = "code";
      const state = crypto.randomUUID();

      // Store state for CSRF protection
      sessionStorage.setItem("google_oauth_state", state);

      const googleAuthUrl = new URL("https://accounts.google.com/o/oauth2/v2/auth");
      googleAuthUrl.searchParams.set("client_id", GOOGLE_CLIENT_ID);
      googleAuthUrl.searchParams.set("redirect_uri", redirectUri);
      googleAuthUrl.searchParams.set("response_type", responseType);
      googleAuthUrl.searchParams.set("scope", scope);
      googleAuthUrl.searchParams.set("state", state);
      googleAuthUrl.searchParams.set("access_type", "offline");
      googleAuthUrl.searchParams.set("prompt", "consent");

      // Redirect to Google OAuth
      window.location.href = googleAuthUrl.toString();
    } catch (error) {
      console.error("Google login error:", error);
      toast.error("Erreur lors de la connexion avec Google");
      setLoading(false);
    }
  }, [setLoading]);

  // Auto-refresh token before expiry
  useEffect(() => {
    if (!isAuthenticated) return;

    // Set up token refresh interval (every 14 minutes for 15-minute tokens)
    const refreshInterval = setInterval(
      () => {
        refreshToken().catch(console.error);
      },
      14 * 60 * 1000
    );

    return () => clearInterval(refreshInterval);
  }, [isAuthenticated, refreshToken]);

  return {
    user,
    isAuthenticated,
    isLoading,
    login,
    loginWithGoogle,
    register,
    logout,
    refreshToken,
    forgotPassword,
    resetPassword,
    verifyEmail,
  };
}
