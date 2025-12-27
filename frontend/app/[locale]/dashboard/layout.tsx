/**
 * Dashboard Layout
 * Main layout for authenticated dashboard pages with sidebar navigation
 */

"use client";

import { AppSidebar } from "@/components/layouts/app-sidebar";
import { Separator } from "@/components/ui/separator";
import { SidebarInset, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { useRouter } from "@/i18n/navigation";
import { useAuthStore } from "@/stores/auth";
import { IconLoader2 } from "@tabler/icons-react";
import { useTranslations } from "next-intl";
import { ReactNode, useEffect } from "react";

interface DashboardLayoutProps {
  children: ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const t = useTranslations("Common");
  const router = useRouter();
  const { isAuthenticated, isLoading, hasHydrated } = useAuthStore();

  // Protect dashboard routes - only redirect after hydration is complete
  useEffect(() => {
    if (hasHydrated && !isLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, isLoading, hasHydrated, router]);

  // Show loading state while checking authentication or hydrating
  if (!hasHydrated || isLoading) {
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
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        {/* Header */}
        <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4">
          <SidebarTrigger className="-ml-1" />
          <Separator orientation="vertical" className="mr-2 h-4" />
          <h1 className="text-foreground text-lg font-semibold">Mon Service</h1>
        </header>

        {/* Main Content */}
        <main className="flex-1 p-4 md:p-6">{children}</main>

        {/* Footer */}
        <footer className="border-t px-4 py-4">
          <p className="text-muted-foreground text-center text-sm">
            © 2025 Mon Service. Tous droits réservés.
          </p>
        </footer>
      </SidebarInset>
    </SidebarProvider>
  );
}
