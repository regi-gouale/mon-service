/**
 * Dashboard Home Page
 * Main dashboard view inspired by Planning Center's clean interface
 */

"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuthStore } from "@/stores/auth";
import {
  IconCalendar,
  IconCalendarEvent,
  IconCheck,
  IconChevronRight,
  IconClock,
  IconPlus,
  IconTrendingUp,
  IconUsers,
} from "@tabler/icons-react";
import { useTranslations } from "next-intl";
import Link from "next/link";

export default function DashboardPage() {
  const t = useTranslations("Dashboard");
  const tNav = useTranslations("Navigation");
  const { user } = useAuthStore();

  // Mock data for upcoming services
  const upcomingServices = [
    {
      id: 1,
      date: "2026-01-11",
      name: "Culte du dimanche",
      time: "10:00",
      teams: ["Louange", "Accueil"],
      confirmed: 8,
      pending: 2,
    },
    {
      id: 2,
      date: "2026-01-11",
      name: "Culte du soir",
      time: "18:00",
      teams: ["Louange", "Technique"],
      confirmed: 5,
      pending: 1,
    },
    {
      id: 3,
      date: "2026-01-18",
      name: "Culte du dimanche",
      time: "10:00",
      teams: ["Louange", "Accueil", "Enfants"],
      confirmed: 12,
      pending: 4,
    },
  ];

  // Mock data for team activity
  const recentActivity = [
    {
      type: "confirmed",
      user: "Marie D.",
      action: "a confirmé sa disponibilité",
      time: "Il y a 2h",
    },
    { type: "declined", user: "Pierre M.", action: "n'est pas disponible", time: "Il y a 3h" },
    {
      type: "confirmed",
      user: "Sophie B.",
      action: "a confirmé sa disponibilité",
      time: "Il y a 5h",
    },
  ];

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-foreground text-2xl font-bold md:text-3xl">
            {t("welcome", { name: user?.firstName || "Utilisateur" })}
          </h1>
          <p className="text-muted-foreground mt-1">
            Voici un aperçu de vos prochaines activités et tâches importantes.
          </p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" render={<Link href="/dashboard/availability" />}>
            <IconCalendar className="mr-2 h-4 w-4" />
            Mes disponibilités
          </Button>
          <Button render={<Link href="/dashboard/planning" />}>
            <IconPlus className="mr-2 h-4 w-4" />
            Nouveau planning
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="border-l-primary border-l-4">
          <CardContent className="p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-muted-foreground text-sm font-medium">{t("upcomingServices")}</p>
                <p className="text-foreground mt-1 text-3xl font-bold">3</p>
                <p className="text-success mt-1 flex items-center text-xs">
                  <IconTrendingUp className="mr-1 h-3 w-3" />
                  Cette semaine
                </p>
              </div>
              <div className="bg-primary/10 flex h-12 w-12 items-center justify-center rounded-xl">
                <IconCalendarEvent className="text-primary h-6 w-6" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-success border-l-4">
          <CardContent className="p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-muted-foreground text-sm font-medium">Confirmations</p>
                <p className="text-foreground mt-1 text-3xl font-bold">25</p>
                <p className="text-muted-foreground mt-1 flex items-center text-xs">
                  <IconCheck className="text-success mr-1 h-3 w-3" />
                  sur 32 demandes
                </p>
              </div>
              <div className="bg-success/10 flex h-12 w-12 items-center justify-center rounded-xl">
                <IconCheck className="text-success h-6 w-6" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-accent border-l-4">
          <CardContent className="p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-muted-foreground text-sm font-medium">Membres actifs</p>
                <p className="text-foreground mt-1 text-3xl font-bold">48</p>
                <p className="text-muted-foreground mt-1 flex items-center text-xs">4 équipes</p>
              </div>
              <div className="bg-accent/10 flex h-12 w-12 items-center justify-center rounded-xl">
                <IconUsers className="text-accent h-6 w-6" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-warning border-l-4">
          <CardContent className="p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-muted-foreground text-sm font-medium">En attente</p>
                <p className="text-foreground mt-1 text-3xl font-bold">7</p>
                <p className="text-warning mt-1 flex items-center text-xs">
                  <IconClock className="mr-1 h-3 w-3" />
                  Réponses à recevoir
                </p>
              </div>
              <div className="bg-warning/10 flex h-12 w-12 items-center justify-center rounded-xl">
                <IconClock className="text-warning h-6 w-6" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Upcoming Services - Takes 2 columns */}
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-lg font-semibold">{t("upcomingServices")}</CardTitle>
            <Button
              variant="ghost"
              size="sm"
              className="text-primary gap-1"
              render={<Link href="/dashboard/planning" />}
            >
              {t("viewAll")}
              <IconChevronRight className="h-4 w-4" />
            </Button>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {upcomingServices.map((service) => (
                <div
                  key={service.id}
                  className="group hover:bg-muted/50 flex items-center gap-4 rounded-lg border p-4 transition-colors"
                >
                  {/* Date column */}
                  <div className="bg-primary/5 flex flex-col items-center justify-center rounded-lg px-3 py-2 text-center">
                    <span className="text-primary text-xs font-medium uppercase">
                      {new Date(service.date).toLocaleDateString("fr-FR", { weekday: "short" })}
                    </span>
                    <span className="text-foreground text-2xl font-bold">
                      {new Date(service.date).getDate()}
                    </span>
                  </div>

                  {/* Service info */}
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <h4 className="text-foreground truncate font-semibold">{service.name}</h4>
                      <Badge variant="secondary" className="shrink-0">
                        {service.time}
                      </Badge>
                    </div>
                    <div className="mt-1 flex flex-wrap gap-1">
                      {service.teams.map((team) => (
                        <Badge key={team} variant="outline" className="text-xs">
                          {team}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  {/* Status */}
                  <div className="hidden shrink-0 items-center gap-4 sm:flex">
                    <div className="text-center">
                      <p className="text-success text-lg font-semibold">{service.confirmed}</p>
                      <p className="text-muted-foreground text-xs">Confirmés</p>
                    </div>
                    <div className="text-center">
                      <p className="text-warning text-lg font-semibold">{service.pending}</p>
                      <p className="text-muted-foreground text-xs">En attente</p>
                    </div>
                  </div>

                  {/* Arrow */}
                  <IconChevronRight className="text-muted-foreground h-5 w-5 opacity-0 transition-opacity group-hover:opacity-100" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg font-semibold">Activité récente</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivity.map((activity, i) => (
                <div key={i} className="flex items-start gap-3">
                  <div
                    className={`mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
                      activity.type === "confirmed"
                        ? "bg-success/10 text-success"
                        : "bg-destructive/10 text-destructive"
                    }`}
                  >
                    {activity.type === "confirmed" ? (
                      <IconCheck className="h-4 w-4" />
                    ) : (
                      <IconClock className="h-4 w-4" />
                    )}
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm">
                      <span className="text-foreground font-medium">{activity.user}</span>{" "}
                      <span className="text-muted-foreground">{activity.action}</span>
                    </p>
                    <p className="text-muted-foreground text-xs">{activity.time}</p>
                  </div>
                </div>
              ))}
            </div>

            <Button variant="outline" className="mt-4 w-full" size="sm">
              Voir toute l&apos;activité
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-lg font-semibold">{t("quickActions")}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {[
              {
                icon: IconCalendar,
                label: tNav("availability"),
                href: "/dashboard/availability",
                color: "primary",
              },
              {
                icon: IconCalendarEvent,
                label: tNav("planning"),
                href: "/dashboard/planning",
                color: "success",
              },
              {
                icon: IconUsers,
                label: tNav("teams"),
                href: "/dashboard/teams",
                color: "accent",
              },
              {
                icon: IconPlus,
                label: "Nouveau service",
                href: "/dashboard/services/new",
                color: "info",
              },
            ].map((action, i) => (
              <Link
                key={i}
                href={action.href}
                className="group hover:border-primary/50 hover:bg-muted/50 flex flex-col items-center gap-3 rounded-xl border p-4 text-center transition-all hover:shadow-sm"
              >
                <div
                  className={`flex h-12 w-12 items-center justify-center rounded-xl bg-${action.color}/10 transition-transform group-hover:scale-110`}
                >
                  <action.icon className={`h-6 w-6 text-${action.color}`} />
                </div>
                <span className="text-foreground text-sm font-medium">{action.label}</span>
              </Link>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
