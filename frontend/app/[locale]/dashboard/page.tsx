/**
 * Dashboard Home Page
 * Main dashboard view showing overview and quick actions
 */

"use client";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useAuthStore } from "@/stores/auth";
import {
  IconBell,
  IconCalendar,
  IconCalendarEvent,
  IconClipboardList,
  IconSettings,
  IconUsers,
} from "@tabler/icons-react";
import { useTranslations } from "next-intl";
import Link from "next/link";

export default function DashboardPage() {
  const t = useTranslations("Dashboard");
  const tNav = useTranslations("Navigation");
  const { user } = useAuthStore();

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <Card className="p-6">
        <h2 className="text-foreground mb-2 text-2xl font-bold">
          {t("welcome", { name: `${user?.firstName} ${user?.lastName}` })}
        </h2>
        <p className="text-muted-foreground">
          Voici un aperçu de vos prochaines activités et tâches importantes.
        </p>
      </Card>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted-foreground mb-1 text-sm">{t("upcomingServices")}</p>
              <p className="text-foreground text-3xl font-bold">3</p>
            </div>
            <div className="bg-primary/10 rounded-full p-3">
              <IconCalendarEvent className="text-primary h-6 w-6" />
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted-foreground mb-1 text-sm">{tNav("notifications")}</p>
              <p className="text-foreground text-3xl font-bold">5</p>
            </div>
            <div className="rounded-full bg-orange-500/10 p-3">
              <IconBell className="h-6 w-6 text-orange-500" />
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted-foreground mb-1 text-sm">{tNav("team")}</p>
              <p className="text-foreground text-3xl font-bold">12</p>
            </div>
            <div className="rounded-full bg-green-500/10 p-3">
              <IconUsers className="h-6 w-6 text-green-500" />
            </div>
          </div>
        </Card>
      </div>

      {/* Upcoming Services */}
      <Card>
        <div className="border-b p-6">
          <h3 className="text-foreground text-lg font-semibold">{t("upcomingServices")}</h3>
        </div>
        <div className="p-6">
          <p className="text-muted-foreground py-8 text-center">{t("noUpcomingServices")}</p>
        </div>
      </Card>

      {/* Quick Actions */}
      <Card className="p-6">
        <h3 className="text-foreground mb-4 text-lg font-semibold">{t("quickActions")}</h3>
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          <Button
            variant="outline"
            className="flex h-auto flex-col gap-2 py-6"
            aria-label={tNav("availability")}
            render={<Link href="/dashboard/availability" />}
            nativeButton={false}
          >
            <IconCalendar className="h-6 w-6" />
            <span className="text-sm font-medium">{tNav("availability")}</span>
          </Button>
          <Button
            variant="outline"
            className="flex h-auto flex-col gap-2 py-6"
            aria-label={tNav("planning")}
            render={<Link href="/dashboard/planning" />}
            nativeButton={false}
          >
            <IconClipboardList className="h-6 w-6" />
            <span className="text-sm font-medium">{tNav("planning")}</span>
          </Button>
          <Button
            variant="outline"
            className="flex h-auto flex-col gap-2 py-6"
            aria-label={tNav("team")}
            render={<Link href="/dashboard/team" />}
            nativeButton={false}
          >
            <IconUsers className="h-6 w-6" />
            <span className="text-sm font-medium">{tNav("team")}</span>
          </Button>
          <Button
            variant="outline"
            className="flex h-auto flex-col gap-2 py-6"
            aria-label={tNav("settings")}
            render={<Link href="/dashboard/settings" />}
            nativeButton={false}
          >
            <IconSettings className="h-6 w-6" />
            <span className="text-sm font-medium">{tNav("settings")}</span>
          </Button>
        </div>
      </Card>
    </div>
  );
}
