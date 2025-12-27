/**
 * Auth Layout
 * Layout for authentication pages (login, register, etc.)
 */

import { Card } from "@/components/ui/card";
import { useTranslations } from "next-intl";
import { setRequestLocale } from "next-intl/server";
import { ReactNode } from "react";

interface AuthLayoutProps {
  children: ReactNode;
  params: Promise<{ locale: string }>;
}

export default async function AuthLayout({ children, params }: AuthLayoutProps) {
  const { locale } = await params;
  setRequestLocale(locale);

  return <AuthLayoutContent>{children}</AuthLayoutContent>;
}

function AuthLayoutContent({ children }: { children: ReactNode }) {
  const t = useTranslations("Metadata");

  return (
    <div className="from-background to-muted flex min-h-screen items-center justify-center bg-linear-to-br p-4">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <h1 className="text-foreground mb-2 text-3xl font-bold">{t("title")}</h1>
          <p className="text-muted-foreground">{t("description")}</p>
        </div>

        <Card className="p-8">{children}</Card>

        <div className="text-muted-foreground mt-6 text-center text-sm">
          <p>© 2025 Mon Service. Tous droits réservés.</p>
        </div>
      </div>
    </div>
  );
}
