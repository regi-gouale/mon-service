/**
 * Site Configuration
 * Global site metadata and navigation configuration
 */

export const siteConfig = {
  name: "Church Team Management",
  description: "Gérez vos équipes de département, plannings et services pour votre église",
  url: process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000",
  ogImage: "/og-image.png",
  links: {
    github: "https://github.com/yourusername/church-team-management",
    docs: "/docs",
  },
};

export type SiteConfig = typeof siteConfig;

// Navigation configuration
export interface NavItem {
  title: string;
  href: string;
  icon?: string;
  disabled?: boolean;
  external?: boolean;
  label?: string;
}

export interface NavConfig {
  mainNav: NavItem[];
  sidebarNav: NavItem[];
}

export const navConfig: NavConfig = {
  mainNav: [
    {
      title: "Tableau de bord",
      href: "/dashboard",
    },
    {
      title: "Planning",
      href: "/planning",
    },
    {
      title: "Équipe",
      href: "/team",
    },
  ],
  sidebarNav: [
    {
      title: "Tableau de bord",
      href: "/dashboard",
      icon: "home",
    },
    {
      title: "Mes disponibilités",
      href: "/availability",
      icon: "calendar",
    },
    {
      title: "Planning",
      href: "/planning",
      icon: "calendar-range",
    },
    {
      title: "Équipe",
      href: "/team",
      icon: "users",
    },
    {
      title: "Notifications",
      href: "/notifications",
      icon: "bell",
    },
    {
      title: "Inventaire",
      href: "/inventory",
      icon: "package",
    },
    {
      title: "Rapports",
      href: "/reports",
      icon: "file-text",
    },
    {
      title: "Calendrier",
      href: "/calendar",
      icon: "calendar-days",
    },
    {
      title: "Paramètres",
      href: "/settings",
      icon: "settings",
    },
  ],
};

// Feature flags
export const features = {
  enableOAuth: process.env.NEXT_PUBLIC_ENABLE_OAUTH === "true",
  enableWebSockets: process.env.NEXT_PUBLIC_ENABLE_WEBSOCKETS !== "false",
  enableNotifications: process.env.NEXT_PUBLIC_ENABLE_NOTIFICATIONS !== "false",
  enableDarkMode: true,
  enableI18n: true,
};

// App metadata
export const appMetadata = {
  version: "1.0.0",
  apiVersion: "v1",
  buildDate: new Date().toISOString(),
};
