/**
 * Dashboard Layout
 * Main layout for authenticated dashboard pages
 */

"use client";

import { Button } from "@/components/ui/button";
import { useRouter } from "@/i18n/navigation";
import { useAuthStore } from "@/stores/auth";
import { IconBell, IconLoader2, IconUser } from "@tabler/icons-react";
import { useTranslations } from "next-intl";
import { ReactNode, useEffect } from "react";

interface DashboardLayoutProps {
  children: ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const t = useTranslations("Common");
  const tNav = useTranslations("Navigation");
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuthStore();

  // Protect dashboard routes
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, isLoading, router]);

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <IconLoader2 className="text-primary mx-auto mb-4 h-12 w-12 animate-spin" />
          <p className="text-muted-foreground">{t("loading")}</p>
        </div>
      </div>
    );
  }

  // Don't render dashboard if not authenticated
  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="bg-background min-h-screen">
      {/* Header */}
      <header className="bg-card border-b">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center">
              <h1 className="text-foreground text-xl font-semibold">Mon Service</h1>
            </div>

            <nav className="flex items-center gap-2">
              <Button variant="ghost" size="icon" aria-label={tNav("notifications")}>
                <IconBell className="h-5 w-5" />
              </Button>
              <Button variant="ghost" size="icon" aria-label={tNav("profile")}>
                <IconUser className="h-5 w-5" />
              </Button>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">{children}</main>

      {/* Footer */}
      <footer className="bg-card mt-auto border-t">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <p className="text-muted-foreground text-center text-sm">
            © 2025 Mon Service. Tous droits réservés.
          </p>
        </div>
      </footer>
    </div>
  );
}
