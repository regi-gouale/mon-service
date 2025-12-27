/**
 * Dashboard Layout
 * Main layout for authenticated dashboard pages
 */

"use client";

import { ROUTES } from "@/lib/constants";
import { useAuthStore } from "@/stores/auth";
import { useRouter } from "next/navigation";
import { ReactNode, useEffect } from "react";

interface DashboardLayoutProps {
  children: ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuthStore();

  // Protect dashboard routes
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push(ROUTES.LOGIN);
    }
  }, [isAuthenticated, isLoading, router]);

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="border-primary mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-b-2"></div>
          <p className="text-gray-600 dark:text-gray-400">Chargement...</p>
        </div>
      </div>
    );
  }

  // Don't render dashboard if not authenticated
  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
                Church Team Management
              </h1>
            </div>

            <nav className="flex items-center space-x-4">
              <button className="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white">
                <span className="sr-only">Notifications</span>
                🔔
              </button>
              <button className="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white">
                <span className="sr-only">Profil</span>
                👤
              </button>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">{children}</main>

      {/* Footer */}
      <footer className="mt-auto border-t border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-gray-600 dark:text-gray-400">
            © 2025 Church Team Management. Tous droits réservés.
          </p>
        </div>
      </footer>
    </div>
  );
}
