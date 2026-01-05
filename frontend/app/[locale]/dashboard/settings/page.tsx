/**
 * Settings Page
 * Application settings including theme, language, and notification preferences
 */

"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { useRouter } from "@/i18n/navigation";
import {
  IconBell,
  IconCheck,
  IconDeviceFloppy,
  IconDeviceMobile,
  IconGlobe,
  IconLoader2,
  IconMail,
  IconMoon,
  IconPalette,
  IconSun,
} from "@tabler/icons-react";
import { useTranslations } from "next-intl";
import { useTheme } from "next-themes";
import { useParams } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

interface NotificationSetting {
  id: string;
  label: string;
  description: string;
  email: boolean;
  push: boolean;
}

export default function SettingsPage() {
  const t = useTranslations("Settings");
  const tCommon = useTranslations("Common");
  const { theme, setTheme } = useTheme();
  const router = useRouter();
  const params = useParams();
  const currentLocale = (params.locale as string) || "fr";

  const [isSaving, setIsSaving] = useState(false);
  const [language, setLanguage] = useState(currentLocale);

  const [notificationSettings, setNotificationSettings] = useState<NotificationSetting[]>([
    {
      id: "assignments",
      label: "Nouvelles affectations",
      description: "Être notifié quand vous êtes affecté à un service",
      email: true,
      push: true,
    },
    {
      id: "reminders",
      label: "Rappels de service",
      description: "Recevoir un rappel 24h avant chaque service",
      email: true,
      push: true,
    },
    {
      id: "planning",
      label: "Publication de planning",
      description: "Être notifié quand un nouveau planning est publié",
      email: true,
      push: false,
    },
    {
      id: "availability",
      label: "Saisie des disponibilités",
      description: "Rappel pour saisir vos disponibilités",
      email: true,
      push: false,
    },
    {
      id: "announcements",
      label: "Annonces de l'équipe",
      description: "Recevoir les annonces du responsable d'équipe",
      email: false,
      push: true,
    },
  ]);

  const handleLanguageChange = (newLocale: string | null) => {
    if (!newLocale) return;
    setLanguage(newLocale);
    router.replace("/dashboard/settings", { locale: newLocale as "fr" | "en" });
    toast.success("Langue modifiée");
  };

  const toggleNotification = (id: string, type: "email" | "push") => {
    setNotificationSettings((prev) =>
      prev.map((setting) => (setting.id === id ? { ...setting, [type]: !setting[type] } : setting))
    );
  };

  const handleSaveSettings = async () => {
    setIsSaving(true);
    await new Promise((resolve) => setTimeout(resolve, 1000));
    setIsSaving(false);
    toast.success("Paramètres enregistrés");
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-foreground text-2xl font-bold md:text-3xl">{t("title")}</h1>
          <p className="text-muted-foreground mt-1">Gérez vos préférences et paramètres</p>
        </div>
        <Button onClick={handleSaveSettings} disabled={isSaving}>
          {isSaving ? (
            <IconLoader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <IconDeviceFloppy className="mr-2 h-4 w-4" />
          )}
          {tCommon("save")}
        </Button>
      </div>

      <div className="grid gap-6">
        {/* Appearance */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <IconPalette className="h-5 w-5" />
              Apparence
            </CardTitle>
            <CardDescription>Personnalisez l&apos;apparence de l&apos;application</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-3">
              <Label>{t("theme")}</Label>
              <div className="grid grid-cols-3 gap-3">
                <Button
                  variant={theme === "light" ? "default" : "outline"}
                  className="flex-col gap-2 py-6"
                  onClick={() => setTheme("light")}
                >
                  <IconSun className="h-5 w-5" />
                  <span className="text-xs">{t("lightMode")}</span>
                  {theme === "light" && <IconCheck className="absolute top-2 right-2 h-4 w-4" />}
                </Button>
                <Button
                  variant={theme === "dark" ? "default" : "outline"}
                  className="flex-col gap-2 py-6"
                  onClick={() => setTheme("dark")}
                >
                  <IconMoon className="h-5 w-5" />
                  <span className="text-xs">{t("darkMode")}</span>
                  {theme === "dark" && <IconCheck className="absolute top-2 right-2 h-4 w-4" />}
                </Button>
                <Button
                  variant={theme === "system" ? "default" : "outline"}
                  className="flex-col gap-2 py-6"
                  onClick={() => setTheme("system")}
                >
                  <IconDeviceMobile className="h-5 w-5" />
                  <span className="text-xs">{t("systemTheme")}</span>
                  {theme === "system" && <IconCheck className="absolute top-2 right-2 h-4 w-4" />}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Language */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <IconGlobe className="h-5 w-5" />
              {t("language")}
            </CardTitle>
            <CardDescription>Choisissez la langue de l&apos;interface</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="max-w-xs">
              <Select value={language} onValueChange={handleLanguageChange}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="fr">
                    <span className="flex items-center gap-2">🇫🇷 Français</span>
                  </SelectItem>
                  <SelectItem value="en">
                    <span className="flex items-center gap-2">🇬🇧 English</span>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Notifications */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <IconBell className="h-5 w-5" />
              {t("notificationPreferences")}
            </CardTitle>
            <CardDescription>
              Configurez comment et quand vous souhaitez être notifié
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-1">
              {/* Header */}
              <div className="grid grid-cols-[1fr,auto,auto] items-center gap-4 pb-2">
                <div />
                <div className="flex w-20 items-center justify-center gap-1 text-sm font-medium">
                  <IconMail className="h-4 w-4" />
                  Email
                </div>
                <div className="flex w-20 items-center justify-center gap-1 text-sm font-medium">
                  <IconBell className="h-4 w-4" />
                  Push
                </div>
              </div>

              <Separator />

              {/* Settings */}
              {notificationSettings.map((setting) => (
                <div
                  key={setting.id}
                  className="grid grid-cols-[1fr,auto,auto] items-center gap-4 py-3"
                >
                  <div>
                    <p className="text-foreground text-sm font-medium">{setting.label}</p>
                    <p className="text-muted-foreground text-xs">{setting.description}</p>
                  </div>
                  <div className="flex w-20 justify-center">
                    <Button
                      variant={setting.email ? "default" : "outline"}
                      size="sm"
                      className="h-8 w-8 p-0"
                      onClick={() => toggleNotification(setting.id, "email")}
                    >
                      {setting.email && <IconCheck className="h-4 w-4" />}
                    </Button>
                  </div>
                  <div className="flex w-20 justify-center">
                    <Button
                      variant={setting.push ? "default" : "outline"}
                      size="sm"
                      className="h-8 w-8 p-0"
                      onClick={() => toggleNotification(setting.id, "push")}
                    >
                      {setting.push && <IconCheck className="h-4 w-4" />}
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Danger Zone */}
        <Card className="border-destructive/50">
          <CardHeader>
            <CardTitle className="text-destructive">Zone de danger</CardTitle>
            <CardDescription>Actions irréversibles concernant votre compte</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between rounded-lg border p-4">
              <div>
                <p className="font-medium">{t("exportData")}</p>
                <p className="text-muted-foreground text-sm">
                  Téléchargez une copie de toutes vos données
                </p>
              </div>
              <Button variant="outline">Exporter</Button>
            </div>
            <div className="flex items-center justify-between rounded-lg border p-4">
              <div>
                <p className="font-medium">{t("deleteAccount")}</p>
                <p className="text-muted-foreground text-sm">
                  Supprimez définitivement votre compte et toutes vos données
                </p>
              </div>
              <Button variant="destructive">Supprimer</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
