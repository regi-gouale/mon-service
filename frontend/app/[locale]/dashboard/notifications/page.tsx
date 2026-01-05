/**
 * Notifications Page
 * Manage all user notifications with filtering and actions
 */

"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { mockNotifications, type MockNotification } from "@/lib/mock-data";
import {
  IconBell,
  IconBellOff,
  IconCalendar,
  IconCheck,
  IconCheckbox,
  IconChevronDown,
  IconDots,
  IconFilter,
  IconMail,
  IconMailOpened,
  IconSpeakerphone,
  IconTrash,
  IconUserCheck,
} from "@tabler/icons-react";
import { useTranslations } from "next-intl";
import Link from "next/link";
import { useState } from "react";
import { toast } from "sonner";

type NotificationFilter = "all" | "unread" | "read";
type NotificationType = MockNotification["type"];

const notificationIcons: Record<NotificationType, typeof IconBell> = {
  assignment: IconUserCheck,
  reminder: IconCalendar,
  announcement: IconSpeakerphone,
  availability: IconCheckbox,
  planning: IconCalendar,
};

const notificationColors: Record<NotificationType, string> = {
  assignment: "bg-blue-500/10 text-blue-600",
  reminder: "bg-orange-500/10 text-orange-600",
  announcement: "bg-purple-500/10 text-purple-600",
  availability: "bg-green-500/10 text-green-600",
  planning: "bg-primary/10 text-primary",
};

export default function NotificationsPage() {
  const t = useTranslations("Notifications");
  const tCommon = useTranslations("Common");

  const [notifications, setNotifications] = useState<MockNotification[]>(mockNotifications);
  const [filter, setFilter] = useState<NotificationFilter>("all");

  const unreadCount = notifications.filter((n) => !n.isRead).length;

  const filteredNotifications = notifications.filter((n) => {
    if (filter === "unread") return !n.isRead;
    if (filter === "read") return n.isRead;
    return true;
  });

  const markAsRead = (id: string) => {
    setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, isRead: true } : n)));
    toast.success(t("markedAsRead"));
  };

  const markAsUnread = (id: string) => {
    setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, isRead: false } : n)));
  };

  const markAllAsRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, isRead: true })));
    toast.success(t("allMarkedAsRead"));
  };

  const deleteNotification = (id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
    toast.success(t("notificationDeleted"));
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffHours < 1) return "Il y a quelques minutes";
    if (diffHours < 24) return `Il y a ${diffHours}h`;
    if (diffDays < 7) return `Il y a ${diffDays} jour${diffDays > 1 ? "s" : ""}`;

    return date.toLocaleDateString("fr-FR", {
      day: "numeric",
      month: "short",
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-foreground text-2xl font-bold md:text-3xl">{t("title")}</h1>
          <p className="text-muted-foreground mt-1">
            {unreadCount > 0
              ? `${unreadCount} notification${unreadCount > 1 ? "s" : ""} non lue${unreadCount > 1 ? "s" : ""}`
              : t("allRead")}
          </p>
        </div>
        <div className="flex gap-2">
          {unreadCount > 0 && (
            <Button variant="outline" onClick={markAllAsRead}>
              <IconCheck className="mr-2 h-4 w-4" />
              {t("markAllAsRead")}
            </Button>
          )}
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-2">
        <DropdownMenu>
          <DropdownMenuTrigger>
            <Button variant="outline" className="gap-2" render={<div />}>
              <IconFilter className="h-4 w-4" />
              {filter === "all" && "Toutes"}
              {filter === "unread" && "Non lues"}
              {filter === "read" && "Lues"}
              <IconChevronDown className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            <DropdownMenuItem onClick={() => setFilter("all")}>
              <IconBell className="mr-2 h-4 w-4" />
              Toutes les notifications
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setFilter("unread")}>
              <IconMail className="mr-2 h-4 w-4" />
              Non lues
              {unreadCount > 0 && (
                <Badge variant="secondary" className="ml-auto">
                  {unreadCount}
                </Badge>
              )}
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setFilter("read")}>
              <IconMailOpened className="mr-2 h-4 w-4" />
              Lues
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Notifications List */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg">{t("recentNotifications")}</CardTitle>
          <CardDescription>
            {filteredNotifications.length} notification
            {filteredNotifications.length !== 1 ? "s" : ""}
          </CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          {filteredNotifications.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12">
              <div className="bg-muted mb-4 flex h-16 w-16 items-center justify-center rounded-full">
                <IconBellOff className="text-muted-foreground h-8 w-8" />
              </div>
              <p className="text-muted-foreground text-sm">{t("noNotifications")}</p>
            </div>
          ) : (
            <div className="divide-y">
              {filteredNotifications.map((notification) => {
                const Icon = notificationIcons[notification.type];
                const colorClass = notificationColors[notification.type];

                return (
                  <div
                    key={notification.id}
                    className={`flex items-start gap-4 p-4 transition-colors ${
                      !notification.isRead ? "bg-primary/5" : "hover:bg-muted/50"
                    }`}
                  >
                    {/* Icon */}
                    <div
                      className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full ${colorClass}`}
                    >
                      <Icon className="h-5 w-5" />
                    </div>

                    {/* Content */}
                    <div className="min-w-0 flex-1">
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <p
                            className={`text-sm font-medium ${!notification.isRead ? "text-foreground" : "text-muted-foreground"}`}
                          >
                            {notification.title}
                          </p>
                          <p className="text-muted-foreground mt-0.5 text-sm">
                            {notification.message}
                          </p>
                        </div>
                        {!notification.isRead && (
                          <div className="bg-primary h-2 w-2 shrink-0 rounded-full" />
                        )}
                      </div>

                      <div className="mt-2 flex items-center gap-3">
                        <span className="text-muted-foreground text-xs">
                          {formatDate(notification.createdAt)}
                        </span>
                        {notification.actionUrl && (
                          <Link
                            href={notification.actionUrl}
                            className="text-primary text-xs font-medium hover:underline"
                          >
                            Voir détails
                          </Link>
                        )}
                      </div>
                    </div>

                    {/* Actions */}
                    <DropdownMenu>
                      <DropdownMenuTrigger>
                        <Button variant="ghost" size="icon" className="h-8 w-8" render={<div />}>
                          <IconDots className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        {notification.isRead ? (
                          <DropdownMenuItem onClick={() => markAsUnread(notification.id)}>
                            <IconMail className="mr-2 h-4 w-4" />
                            Marquer comme non lu
                          </DropdownMenuItem>
                        ) : (
                          <DropdownMenuItem onClick={() => markAsRead(notification.id)}>
                            <IconMailOpened className="mr-2 h-4 w-4" />
                            {t("markAsRead")}
                          </DropdownMenuItem>
                        )}
                        <DropdownMenuItem
                          onClick={() => deleteNotification(notification.id)}
                          className="text-destructive"
                        >
                          <IconTrash className="mr-2 h-4 w-4" />
                          {tCommon("delete")}
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
