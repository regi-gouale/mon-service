/**
 * Teams Page
 * Team management view inspired by Planning Center's team organization
 */

"use client";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  IconChevronRight,
  IconDots,
  IconMail,
  IconPlus,
  IconSearch,
  IconUser,
  IconUserPlus,
  IconUsers,
} from "@tabler/icons-react";
import { useTranslations } from "next-intl";

// Mock data for teams
const mockTeams = [
  {
    id: "t1",
    name: "Louange",
    description: "Équipe de louange et worship",
    color: "primary",
    members: [
      { id: "m1", name: "Marie Dupont", role: "Leader", avatar: null, status: "active" },
      { id: "m2", name: "Pierre Martin", role: "Chant", avatar: null, status: "active" },
      { id: "m3", name: "Sophie Bernard", role: "Piano", avatar: null, status: "active" },
      { id: "m4", name: "Lucas Tremblay", role: "Guitare", avatar: null, status: "away" },
    ],
    positions: ["Leader", "Chant", "Piano", "Guitare", "Batterie", "Basse"],
  },
  {
    id: "t2",
    name: "Technique",
    description: "Son, lumières et vidéo",
    color: "accent",
    members: [
      { id: "m5", name: "Emma Leroy", role: "Responsable", avatar: null, status: "active" },
      { id: "m6", name: "Hugo Bernard", role: "Son", avatar: null, status: "active" },
      { id: "m7", name: "Léa Martin", role: "Vidéo", avatar: null, status: "active" },
    ],
    positions: ["Responsable", "Son", "Vidéo", "Lumières", "Streaming"],
  },
  {
    id: "t3",
    name: "Accueil",
    description: "Accueil et hospitalité",
    color: "success",
    members: [
      { id: "m8", name: "Julie Moreau", role: "Responsable", avatar: null, status: "active" },
      { id: "m9", name: "Thomas Petit", role: "Accueil", avatar: null, status: "active" },
      { id: "m10", name: "Clara Roux", role: "Accueil", avatar: null, status: "active" },
      { id: "m11", name: "Antoine Dubois", role: "Accueil", avatar: null, status: "away" },
      { id: "m12", name: "Marine Robert", role: "Accueil", avatar: null, status: "active" },
    ],
    positions: ["Responsable", "Accueil", "Parking"],
  },
  {
    id: "t4",
    name: "Enfants",
    description: "Ministère des enfants",
    color: "warning",
    members: [
      { id: "m13", name: "Céline Richard", role: "Responsable", avatar: null, status: "active" },
      { id: "m14", name: "François Simon", role: "Animateur", avatar: null, status: "active" },
    ],
    positions: ["Responsable", "Animateur", "Assistant"],
  },
];

export default function TeamsPage() {
  const t = useTranslations("Team");
  const tNav = useTranslations("Navigation");

  const totalMembers = mockTeams.reduce((acc, team) => acc + team.members.length, 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-foreground text-2xl font-bold md:text-3xl">{tNav("teams")}</h1>
          <p className="text-muted-foreground mt-1">
            Gérez vos équipes et les membres de votre organisation
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="gap-2">
            <IconUserPlus className="h-4 w-4" />
            {t("inviteMember")}
          </Button>
          <Button className="gap-2">
            <IconPlus className="h-4 w-4" />
            Nouvelle équipe
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid gap-4 sm:grid-cols-3">
        <Card className="p-5">
          <div className="flex items-center gap-4">
            <div className="bg-primary/10 flex h-12 w-12 items-center justify-center rounded-xl">
              <IconUsers className="text-primary h-6 w-6" />
            </div>
            <div>
              <p className="text-muted-foreground text-sm">Total équipes</p>
              <p className="text-foreground text-2xl font-bold">{mockTeams.length}</p>
            </div>
          </div>
        </Card>
        <Card className="p-5">
          <div className="flex items-center gap-4">
            <div className="bg-success/10 flex h-12 w-12 items-center justify-center rounded-xl">
              <IconUser className="text-success h-6 w-6" />
            </div>
            <div>
              <p className="text-muted-foreground text-sm">Total membres</p>
              <p className="text-foreground text-2xl font-bold">{totalMembers}</p>
            </div>
          </div>
        </Card>
        <Card className="p-5">
          <div className="flex items-center gap-4">
            <div className="bg-warning/10 flex h-12 w-12 items-center justify-center rounded-xl">
              <IconMail className="text-warning h-6 w-6" />
            </div>
            <div>
              <p className="text-muted-foreground text-sm">Invitations en attente</p>
              <p className="text-foreground text-2xl font-bold">2</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Search */}
      <div className="relative max-w-md">
        <IconSearch className="text-muted-foreground absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2" />
        <input
          type="search"
          placeholder="Rechercher une équipe ou un membre..."
          className="bg-background placeholder:text-muted-foreground focus:ring-primary/20 h-10 w-full rounded-lg border pr-4 pl-10 text-sm focus:ring-2 focus:outline-none"
        />
      </div>

      {/* Teams Grid */}
      <div className="grid gap-6 lg:grid-cols-2">
        {mockTeams.map((team) => (
          <Card key={team.id} className="overflow-hidden">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div
                    className={`flex h-10 w-10 items-center justify-center rounded-lg bg-${team.color}/10`}
                  >
                    <IconUsers className={`h-5 w-5 text-${team.color}`} />
                  </div>
                  <div>
                    <CardTitle className="text-lg">{team.name}</CardTitle>
                    <p className="text-muted-foreground text-sm">{team.description}</p>
                  </div>
                </div>
                <DropdownMenu>
                  <DropdownMenuTrigger>
                    <Button variant="ghost" size="icon" render={<div />}>
                      <IconDots className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem>Modifier l&apos;équipe</DropdownMenuItem>
                    <DropdownMenuItem>Gérer les positions</DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem className="text-destructive">
                      Supprimer l&apos;équipe
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </CardHeader>
            <CardContent>
              {/* Positions */}
              <div className="mb-4 flex flex-wrap gap-1.5">
                {team.positions.map((position) => (
                  <Badge key={position} variant="outline" className="text-xs">
                    {position}
                  </Badge>
                ))}
              </div>

              {/* Members */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">
                    {t("members")} ({team.members.length})
                  </span>
                  <Button variant="ghost" size="sm" className="text-primary h-auto p-0">
                    Voir tout
                    <IconChevronRight className="ml-1 h-3 w-3" />
                  </Button>
                </div>

                <div className="flex flex-wrap gap-2">
                  {team.members.slice(0, 5).map((member) => (
                    <div
                      key={member.id}
                      className="group bg-muted/30 hover:bg-muted relative flex items-center gap-2 rounded-lg border px-3 py-2 transition-colors"
                    >
                      <Avatar className="h-8 w-8">
                        <AvatarImage src={member.avatar || undefined} />
                        <AvatarFallback className="text-xs">
                          {member.name
                            .split(" ")
                            .map((n) => n[0])
                            .join("")}
                        </AvatarFallback>
                      </Avatar>
                      <div className="min-w-0">
                        <p className="text-foreground truncate text-sm font-medium">
                          {member.name}
                        </p>
                        <p className="text-muted-foreground text-xs">{member.role}</p>
                      </div>
                      {member.status === "away" && (
                        <Badge variant="secondary" className="ml-auto text-xs">
                          Absent
                        </Badge>
                      )}
                    </div>
                  ))}
                  {team.members.length > 5 && (
                    <div className="text-muted-foreground flex items-center justify-center rounded-lg border border-dashed px-4 py-2 text-sm">
                      +{team.members.length - 5} autres
                    </div>
                  )}
                </div>
              </div>

              {/* Add member button */}
              <Button variant="outline" className="mt-4 w-full gap-2" size="sm">
                <IconUserPlus className="h-4 w-4" />
                Ajouter un membre
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
