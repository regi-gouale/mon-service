/**
 * Services Page
 * List and manage church services/events
 */

"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
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
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Textarea } from "@/components/ui/textarea";
import { mockServices, mockTeams, type MockService } from "@/lib/mock-data";
import {
  IconCalendar,
  IconCalendarEvent,
  IconCheck,
  IconChevronDown,
  IconClock,
  IconDots,
  IconEdit,
  IconFilter,
  IconLoader2,
  IconPlus,
  IconSearch,
  IconSend,
  IconTrash,
  IconUsers,
} from "@tabler/icons-react";
import { useTranslations } from "next-intl";
import { useState } from "react";
import { toast } from "sonner";

export default function ServicesPage() {
  const t = useTranslations("Planning");
  const tCommon = useTranslations("Common");

  const [services, setServices] = useState<MockService[]>(mockServices);
  const [filter, setFilter] = useState<"all" | "upcoming" | "draft" | "published">("upcoming");
  const [searchQuery, setSearchQuery] = useState("");
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);

  const [newService, setNewService] = useState({
    name: "",
    date: "",
    time: "",
    endTime: "",
    teams: [] as string[],
    dressCode: "",
    notes: "",
  });

  const filteredServices = services.filter((service) => {
    const matchesSearch = service.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter =
      filter === "all" ||
      (filter === "upcoming" && service.status !== "completed") ||
      (filter === "draft" && service.status === "draft") ||
      (filter === "published" && service.status === "published");
    return matchesSearch && matchesFilter;
  });

  const getStatusBadge = (status: MockService["status"]) => {
    switch (status) {
      case "published":
        return <Badge className="bg-green-500/10 text-green-600">{t("published")}</Badge>;
      case "draft":
        return <Badge variant="secondary">{t("draft")}</Badge>;
      case "completed":
        return <Badge variant="outline">Terminé</Badge>;
    }
  };

  const handleCreateService = async () => {
    if (!newService.name || !newService.date || !newService.time) {
      toast.error("Veuillez remplir tous les champs obligatoires");
      return;
    }

    setIsCreating(true);
    await new Promise((resolve) => setTimeout(resolve, 1000));

    const service: MockService = {
      id: `service-${Date.now()}`,
      ...newService,
      confirmed: 0,
      pending: 0,
      status: "draft",
    };

    setServices((prev) => [service, ...prev]);
    setIsCreating(false);
    setIsCreateOpen(false);
    setNewService({
      name: "",
      date: "",
      time: "",
      endTime: "",
      teams: [],
      dressCode: "",
      notes: "",
    });
    toast.success("Service créé avec succès");
  };

  const handlePublish = (id: string) => {
    setServices((prev) =>
      prev.map((s) => (s.id === id ? { ...s, status: "published" as const } : s))
    );
    toast.success("Service publié");
  };

  const handleDelete = (id: string) => {
    setServices((prev) => prev.filter((s) => s.id !== id));
    toast.success("Service supprimé");
  };

  const stats = {
    total: services.length,
    upcoming: services.filter((s) => s.status !== "completed").length,
    draft: services.filter((s) => s.status === "draft").length,
    published: services.filter((s) => s.status === "published").length,
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-foreground text-2xl font-bold md:text-3xl">Services</h1>
          <p className="text-muted-foreground mt-1">
            Créez et gérez les services et événements de votre église
          </p>
        </div>
        <Button onClick={() => setIsCreateOpen(true)}>
          <IconPlus className="mr-2 h-4 w-4" />
          Nouveau service
        </Button>
      </div>

      {/* Stats */}
      <div className="grid gap-4 sm:grid-cols-4">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted-foreground text-sm">Total</p>
              <p className="text-2xl font-bold">{stats.total}</p>
            </div>
            <IconCalendarEvent className="text-muted-foreground h-8 w-8" />
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted-foreground text-sm">À venir</p>
              <p className="text-primary text-2xl font-bold">{stats.upcoming}</p>
            </div>
            <IconCalendar className="text-primary h-8 w-8" />
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted-foreground text-sm">Publiés</p>
              <p className="text-2xl font-bold text-green-600">{stats.published}</p>
            </div>
            <IconCheck className="h-8 w-8 text-green-600" />
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted-foreground text-sm">Brouillons</p>
              <p className="text-2xl font-bold text-orange-500">{stats.draft}</p>
            </div>
            <IconEdit className="h-8 w-8 text-orange-500" />
          </div>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative max-w-md flex-1">
          <IconSearch className="text-muted-foreground absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2" />
          <Input
            placeholder="Rechercher un service..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger>
            <Button variant="outline" className="gap-2" render={<div />}>
              <IconFilter className="h-4 w-4" />
              {filter === "all" && "Tous"}
              {filter === "upcoming" && "À venir"}
              {filter === "draft" && "Brouillons"}
              {filter === "published" && "Publiés"}
              <IconChevronDown className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            <DropdownMenuItem onClick={() => setFilter("all")}>Tous</DropdownMenuItem>
            <DropdownMenuItem onClick={() => setFilter("upcoming")}>À venir</DropdownMenuItem>
            <DropdownMenuItem onClick={() => setFilter("published")}>Publiés</DropdownMenuItem>
            <DropdownMenuItem onClick={() => setFilter("draft")}>Brouillons</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Services List */}
      <div className="space-y-4">
        {filteredServices.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <IconCalendarEvent className="text-muted-foreground mb-4 h-12 w-12" />
              <p className="text-muted-foreground">Aucun service trouvé</p>
              <Button className="mt-4" onClick={() => setIsCreateOpen(true)}>
                <IconPlus className="mr-2 h-4 w-4" />
                Créer un service
              </Button>
            </CardContent>
          </Card>
        ) : (
          filteredServices.map((service) => (
            <Card key={service.id} className="overflow-hidden">
              <div className="flex items-start gap-4 p-4">
                {/* Date Badge */}
                <div className="bg-primary/10 flex flex-col items-center justify-center rounded-xl px-4 py-3">
                  <span className="text-primary text-xs font-medium uppercase">
                    {new Date(service.date).toLocaleDateString("fr-FR", { weekday: "short" })}
                  </span>
                  <span className="text-foreground text-2xl font-bold">
                    {new Date(service.date).getDate()}
                  </span>
                  <span className="text-muted-foreground text-xs">
                    {new Date(service.date).toLocaleDateString("fr-FR", { month: "short" })}
                  </span>
                </div>

                {/* Service Info */}
                <div className="min-w-0 flex-1">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h3 className="text-foreground font-semibold">{service.name}</h3>
                      <div className="text-muted-foreground mt-1 flex items-center gap-3 text-sm">
                        <span className="flex items-center gap-1">
                          <IconClock className="h-4 w-4" />
                          {service.time}
                          {service.endTime && ` - ${service.endTime}`}
                        </span>
                        <span className="flex items-center gap-1">
                          <IconUsers className="h-4 w-4" />
                          {service.confirmed} confirmé
                          {service.pending > 0 && `, ${service.pending} en attente`}
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {getStatusBadge(service.status)}
                      <DropdownMenu>
                        <DropdownMenuTrigger>
                          <Button variant="ghost" size="icon" render={<div />}>
                            <IconDots className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem>
                            <IconEdit className="mr-2 h-4 w-4" />
                            Modifier
                          </DropdownMenuItem>
                          {service.status === "draft" && (
                            <DropdownMenuItem onClick={() => handlePublish(service.id)}>
                              <IconSend className="mr-2 h-4 w-4" />
                              Publier
                            </DropdownMenuItem>
                          )}
                          <DropdownMenuSeparator />
                          <DropdownMenuItem
                            className="text-destructive"
                            onClick={() => handleDelete(service.id)}
                          >
                            <IconTrash className="mr-2 h-4 w-4" />
                            Supprimer
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </div>

                  {/* Teams */}
                  <div className="mt-3 flex flex-wrap gap-2">
                    {service.teams.map((team) => (
                      <Badge key={team} variant="outline">
                        {team}
                      </Badge>
                    ))}
                  </div>

                  {/* Notes */}
                  {service.notes && (
                    <p className="text-muted-foreground mt-2 text-sm">{service.notes}</p>
                  )}
                </div>
              </div>
            </Card>
          ))
        )}
      </div>

      {/* Create Service Sheet */}
      <Sheet open={isCreateOpen} onOpenChange={setIsCreateOpen}>
        <SheetContent className="overflow-y-auto sm:max-w-lg">
          <SheetHeader>
            <SheetTitle>Nouveau service</SheetTitle>
            <SheetDescription>
              Créez un nouveau service ou événement pour votre église
            </SheetDescription>
          </SheetHeader>
          <div className="mt-6 space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Nom du service *</Label>
              <Input
                id="name"
                placeholder="ex: Culte du dimanche"
                value={newService.name}
                onChange={(e) => setNewService((prev) => ({ ...prev, name: e.target.value }))}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="date">Date *</Label>
                <Input
                  id="date"
                  type="date"
                  value={newService.date}
                  onChange={(e) => setNewService((prev) => ({ ...prev, date: e.target.value }))}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="time">Heure de début *</Label>
                <Input
                  id="time"
                  type="time"
                  value={newService.time}
                  onChange={(e) => setNewService((prev) => ({ ...prev, time: e.target.value }))}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="endTime">Heure de fin</Label>
              <Input
                id="endTime"
                type="time"
                value={newService.endTime}
                onChange={(e) => setNewService((prev) => ({ ...prev, endTime: e.target.value }))}
              />
            </div>

            <div className="space-y-2">
              <Label>Équipes</Label>
              <div className="flex flex-wrap gap-2">
                {mockTeams.map((team) => (
                  <Badge
                    key={team.id}
                    variant={newService.teams.includes(team.name) ? "default" : "outline"}
                    className="cursor-pointer"
                    onClick={() => {
                      setNewService((prev) => ({
                        ...prev,
                        teams: prev.teams.includes(team.name)
                          ? prev.teams.filter((t) => t !== team.name)
                          : [...prev.teams, team.name],
                      }));
                    }}
                  >
                    {team.name}
                    {newService.teams.includes(team.name) && <IconCheck className="ml-1 h-3 w-3" />}
                  </Badge>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="dressCode">Code vestimentaire</Label>
              <Input
                id="dressCode"
                placeholder="ex: Tenue de ville élégante"
                value={newService.dressCode}
                onChange={(e) => setNewService((prev) => ({ ...prev, dressCode: e.target.value }))}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="notes">Notes</Label>
              <Textarea
                id="notes"
                placeholder="Informations supplémentaires..."
                value={newService.notes}
                onChange={(e) => setNewService((prev) => ({ ...prev, notes: e.target.value }))}
                rows={3}
              />
            </div>

            <div className="flex gap-2 pt-4">
              <Button variant="outline" className="flex-1" onClick={() => setIsCreateOpen(false)}>
                {tCommon("cancel")}
              </Button>
              <Button className="flex-1" onClick={handleCreateService} disabled={isCreating}>
                {isCreating ? (
                  <IconLoader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <IconPlus className="mr-2 h-4 w-4" />
                )}
                Créer
              </Button>
            </div>
          </div>
        </SheetContent>
      </Sheet>
    </div>
  );
}
