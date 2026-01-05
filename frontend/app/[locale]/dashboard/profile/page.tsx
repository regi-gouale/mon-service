/**
 * Profile Page
 * User profile management with personal info, password change, and preferences
 */

"use client";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Textarea } from "@/components/ui/textarea";
import { useAuthStore } from "@/stores/auth";
import {
  IconCamera,
  IconCheck,
  IconDeviceFloppy,
  IconEdit,
  IconKey,
  IconLoader2,
  IconMail,
  IconShield,
  IconUser,
} from "@tabler/icons-react";
import { useTranslations } from "next-intl";
import { useState } from "react";
import { toast } from "sonner";

export default function ProfilePage() {
  const t = useTranslations("Profile");
  const tCommon = useTranslations("Common");
  const { user } = useAuthStore();

  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isChangingPassword, setIsChangingPassword] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    firstName: user?.firstName || "",
    lastName: user?.lastName || "",
    email: user?.email || "",
    phone: "",
    bio: "",
  });

  const [passwordData, setPasswordData] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPasswordData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleSaveProfile = async () => {
    setIsSaving(true);
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1000));
    setIsSaving(false);
    setIsEditing(false);
    toast.success("Profil mis à jour avec succès");
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();

    if (passwordData.newPassword !== passwordData.confirmPassword) {
      toast.error("Les mots de passe ne correspondent pas");
      return;
    }

    if (passwordData.newPassword.length < 8) {
      toast.error("Le mot de passe doit contenir au moins 8 caractères");
      return;
    }

    setIsSaving(true);
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1000));
    setIsSaving(false);
    setIsChangingPassword(false);
    setPasswordData({ currentPassword: "", newPassword: "", confirmPassword: "" });
    toast.success("Mot de passe modifié avec succès");
  };

  const getInitials = () => {
    return `${user?.firstName?.charAt(0) || ""}${user?.lastName?.charAt(0) || ""}`.toUpperCase();
  };

  const getRoleBadge = () => {
    switch (user?.role) {
      case "admin":
        return <Badge variant="default">Administrateur</Badge>;
      case "leader":
        return <Badge variant="secondary">Responsable</Badge>;
      default:
        return <Badge variant="outline">Membre</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-foreground text-2xl font-bold md:text-3xl">{t("title")}</h1>
        <p className="text-muted-foreground mt-1">{t("description")}</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Profile Card */}
        <Card className="lg:col-span-1">
          <CardContent className="pt-6">
            <div className="flex flex-col items-center text-center">
              <div className="relative">
                <Avatar className="h-24 w-24">
                  <AvatarImage src={user?.avatarUrl} />
                  <AvatarFallback className="bg-primary/10 text-primary text-2xl">
                    {getInitials()}
                  </AvatarFallback>
                </Avatar>
                <Button
                  size="icon"
                  variant="secondary"
                  className="absolute -right-1 -bottom-1 h-8 w-8 rounded-full"
                >
                  <IconCamera className="h-4 w-4" />
                </Button>
              </div>

              <h2 className="text-foreground mt-4 text-xl font-semibold">
                {user?.firstName} {user?.lastName}
              </h2>
              <p className="text-muted-foreground text-sm">{user?.email}</p>

              <div className="mt-3 flex items-center gap-2">
                {getRoleBadge()}
                {user?.isEmailVerified && (
                  <Badge variant="outline" className="gap-1 text-green-600">
                    <IconCheck className="h-3 w-3" />
                    Vérifié
                  </Badge>
                )}
              </div>

              <Separator className="my-6" />

              <div className="w-full space-y-3 text-left">
                <div className="text-muted-foreground flex items-center gap-3 text-sm">
                  <IconMail className="h-4 w-4" />
                  <span>{user?.email}</span>
                </div>
                <div className="text-muted-foreground flex items-center gap-3 text-sm">
                  <IconShield className="h-4 w-4" />
                  <span>
                    {user?.role === "admin"
                      ? "Administrateur"
                      : user?.role === "leader"
                        ? "Responsable"
                        : "Membre"}
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Edit Profile */}
        <div className="space-y-6 lg:col-span-2">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <IconUser className="h-5 w-5" />
                  {t("personalInfo")}
                </CardTitle>
                <CardDescription>{t("personalInfoDescription")}</CardDescription>
              </div>
              {!isEditing && (
                <Button variant="outline" size="sm" onClick={() => setIsEditing(true)}>
                  <IconEdit className="mr-2 h-4 w-4" />
                  {tCommon("edit")}
                </Button>
              )}
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="firstName">{t("firstName")}</Label>
                  <Input
                    id="firstName"
                    name="firstName"
                    value={formData.firstName}
                    onChange={handleChange}
                    disabled={!isEditing}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="lastName">{t("lastName")}</Label>
                  <Input
                    id="lastName"
                    name="lastName"
                    value={formData.lastName}
                    onChange={handleChange}
                    disabled={!isEditing}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">{t("email")}</Label>
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    value={formData.email}
                    onChange={handleChange}
                    disabled={!isEditing}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="phone">{t("phone")}</Label>
                  <Input
                    id="phone"
                    name="phone"
                    type="tel"
                    placeholder="06 12 34 56 78"
                    value={formData.phone}
                    onChange={handleChange}
                    disabled={!isEditing}
                  />
                </div>
                <div className="space-y-2 sm:col-span-2">
                  <Label htmlFor="bio">{t("bio")}</Label>
                  <Textarea
                    id="bio"
                    name="bio"
                    placeholder={t("bioPlaceholder")}
                    value={formData.bio}
                    onChange={handleChange}
                    disabled={!isEditing}
                    rows={3}
                  />
                </div>
              </div>

              {isEditing && (
                <div className="mt-6 flex justify-end gap-3">
                  <Button
                    variant="outline"
                    onClick={() => {
                      setIsEditing(false);
                      setFormData({
                        firstName: user?.firstName || "",
                        lastName: user?.lastName || "",
                        email: user?.email || "",
                        phone: "",
                        bio: "",
                      });
                    }}
                  >
                    {tCommon("cancel")}
                  </Button>
                  <Button onClick={handleSaveProfile} disabled={isSaving}>
                    {isSaving ? (
                      <IconLoader2 className="mr-2 h-4 w-4 animate-spin" />
                    ) : (
                      <IconDeviceFloppy className="mr-2 h-4 w-4" />
                    )}
                    {tCommon("save")}
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Change Password */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <IconKey className="h-5 w-5" />
                {t("changePassword")}
              </CardTitle>
              <CardDescription>{t("changePasswordDescription")}</CardDescription>
            </CardHeader>
            <CardContent>
              {!isChangingPassword ? (
                <Button variant="outline" onClick={() => setIsChangingPassword(true)}>
                  {t("changePassword")}
                </Button>
              ) : (
                <form onSubmit={handleChangePassword} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="currentPassword">{t("currentPassword")}</Label>
                    <Input
                      id="currentPassword"
                      name="currentPassword"
                      type="password"
                      value={passwordData.currentPassword}
                      onChange={handlePasswordChange}
                      required
                    />
                  </div>
                  <div className="grid gap-4 sm:grid-cols-2">
                    <div className="space-y-2">
                      <Label htmlFor="newPassword">{t("newPassword")}</Label>
                      <Input
                        id="newPassword"
                        name="newPassword"
                        type="password"
                        value={passwordData.newPassword}
                        onChange={handlePasswordChange}
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="confirmPassword">{t("confirmNewPassword")}</Label>
                      <Input
                        id="confirmPassword"
                        name="confirmPassword"
                        type="password"
                        value={passwordData.confirmPassword}
                        onChange={handlePasswordChange}
                        required
                      />
                    </div>
                  </div>
                  <div className="flex justify-end gap-3">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => {
                        setIsChangingPassword(false);
                        setPasswordData({
                          currentPassword: "",
                          newPassword: "",
                          confirmPassword: "",
                        });
                      }}
                    >
                      {tCommon("cancel")}
                    </Button>
                    <Button type="submit" disabled={isSaving}>
                      {isSaving ? (
                        <IconLoader2 className="mr-2 h-4 w-4 animate-spin" />
                      ) : (
                        <IconKey className="mr-2 h-4 w-4" />
                      )}
                      {t("updatePassword")}
                    </Button>
                  </div>
                </form>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
