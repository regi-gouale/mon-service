/**
 * useMockAuth Hook
 * Mock authentication for frontend development without backend
 * Set NEXT_PUBLIC_MOCK_API=true in .env.local to enable
 */

import { currentMockUser, simulateDelay, validateMockLogin, type MockUser } from "@/lib/mock-data";
import { useAuthStore } from "@/stores/auth";
import { useRouter } from "next/navigation";
import { useCallback } from "react";
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

// Check if mock mode is enabled
export const isMockMode = process.env.NEXT_PUBLIC_MOCK_API === "true";

export function useMockAuth() {
  const router = useRouter();
  const {
    user,
    isAuthenticated,
    isLoading,
    hasHydrated,
    login: setLoginState,
    logout: clearAuthState,
    setLoading,
  } = useAuthStore();

  // Mock Login
  const login = useCallback(
    async (credentials: LoginCredentials) => {
      try {
        setLoading(true);
        await simulateDelay(800);

        const mockUser = validateMockLogin(credentials.email, credentials.password);

        if (!mockUser) {
          throw new Error("Email ou mot de passe incorrect");
        }

        // Convert MockUser to the format expected by auth store
        const user = {
          id: mockUser.id,
          email: mockUser.email,
          firstName: mockUser.firstName,
          lastName: mockUser.lastName,
          avatarUrl: mockUser.avatarUrl,
          role: mockUser.role,
          organizationId: mockUser.organizationId,
          isEmailVerified: mockUser.isEmailVerified,
        };

        setLoginState(user, "mock-access-token", "mock-refresh-token");
        toast.success("Connexion réussie (mode démo)");
        router.push("/dashboard");
      } catch (error) {
        const message = error instanceof Error ? error.message : "Erreur de connexion";
        toast.error(message);
        throw error;
      } finally {
        setLoading(false);
      }
    },
    [router, setLoginState, setLoading]
  );

  // Mock Register
  const register = useCallback(
    async (data: RegisterData) => {
      try {
        setLoading(true);
        await simulateDelay(1000);

        // Create a new mock user
        const newUser: MockUser = {
          id: `user-${Date.now()}`,
          email: data.email,
          firstName: data.firstName,
          lastName: data.lastName,
          avatarUrl: undefined,
          role: "member",
          organizationId: "org-1",
          isEmailVerified: false,
        };

        setLoginState(newUser, "mock-access-token", "mock-refresh-token");
        toast.success("Inscription réussie ! (mode démo)");
        router.push("/dashboard");
      } catch (error) {
        const message = error instanceof Error ? error.message : "Erreur d'inscription";
        toast.error(message);
        throw error;
      } finally {
        setLoading(false);
      }
    },
    [router, setLoginState, setLoading]
  );

  // Mock Logout
  const logout = useCallback(async () => {
    await simulateDelay(300);
    clearAuthState();
    router.push("/login");
    toast.success("Déconnexion réussie");
  }, [router, clearAuthState]);

  // Mock Forgot Password
  const forgotPassword = useCallback(
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    async (email: string) => {
      try {
        setLoading(true);
        await simulateDelay(800);
        toast.success("Email de réinitialisation envoyé (mode démo)");
      } finally {
        setLoading(false);
      }
    },
    [setLoading]
  );

  // Mock Reset Password
  const resetPassword = useCallback(
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    async (token: string, newPassword: string) => {
      try {
        setLoading(true);
        await simulateDelay(800);
        toast.success("Mot de passe réinitialisé (mode démo)");
        router.push("/login");
      } finally {
        setLoading(false);
      }
    },
    [router, setLoading]
  );

  // Mock Verify Email
  const verifyEmail = useCallback(
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    async (token: string) => {
      try {
        setLoading(true);
        await simulateDelay(1000);
        toast.success("Email vérifié (mode démo)");
      } finally {
        setLoading(false);
      }
    },
    [setLoading]
  );

  // Mock Google Login
  const loginWithGoogle = useCallback(async () => {
    try {
      setLoading(true);
      await simulateDelay(800);

      // Auto-login with mock user for Google
      const googleUser: MockUser = {
        ...currentMockUser,
        email: "google.user@gmail.com",
        firstName: "Google",
        lastName: "User",
      };

      setLoginState(googleUser, "mock-google-token", "mock-refresh-token");
      toast.success("Connexion Google réussie (mode démo)");
      router.push("/dashboard");
    } catch (error) {
      toast.error("Erreur lors de la connexion Google");
      throw error;
    } finally {
      setLoading(false);
    }
  }, [router, setLoginState, setLoading]);

  // Mock Refresh Token
  const refreshToken = useCallback(async () => {
    await simulateDelay(200);
    return "mock-refreshed-token";
  }, []);

  return {
    user,
    isAuthenticated,
    isLoading,
    hasHydrated,
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
