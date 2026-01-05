"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  IconCheck,
  IconChevronLeft,
  IconChevronRight,
  IconClock,
  IconDots,
  IconUser,
  IconX,
} from "@tabler/icons-react";
import { useTranslations } from "next-intl";
import { useState } from "react";

interface ServicePlan {
  id: string;
  date: Date;
  name: string;
  time: string;
  teams: TeamAssignment[];
  status: "draft" | "published";
}

interface TeamAssignment {
  id: string;
  name: string;
  positions: Position[];
}

interface Position {
  id: string;
  name: string;
  assignee?: {
    id: string;
    name: string;
    avatar?: string;
  };
  status: "confirmed" | "pending" | "declined" | "empty";
}

// Mock data
const mockServices: ServicePlan[] = [
  {
    id: "1",
    date: new Date("2026-01-11"),
    name: "Culte du dimanche",
    time: "10:00",
    status: "published",
    teams: [
      {
        id: "t1",
        name: "Louange",
        positions: [
          {
            id: "p1",
            name: "Leader",
            assignee: { id: "u1", name: "Marie D." },
            status: "confirmed",
          },
          { id: "p2", name: "Chant", assignee: { id: "u2", name: "Pierre M." }, status: "pending" },
          {
            id: "p3",
            name: "Piano",
            assignee: { id: "u3", name: "Sophie B." },
            status: "confirmed",
          },
          { id: "p4", name: "Guitare", status: "empty" },
        ],
      },
      {
        id: "t2",
        name: "Technique",
        positions: [
          { id: "p5", name: "Son", assignee: { id: "u4", name: "Lucas T." }, status: "confirmed" },
          { id: "p6", name: "Vidéo", assignee: { id: "u5", name: "Emma L." }, status: "declined" },
        ],
      },
    ],
  },
  {
    id: "2",
    date: new Date("2026-01-11"),
    name: "Culte du soir",
    time: "18:00",
    status: "draft",
    teams: [
      {
        id: "t3",
        name: "Louange",
        positions: [
          { id: "p7", name: "Leader", assignee: { id: "u6", name: "Jean D." }, status: "pending" },
          { id: "p8", name: "Chant", status: "empty" },
        ],
      },
    ],
  },
];

export function ServicePlanCard({ service }: { service: ServicePlan }) {
  const t = useTranslations("Planning");

  const getStatusIcon = (status: Position["status"]) => {
    switch (status) {
      case "confirmed":
        return <IconCheck className="text-success h-3 w-3" />;
      case "pending":
        return <IconClock className="text-warning h-3 w-3" />;
      case "declined":
        return <IconX className="text-destructive h-3 w-3" />;
      default:
        return <IconUser className="text-muted-foreground h-3 w-3" />;
    }
  };

  const getStatusBg = (status: Position["status"]) => {
    switch (status) {
      case "confirmed":
        return "bg-success/10 border-success/30";
      case "pending":
        return "bg-warning/10 border-warning/30";
      case "declined":
        return "bg-destructive/10 border-destructive/30";
      default:
        return "bg-muted border-dashed";
    }
  };

  return (
    <div className="bg-card rounded-xl border shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between border-b p-4">
        <div className="flex items-center gap-3">
          <div className="bg-primary/10 flex flex-col items-center justify-center rounded-lg px-3 py-2">
            <span className="text-primary text-xs font-medium uppercase">
              {service.date.toLocaleDateString("fr-FR", { weekday: "short" })}
            </span>
            <span className="text-foreground text-xl font-bold">{service.date.getDate()}</span>
          </div>
          <div>
            <h3 className="text-foreground font-semibold">{service.name}</h3>
            <p className="text-muted-foreground text-sm">{service.time}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={service.status === "published" ? "default" : "secondary"}>
            {service.status === "published" ? t("published") : t("draft")}
          </Badge>
          <Button variant="ghost" size="icon">
            <IconDots className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Teams */}
      <div className="divide-y">
        {service.teams.map((team) => (
          <div key={team.id} className="p-4">
            <h4 className="text-muted-foreground mb-3 text-sm font-medium">{team.name}</h4>
            <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
              {team.positions.map((position) => (
                <div
                  key={position.id}
                  className={`flex items-center gap-2 rounded-lg border p-2 ${getStatusBg(
                    position.status
                  )}`}
                >
                  <div
                    className={`flex h-8 w-8 items-center justify-center rounded-full ${
                      position.assignee ? "bg-primary/10" : "bg-muted"
                    }`}
                  >
                    {position.assignee ? (
                      <span className="text-primary text-xs font-medium">
                        {position.assignee.name
                          .split(" ")
                          .map((n) => n[0])
                          .join("")}
                      </span>
                    ) : (
                      <IconUser className="text-muted-foreground h-4 w-4" />
                    )}
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-muted-foreground text-xs">{position.name}</p>
                    <p className="text-foreground truncate text-sm font-medium">
                      {position.assignee?.name || "Non assigné"}
                    </p>
                  </div>
                  {getStatusIcon(position.status)}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function ServiceMatrix() {
  const [currentWeek, setCurrentWeek] = useState(new Date());

  // Generate week dates
  const getWeekDates = (date: Date) => {
    const start = new Date(date);
    start.setDate(start.getDate() - start.getDay());
    return Array.from({ length: 7 }, (_, i) => {
      const d = new Date(start);
      d.setDate(start.getDate() + i);
      return d;
    });
  };

  const weekDates = getWeekDates(currentWeek);

  const prevWeek = () => {
    const newDate = new Date(currentWeek);
    newDate.setDate(newDate.getDate() - 7);
    setCurrentWeek(newDate);
  };

  const nextWeek = () => {
    const newDate = new Date(currentWeek);
    newDate.setDate(newDate.getDate() + 7);
    setCurrentWeek(newDate);
  };

  // Mock teams
  const teams = [
    { id: "t1", name: "Louange" },
    { id: "t2", name: "Technique" },
    { id: "t3", name: "Accueil" },
    { id: "t4", name: "Enfants" },
  ];

  // Mock assignments (teamId -> date -> count)
  const assignments: Record<string, Record<string, number>> = {
    t1: { "2026-01-11": 4, "2026-01-18": 3 },
    t2: { "2026-01-11": 2, "2026-01-18": 2 },
    t3: { "2026-01-11": 5, "2026-01-18": 4 },
    t4: { "2026-01-11": 3 },
  };

  return (
    <div className="bg-card rounded-xl border">
      {/* Header */}
      <div className="flex items-center justify-between border-b p-4">
        <h3 className="text-foreground font-semibold">Vue matricielle</h3>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="icon" onClick={prevWeek}>
            <IconChevronLeft className="h-4 w-4" />
          </Button>
          <span className="text-foreground min-w-32 text-center text-sm font-medium">
            {weekDates[0].toLocaleDateString("fr-FR", { month: "short", day: "numeric" })} -{" "}
            {weekDates[6].toLocaleDateString("fr-FR", { month: "short", day: "numeric" })}
          </span>
          <Button variant="outline" size="icon" onClick={nextWeek}>
            <IconChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Matrix */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b">
              <th className="text-muted-foreground p-3 text-left text-sm font-medium">Équipe</th>
              {weekDates.map((date) => (
                <th
                  key={date.toISOString()}
                  className={`p-3 text-center text-sm font-medium ${
                    date.getDay() === 0 ? "bg-primary/5" : ""
                  }`}
                >
                  <span className="text-muted-foreground">
                    {date.toLocaleDateString("fr-FR", { weekday: "short" })}
                  </span>
                  <br />
                  <span className="text-foreground">{date.getDate()}</span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {teams.map((team) => (
              <tr key={team.id} className="border-b last:border-0">
                <td className="text-foreground p-3 font-medium">{team.name}</td>
                {weekDates.map((date) => {
                  const dateKey = date.toISOString().split("T")[0];
                  const count = assignments[team.id]?.[dateKey];
                  return (
                    <td
                      key={date.toISOString()}
                      className={`p-3 text-center ${date.getDay() === 0 ? "bg-primary/5" : ""}`}
                    >
                      {count ? (
                        <Badge
                          variant="secondary"
                          className="hover:bg-primary hover:text-primary-foreground cursor-pointer"
                        >
                          {count}
                        </Badge>
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function PlanningList() {
  return (
    <div className="space-y-4">
      {mockServices.map((service) => (
        <ServicePlanCard key={service.id} service={service} />
      ))}
    </div>
  );
}
