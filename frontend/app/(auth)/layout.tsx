/**
 * Auth Layout
 * Layout for authentication pages (login, register, etc.)
 */

import { ReactNode } from "react";

interface AuthLayoutProps {
  children: ReactNode;
}

export default function AuthLayout({ children }: AuthLayoutProps) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-linear-to-br from-blue-50 to-indigo-100 p-4 dark:from-gray-900 dark:to-gray-800">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <h1 className="mb-2 text-3xl font-bold text-gray-900 dark:text-white">
            Church Team Management
          </h1>
          <p className="text-gray-600 dark:text-gray-400">Gérez vos équipes et plannings</p>
        </div>

        <div className="rounded-lg bg-white p-8 shadow-xl dark:bg-gray-800">{children}</div>

        <div className="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
          <p>© 2025 Church Team Management. Tous droits réservés.</p>
        </div>
      </div>
    </div>
  );
}
