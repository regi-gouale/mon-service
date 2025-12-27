/**
 * Auth Callback Page
 * Handles OAuth callback and stores authentication data
 */

"use client";

import { useAuthStore } from "@/stores/auth";
import { IconLoader2 } from "@tabler/icons-react";
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
    <div className="bg-background flex min-h-screen items-center justify-center">
      <div className="text-center">
        <IconLoader2 className="text-primary mx-auto mb-4 h-8 w-8 animate-spin" />
        <p className="text-muted-foreground">Connexion en cours...</p>
      </div>
    </div>
  );
}

export default function AuthCallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="bg-background flex min-h-screen items-center justify-center">
          <div className="text-center">
            <IconLoader2 className="text-primary mx-auto mb-4 h-8 w-8 animate-spin" />
            <p className="text-muted-foreground">Chargement...</p>
          </div>
        </div>
      }
    >
      <AuthCallbackContent />
    </Suspense>
  );
}
