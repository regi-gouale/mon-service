/**
 * Language Switcher Component
 * Allows users to switch between available locales
 */

"use client";

import { usePathname, useRouter } from "@/i18n/navigation";
import { routing, type Locale } from "@/i18n/routing";
import { useLocale, useTranslations } from "next-intl";
import { useTransition } from "react";

export function LanguageSwitcher() {
  const t = useTranslations("Locale");
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();
  const [isPending, startTransition] = useTransition();

  const handleLocaleChange = (newLocale: Locale) => {
    startTransition(() => {
      router.replace(pathname, { locale: newLocale });
    });
  };

  return (
    <div className="flex items-center gap-2">
      {routing.locales.map((loc) => (
        <button
          key={loc}
          onClick={() => handleLocaleChange(loc)}
          disabled={isPending || locale === loc}
          className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
            locale === loc
              ? "bg-primary text-primary-foreground"
              : "bg-muted text-muted-foreground hover:bg-muted/80"
          } ${isPending ? "cursor-wait opacity-50" : ""}`}
          aria-label={t(loc)}
        >
          {loc.toUpperCase()}
        </button>
      ))}
    </div>
  );
}

/**
 * Language Switcher Dropdown Component
 * A dropdown version of the language switcher for use in headers/navbars
 */
export function LanguageSwitcherDropdown() {
  const t = useTranslations("Locale");
  const tSettings = useTranslations("Settings");
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();
  const [isPending, startTransition] = useTransition();

  const handleLocaleChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const newLocale = event.target.value as Locale;
    startTransition(() => {
      router.replace(pathname, { locale: newLocale });
    });
  };

  return (
    <div className="flex items-center gap-2">
      <label htmlFor="language-select" className="text-muted-foreground text-sm">
        {tSettings("language")}:
      </label>
      <select
        id="language-select"
        value={locale}
        onChange={handleLocaleChange}
        disabled={isPending}
        className={`border-input bg-background focus:ring-ring rounded-md border px-3 py-1.5 text-sm focus:ring-2 focus:outline-none ${
          isPending ? "cursor-wait opacity-50" : ""
        }`}
      >
        {routing.locales.map((loc) => (
          <option key={loc} value={loc}>
            {t(loc)}
          </option>
        ))}
      </select>
    </div>
  );
}
