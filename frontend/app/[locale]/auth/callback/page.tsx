/**
 * Auth Callback Page
 * Handles OAuth callback and stores authentication data
 */

"use client";

import { useAuthStore } from "@/stores/auth";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect } from "react";
import { toast } from "sonner";

function AuthCallbackContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { login: setLoginState } = useAuthStore();

  useEffect(() => {
    const accessToken = searchParams.get("accessToken");
    const refreshToken = searchParams.get("refreshToken");
    const userParam = searchParams.get("user");

    if (accessToken && refreshToken && userParam) {
      try {
        const user = JSON.parse(userParam);
        setLoginState(user, accessToken, refreshToken);
        toast.success("Connexion avec Google réussie");
        router.replace("/dashboard");
      } catch (error) {
        console.error("Failed to parse user data:", error);
        toast.error("Erreur lors de la connexion");
        router.replace("/login");
      }
    } else {
      // No tokens, redirect to login
      router.replace("/login");
    }
  }, [searchParams, router, setLoginState]);

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <div className="mx-auto mb-4 h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent"></div>
        <p className="text-gray-600 dark:text-gray-400">Connexion en cours...</p>
      </div>
    </div>
  );
}

export default function AuthCallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center">
          <div className="text-center">
            <div className="mx-auto mb-4 h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent"></div>
            <p className="text-gray-600 dark:text-gray-400">Chargement...</p>
          </div>
        </div>
      }
    >
      <AuthCallbackContent />
    </Suspense>
  );
}
