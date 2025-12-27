import { defineRouting } from "next-intl/routing";

export const routing = defineRouting({
  // List of all supported locales
  locales: ["fr", "en"],

  // Default locale (French)
  defaultLocale: "fr",

  // Locale prefix strategy: always show locale in URL
  localePrefix: "always",

  // Cookie configuration for locale persistence
  localeCookie: {
    name: "NEXT_LOCALE",
    maxAge: 31536000, // 1 year
    sameSite: "lax",
  },
});

export type Locale = (typeof routing.locales)[number];
