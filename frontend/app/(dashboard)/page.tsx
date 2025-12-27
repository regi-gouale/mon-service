/**
 * Dashboard Home Page
 * Main dashboard view showing overview and quick actions
 */

"use client";

import { useAuthStore } from "@/stores/auth";

export default function DashboardPage() {
  const { user } = useAuthStore();

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="rounded-lg bg-white p-6 shadow dark:bg-gray-800">
        <h2 className="mb-2 text-2xl font-bold text-gray-900 dark:text-white">
          Bienvenue, {user?.firstName} {user?.lastName} 👋
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Voici un aperçu de vos prochaines activités et tâches importantes.
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        <div className="rounded-lg bg-white p-6 shadow dark:bg-gray-800">
          <div className="flex items-center justify-between">
            <div>
              <p className="mb-1 text-sm text-gray-600 dark:text-gray-400">Prochains services</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">3</p>
            </div>
            <div className="text-4xl">📅</div>
          </div>
        </div>

        <div className="rounded-lg bg-white p-6 shadow dark:bg-gray-800">
          <div className="flex items-center justify-between">
            <div>
              <p className="mb-1 text-sm text-gray-600 dark:text-gray-400">Notifications</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">5</p>
            </div>
            <div className="text-4xl">🔔</div>
          </div>
        </div>

        <div className="rounded-lg bg-white p-6 shadow dark:bg-gray-800">
          <div className="flex items-center justify-between">
            <div>
              <p className="mb-1 text-sm text-gray-600 dark:text-gray-400">Membres d&apos;équipe</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">12</p>
            </div>
            <div className="text-4xl">👥</div>
          </div>
        </div>
      </div>

      {/* Upcoming Services */}
      <div className="rounded-lg bg-white shadow dark:bg-gray-800">
        <div className="border-b border-gray-200 p-6 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Prochains services
          </h3>
        </div>
        <div className="p-6">
          <p className="py-8 text-center text-gray-600 dark:text-gray-400">
            Aucun service à venir pour le moment
          </p>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="rounded-lg bg-white p-6 shadow dark:bg-gray-800">
        <h3 className="mb-4 text-lg font-semibold text-gray-900 dark:text-white">
          Actions rapides
        </h3>
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          <button className="rounded-lg border border-gray-200 p-4 transition-colors hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-700">
            <div className="mb-2 text-2xl">📆</div>
            <p className="text-sm font-medium text-gray-900 dark:text-white">Disponibilités</p>
          </button>
          <button className="rounded-lg border border-gray-200 p-4 transition-colors hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-700">
            <div className="mb-2 text-2xl">📋</div>
            <p className="text-sm font-medium text-gray-900 dark:text-white">Planning</p>
          </button>
          <button className="rounded-lg border border-gray-200 p-4 transition-colors hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-700">
            <div className="mb-2 text-2xl">👥</div>
            <p className="text-sm font-medium text-gray-900 dark:text-white">Équipe</p>
          </button>
          <button className="rounded-lg border border-gray-200 p-4 transition-colors hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-700">
            <div className="mb-2 text-2xl">⚙️</div>
            <p className="text-sm font-medium text-gray-900 dark:text-white">Paramètres</p>
          </button>
        </div>
      </div>
    </div>
  );
}
