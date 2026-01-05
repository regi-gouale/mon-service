/**
 * Dashboard Layout
 * Main layout for authenticated dashboard pages with sidebar navigation
 * Inspired by Planning Center's clean and functional design
 */

"use client";

import { AppSidebar } from "@/components/layouts/app-sidebar";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Separator } from "@/components/ui/separator";
import { SidebarInset, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { useRouter } from "@/i18n/navigation";
import { useAuthStore } from "@/stores/auth";
import {
  IconBell,
  IconCalendarEvent,
  IconHelpCircle,
  IconMoon,
  IconSearch,
  IconSun,
} from "@tabler/icons-react";
import { useTranslations } from "next-intl";
import { useTheme } from "next-themes";
import { ReactNode, useEffect, useSyncExternalStore } from "react";

interface DashboardLayoutProps {
  children: ReactNode;
}

const emptySubscribe = () => () => {};

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const t = useTranslations("Common");
  const tNav = useTranslations("Navigation");
  const router = useRouter();
  const { isAuthenticated, isLoading, hasHydrated } = useAuthStore();
  const { theme, setTheme } = useTheme();
  const mounted = useSyncExternalStore(
    emptySubscribe,
    () => true,
    () => false
  );

  // Protect dashboard routes - only redirect after hydration is complete
  useEffect(() => {
    if (hasHydrated && !isLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, isLoading, hasHydrated, router]);

  // Show loading state while checking authentication or hydrating
  if (!hasHydrated || isLoading) {
    return (
      <div className="bg-background flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="relative mb-4">
            <div className="bg-primary mx-auto flex h-16 w-16 items-center justify-center rounded-2xl">
              <IconCalendarEvent className="text-primary-foreground h-8 w-8" />
            </div>
            <div className="border-primary absolute -right-1 -bottom-1 h-6 w-6 animate-spin rounded-full border-2 border-t-transparent" />
          </div>
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
      <SidebarInset className="bg-muted/30">
        {/* Header - Inspired by Planning Center's clean top bar */}
        <header className="bg-background/95 supports-backdrop-filter:bg-background/60 sticky top-0 z-40 flex h-14 items-center gap-4 border-b px-4 backdrop-blur lg:px-6">
          <SidebarTrigger className="-ml-1" />
          <Separator orientation="vertical" className="h-5" />

          {/* Search bar */}
          <div className="relative hidden max-w-md flex-1 md:block">
            <IconSearch className="text-muted-foreground absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2" />
            <input
              type="search"
              placeholder={t("search")}
              className="bg-muted/50 placeholder:text-muted-foreground focus:bg-background focus:ring-primary/20 h-9 w-full rounded-lg border pr-4 pl-10 text-sm focus:ring-2 focus:outline-none"
            />
          </div>

          <div className="ml-auto flex items-center gap-2">
            {/* Help button */}
            <Button variant="ghost" size="icon" className="text-muted-foreground">
              <IconHelpCircle className="h-5 w-5" />
            </Button>

            {/* Theme toggle */}
            {mounted && (
              <Button
                variant="ghost"
                size="icon"
                className="text-muted-foreground"
                onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              >
                {theme === "dark" ? (
                  <IconSun className="h-5 w-5" />
                ) : (
                  <IconMoon className="h-5 w-5" />
                )}
              </Button>
            )}

            {/* Notifications */}
            <DropdownMenu>
              <DropdownMenuTrigger>
                <div className="text-muted-foreground hover:bg-muted relative inline-flex h-9 w-9 cursor-pointer items-center justify-center rounded-md">
                  <IconBell className="h-5 w-5" />
                  <span className="bg-accent text-accent-foreground absolute -top-0.5 -right-0.5 flex h-4 w-4 items-center justify-center rounded-full text-[10px] font-medium">
                    3
                  </span>
                </div>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-80">
                <DropdownMenuLabel className="flex items-center justify-between">
                  {tNav("notifications")}
                  <Button variant="ghost" size="sm" className="text-primary h-auto p-1 text-xs">
                    Tout marquer comme lu
                  </Button>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <div className="max-h-72 overflow-auto">
                  {[1, 2, 3].map((i) => (
                    <DropdownMenuItem key={i} className="flex flex-col items-start gap-1 p-3">
                      <p className="text-sm font-medium">Nouvelle affectation</p>
                      <p className="text-muted-foreground text-xs">
                        Vous êtes affecté au service de dimanche
                      </p>
                      <p className="text-muted-foreground text-xs">
                        Il y a {i} heure{i > 1 ? "s" : ""}
                      </p>
                    </DropdownMenuItem>
                  ))}
                </div>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 p-4 lg:p-6">{children}</main>

        {/* Footer */}
        <footer className="bg-background/50 border-t px-4 py-3">
          <p className="text-muted-foreground text-center text-xs">
            © {new Date().getFullYear()} Mon Service. Tous droits réservés.
          </p>
        </footer>
      </SidebarInset>
    </SidebarProvider>
  );
}
