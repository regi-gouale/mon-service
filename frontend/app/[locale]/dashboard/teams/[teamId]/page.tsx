/**
 * Team Detail Page
 * Detailed view of a single team with member management
 */

"use client";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { mockTeams, type MockTeamMember } from "@/lib/mock-data";
import {
  IconArrowLeft,
  IconDots,
  IconEdit,
  IconLoader2,
  IconMail,
  IconPhone,
  IconPlus,
  IconSearch,
  IconSettings,
  IconTrash,
  IconUser,
  IconUserPlus,
  IconUsers,
} from "@tabler/icons-react";
import { useTranslations } from "next-intl";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

export default function TeamDetailPage() {
  const t = useTranslations("Team");
  const tCommon = useTranslations("Common");
  const params = useParams();
  const teamId = params.teamId as string;

  // Find the team from mock data
  const team = mockTeams.find((t) => t.id === teamId) || mockTeams[0];

  const [searchQuery, setSearchQuery] = useState("");
  const [selectedMember, setSelectedMember] = useState<MockTeamMember | null>(null);
  const [isInviteOpen, setIsInviteOpen] = useState(false);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState("");
  const [isInviting, setIsInviting] = useState(false);

  const filteredMembers = team.members.filter(
    (member) =>
      member.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      member.role.toLowerCase().includes(searchQuery.toLowerCase()) ||
      member.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleInvite = async () => {
    if (!inviteEmail || !inviteRole) {
      toast.error("Veuillez remplir tous les champs");
      return;
    }

    setIsInviting(true);
    await new Promise((resolve) => setTimeout(resolve, 1000));
    setIsInviting(false);
    setIsInviteOpen(false);
    setInviteEmail("");
    setInviteRole("");
    toast.success(t("inviteSuccess"));
  };

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const handleRemoveMember = (memberId: string) => {
    toast.success("Membre retiré de l'équipe");
  };

  const getStatusBadge = (status: MockTeamMember["status"]) => {
    switch (status) {
      case "active":
        return <Badge className="bg-green-500/10 text-green-600">Actif</Badge>;
      case "away":
        return <Badge variant="secondary">Absent</Badge>;
      case "inactive":
        return <Badge variant="outline">Inactif</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/dashboard/teams">
          <Button variant="ghost" size="icon">
            <IconArrowLeft className="h-5 w-5" />
          </Button>
        </Link>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <div
              className={`flex h-12 w-12 items-center justify-center rounded-xl bg-${team.color}/10`}
            >
              <IconUsers className={`h-6 w-6 text-${team.color}`} />
            </div>
            <div>
              <h1 className="text-foreground text-2xl font-bold">{team.name}</h1>
              <p className="text-muted-foreground">{team.description}</p>
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="icon">
            <IconSettings className="h-4 w-4" />
          </Button>
          <Button onClick={() => setIsInviteOpen(true)}>
            <IconUserPlus className="mr-2 h-4 w-4" />
            {t("inviteMember")}
          </Button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Members List */}
        <div className="space-y-4 lg:col-span-2">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>{t("members")}</CardTitle>
                  <CardDescription>{team.members.length} membres dans cette équipe</CardDescription>
                </div>
              </div>

              {/* Search */}
              <div className="relative mt-4">
                <IconSearch className="text-muted-foreground absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2" />
                <Input
                  placeholder="Rechercher un membre..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </CardHeader>
            <CardContent className="p-0">
              <div className="divide-y">
                {filteredMembers.map((member) => (
                  <div
                    key={member.id}
                    className="hover:bg-muted/50 flex cursor-pointer items-center gap-4 p-4 transition-colors"
                    onClick={() => setSelectedMember(member)}
                  >
                    <Avatar className="h-12 w-12">
                      <AvatarImage src={member.avatar || undefined} />
                      <AvatarFallback>
                        {member.name
                          .split(" ")
                          .map((n) => n[0])
                          .join("")}
                      </AvatarFallback>
                    </Avatar>
                    <div className="min-w-0 flex-1">
                      <p className="text-foreground font-medium">{member.name}</p>
                      <p className="text-muted-foreground text-sm">{member.role}</p>
                    </div>
                    <div className="flex items-center gap-3">
                      {getStatusBadge(member.status)}
                      <DropdownMenu>
                        <DropdownMenuTrigger onClick={(e) => e.stopPropagation()}>
                          <Button variant="ghost" size="icon" render={<div />}>
                            <IconDots className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => setSelectedMember(member)}>
                            <IconUser className="mr-2 h-4 w-4" />
                            Voir le profil
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <IconEdit className="mr-2 h-4 w-4" />
                            Modifier le rôle
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem
                            className="text-destructive"
                            onClick={() => handleRemoveMember(member.id)}
                          >
                            <IconTrash className="mr-2 h-4 w-4" />
                            {t("removeMember")}
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </div>
                ))}

                {filteredMembers.length === 0 && (
                  <div className="flex flex-col items-center justify-center py-12">
                    <IconUsers className="text-muted-foreground mb-4 h-12 w-12" />
                    <p className="text-muted-foreground">Aucun membre trouvé</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Team Info Sidebar */}
        <div className="space-y-4">
          {/* Positions */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Positions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {team.positions.map((position) => (
                  <Badge key={position} variant="secondary">
                    {position}
                  </Badge>
                ))}
                <Button variant="outline" size="sm" className="h-6 gap-1 px-2 text-xs">
                  <IconPlus className="h-3 w-3" />
                  Ajouter
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Quick Stats */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Statistiques</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground text-sm">Membres actifs</span>
                <span className="font-medium">
                  {team.members.filter((m) => m.status === "active").length}
                </span>
              </div>
              <Separator />
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground text-sm">Membres absents</span>
                <span className="font-medium">
                  {team.members.filter((m) => m.status === "away").length}
                </span>
              </div>
              <Separator />
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground text-sm">Positions</span>
                <span className="font-medium">{team.positions.length}</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Member Detail Sheet */}
      <Sheet open={!!selectedMember} onOpenChange={() => setSelectedMember(null)}>
        <SheetContent>
          {selectedMember && (
            <>
              <SheetHeader>
                <SheetTitle>Profil du membre</SheetTitle>
                <SheetDescription>
                  Informations détaillées sur {selectedMember.name}
                </SheetDescription>
              </SheetHeader>
              <div className="mt-6 space-y-6">
                {/* Avatar & Name */}
                <div className="flex flex-col items-center text-center">
                  <Avatar className="h-20 w-20">
                    <AvatarImage src={selectedMember.avatar || undefined} />
                    <AvatarFallback className="text-2xl">
                      {selectedMember.name
                        .split(" ")
                        .map((n) => n[0])
                        .join("")}
                    </AvatarFallback>
                  </Avatar>
                  <h3 className="text-foreground mt-4 text-xl font-semibold">
                    {selectedMember.name}
                  </h3>
                  <p className="text-muted-foreground">{selectedMember.role}</p>
                  <div className="mt-2">{getStatusBadge(selectedMember.status)}</div>
                </div>

                <Separator />

                {/* Contact Info */}
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <IconMail className="text-muted-foreground h-4 w-4" />
                    <span className="text-sm">{selectedMember.email}</span>
                  </div>
                  {selectedMember.phone && (
                    <div className="flex items-center gap-3">
                      <IconPhone className="text-muted-foreground h-4 w-4" />
                      <span className="text-sm">{selectedMember.phone}</span>
                    </div>
                  )}
                </div>

                <Separator />

                {/* Skills */}
                {selectedMember.skills && selectedMember.skills.length > 0 && (
                  <div>
                    <h4 className="text-foreground mb-2 text-sm font-medium">{t("skills")}</h4>
                    <div className="flex flex-wrap gap-2">
                      {selectedMember.skills.map((skill) => (
                        <Badge key={skill} variant="outline">
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {/* Joined Date */}
                <div>
                  <h4 className="text-foreground mb-1 text-sm font-medium">Membre depuis</h4>
                  <p className="text-muted-foreground text-sm">
                    {new Date(selectedMember.joinedAt).toLocaleDateString("fr-FR", {
                      day: "numeric",
                      month: "long",
                      year: "numeric",
                    })}
                  </p>
                </div>

                {/* Actions */}
                <div className="flex gap-2 pt-4">
                  <Button
                    variant="outline"
                    className="flex-1"
                    onClick={() => setSelectedMember(null)}
                  >
                    Fermer
                  </Button>
                  <Button variant="destructive" className="flex-1">
                    <IconTrash className="mr-2 h-4 w-4" />
                    Retirer
                  </Button>
                </div>
              </div>
            </>
          )}
        </SheetContent>
      </Sheet>

      {/* Invite Member Sheet */}
      <Sheet open={isInviteOpen} onOpenChange={setIsInviteOpen}>
        <SheetContent>
          <SheetHeader>
            <SheetTitle>{t("inviteMember")}</SheetTitle>
            <SheetDescription>
              Invitez un nouveau membre à rejoindre l&apos;équipe {team.name}
            </SheetDescription>
          </SheetHeader>
          <div className="mt-6 space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="membre@exemple.com"
                value={inviteEmail}
                onChange={(e) => setInviteEmail(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="role">{t("role")}</Label>
              <Select value={inviteRole} onValueChange={(val) => val && setInviteRole(val)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {team.positions.map((position) => (
                    <SelectItem key={position} value={position}>
                      {position}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex gap-2 pt-4">
              <Button variant="outline" className="flex-1" onClick={() => setIsInviteOpen(false)}>
                {tCommon("cancel")}
              </Button>
              <Button className="flex-1" onClick={handleInvite} disabled={isInviting}>
                {isInviting ? (
                  <IconLoader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <IconMail className="mr-2 h-4 w-4" />
                )}
                {t("invite")}
              </Button>
            </div>
          </div>
        </SheetContent>
      </Sheet>
    </div>
  );
}
