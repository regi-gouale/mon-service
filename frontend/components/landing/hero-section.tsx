"use client";

import { Button } from "@/components/ui/button";
import { Link } from "@/i18n/navigation";
import { IconArrowRight, IconCalendarEvent, IconPlayerPlay, IconUsers } from "@tabler/icons-react";
import { useTranslations } from "next-intl";

export function HeroSection() {
  const t = useTranslations("Landing");

  return (
    <section className="relative overflow-hidden">
      {/* Background gradient */}
      <div className="gradient-hero pointer-events-none absolute inset-0" />

      {/* Decorative elements */}
      <div className="bg-primary/5 absolute -top-24 -right-24 h-96 w-96 rounded-full blur-3xl" />
      <div className="bg-accent/5 absolute -bottom-24 -left-24 h-96 w-96 rounded-full blur-3xl" />

      <div className="relative container mx-auto px-4 py-20 md:py-32">
        <div className="grid items-center gap-12 lg:grid-cols-2">
          {/* Left content */}
          <div className="animate-fade-in space-y-8">
            <div className="bg-primary/10 text-primary inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium">
              <IconCalendarEvent className="h-4 w-4" />
              <span>{t("badge")}</span>
            </div>

            <h1 className="text-foreground text-4xl leading-tight font-bold tracking-tight md:text-5xl lg:text-6xl">
              {t("heroTitle")}
              <span className="relative">
                <span className="text-primary relative z-10"> {t("heroHighlight")}</span>
                <svg
                  className="text-primary/30 absolute -bottom-2 left-0 h-3 w-full"
                  viewBox="0 0 200 12"
                  fill="none"
                >
                  <path
                    d="M2 10C50 4 150 4 198 10"
                    stroke="currentColor"
                    strokeWidth="4"
                    strokeLinecap="round"
                  />
                </svg>
              </span>
            </h1>

            <p className="text-muted-foreground max-w-lg text-lg md:text-xl">
              {t("heroDescription")}
            </p>

            <div className="flex flex-wrap gap-4">
              <Button size="lg" className="gap-2" render={<Link href="/register" />}>
                {t("getStarted")}
                <IconArrowRight className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="lg" className="gap-2">
                <IconPlayerPlay className="h-4 w-4" />
                {t("watchDemo")}
              </Button>
            </div>

            {/* Social proof */}
            <div className="flex items-center gap-6 pt-4">
              <div className="flex -space-x-3">
                {[1, 2, 3, 4, 5].map((i) => (
                  <div
                    key={i}
                    className="border-background from-primary/20 to-accent/20 text-foreground flex h-10 w-10 items-center justify-center rounded-full border-2 bg-linear-to-br text-xs font-medium"
                  >
                    {String.fromCharCode(64 + i)}
                  </div>
                ))}
              </div>
              <div className="text-sm">
                <p className="text-foreground font-semibold">{t("trustedBy")}</p>
                <p className="text-muted-foreground">{t("churches")}</p>
              </div>
            </div>
          </div>

          {/* Right content - Dashboard preview */}
          <div className="animate-slide-up relative">
            <div className="bg-card relative rounded-2xl border p-2 shadow-2xl">
              {/* Mock browser header */}
              <div className="flex items-center gap-2 border-b px-4 py-3">
                <div className="flex gap-1.5">
                  <div className="bg-destructive/60 h-3 w-3 rounded-full" />
                  <div className="bg-warning/60 h-3 w-3 rounded-full" />
                  <div className="bg-success/60 h-3 w-3 rounded-full" />
                </div>
                <div className="bg-muted text-muted-foreground flex-1 rounded-md px-3 py-1 text-center text-xs">
                  app.mon-service.fr
                </div>
              </div>

              {/* Mock dashboard content */}
              <div className="p-4">
                <div className="mb-4 flex items-center justify-between">
                  <div>
                    <div className="bg-foreground/10 h-4 w-32 rounded" />
                    <div className="bg-muted mt-2 h-3 w-48 rounded" />
                  </div>
                  <div className="flex gap-2">
                    <div className="bg-primary/20 h-8 w-20 rounded-md" />
                    <div className="bg-muted h-8 w-8 rounded-md" />
                  </div>
                </div>

                {/* Stats cards */}
                <div className="mb-4 grid grid-cols-3 gap-3">
                  {[
                    { icon: IconCalendarEvent, value: "12", label: "Services", color: "primary" },
                    { icon: IconUsers, value: "48", label: "Membres", color: "success" },
                    { icon: IconCalendarEvent, value: "6", label: "Équipes", color: "accent" },
                  ].map((stat, i) => (
                    <div key={i} className="bg-card rounded-lg border p-3 text-center">
                      <stat.icon className={`mx-auto mb-1 h-5 w-5 text-${stat.color}`} />
                      <div className="text-xl font-bold">{stat.value}</div>
                      <div className="text-muted-foreground text-xs">{stat.label}</div>
                    </div>
                  ))}
                </div>

                {/* Mock calendar */}
                <div className="bg-muted/30 rounded-lg border p-3">
                  <div className="mb-2 flex items-center justify-between">
                    <div className="bg-foreground/10 h-3 w-20 rounded" />
                    <div className="flex gap-1">
                      <div className="bg-muted h-6 w-6 rounded" />
                      <div className="bg-muted h-6 w-6 rounded" />
                    </div>
                  </div>
                  <div className="grid grid-cols-7 gap-1">
                    {Array.from({ length: 35 }).map((_, i) => (
                      <div
                        key={i}
                        className={`h-8 rounded ${
                          [5, 12, 19, 26].includes(i)
                            ? "bg-primary/30"
                            : i === 15
                              ? "bg-accent/40 ring-accent ring-2"
                              : "bg-card"
                        }`}
                      />
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Floating elements */}
            <div className="bg-card animate-slide-in-left absolute -bottom-4 -left-4 rounded-lg border p-3 shadow-lg">
              <div className="flex items-center gap-3">
                <div className="bg-success/20 flex h-10 w-10 items-center justify-center rounded-full">
                  <IconUsers className="text-success h-5 w-5" />
                </div>
                <div>
                  <p className="text-sm font-medium">+3 confirmés</p>
                  <p className="text-muted-foreground text-xs">Dimanche matin</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
