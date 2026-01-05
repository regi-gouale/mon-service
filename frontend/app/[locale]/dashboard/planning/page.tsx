/**
 * Planning Page
 * Service planning view inspired by Planning Center's approach
 */

"use client";

import { PlanningList, ServiceMatrix } from "@/components/planning";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  IconCalendar,
  IconChevronDown,
  IconFilter,
  IconLayoutGrid,
  IconLayoutList,
  IconPlus,
  IconSearch,
} from "@tabler/icons-react";
import { useTranslations } from "next-intl";
import { useState } from "react";

export default function PlanningPage() {
  const t = useTranslations("Planning");
  const [view, setView] = useState<"list" | "matrix">("list");
  const [filter, setFilter] = useState<"all" | "upcoming" | "draft">("upcoming");

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-foreground text-2xl font-bold md:text-3xl">{t("title")}</h1>
          <p className="text-muted-foreground mt-1">
            Gérez et organisez les plannings de services de votre église
          </p>
        </div>
        <Button className="gap-2">
          <IconPlus className="h-4 w-4" />
          Nouveau planning
        </Button>
      </div>

      {/* Filters and View Toggle */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-wrap items-center gap-2">
          {/* Filter dropdown */}
          <DropdownMenu>
            <DropdownMenuTrigger>
              <Button variant="outline" className="gap-2" render={<div />}>
                <IconFilter className="h-4 w-4" />
                {filter === "all" && "Tous les plannings"}
                {filter === "upcoming" && "À venir"}
                {filter === "draft" && "Brouillons"}
                <IconChevronDown className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuItem onClick={() => setFilter("all")}>
                Tous les plannings
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setFilter("upcoming")}>À venir</DropdownMenuItem>
              <DropdownMenuItem onClick={() => setFilter("draft")}>Brouillons</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Date filter */}
          <Button variant="outline" className="gap-2">
            <IconCalendar className="h-4 w-4" />
            Janvier 2026
            <IconChevronDown className="h-4 w-4" />
          </Button>

          {/* Search */}
          <div className="relative">
            <IconSearch className="text-muted-foreground absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2" />
            <input
              type="search"
              placeholder="Rechercher..."
              className="bg-background placeholder:text-muted-foreground focus:ring-primary/20 h-9 w-48 rounded-lg border pr-4 pl-10 text-sm focus:ring-2 focus:outline-none"
            />
          </div>
        </div>

        {/* View toggle */}
        <div className="flex items-center gap-1 rounded-lg border p-1">
          <Button
            variant={view === "list" ? "secondary" : "ghost"}
            size="sm"
            className="gap-2"
            onClick={() => setView("list")}
          >
            <IconLayoutList className="h-4 w-4" />
            Liste
          </Button>
          <Button
            variant={view === "matrix" ? "secondary" : "ghost"}
            size="sm"
            className="gap-2"
            onClick={() => setView("matrix")}
          >
            <IconLayoutGrid className="h-4 w-4" />
            Matrice
          </Button>
        </div>
      </div>

      {/* Quick stats */}
      <div className="grid gap-4 sm:grid-cols-4">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted-foreground text-sm">Ce mois</p>
              <p className="text-2xl font-bold">8</p>
            </div>
            <Badge variant="secondary">Services</Badge>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted-foreground text-sm">Publiés</p>
              <p className="text-success text-2xl font-bold">6</p>
            </div>
            <Badge className="bg-success/10 text-success">{t("published")}</Badge>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted-foreground text-sm">Brouillons</p>
              <p className="text-warning text-2xl font-bold">2</p>
            </div>
            <Badge className="bg-warning/10 text-warning">{t("draft")}</Badge>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted-foreground text-sm">Conflits</p>
              <p className="text-destructive text-2xl font-bold">1</p>
            </div>
            <Badge variant="destructive">{t("conflicts")}</Badge>
          </div>
        </Card>
      </div>

      {/* Content */}
      {view === "list" ? <PlanningList /> : <ServiceMatrix />}
    </div>
  );
}
