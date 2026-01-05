"use client";

import {
  IconBell,
  IconCalendar,
  IconCalendarEvent,
  IconChartBar,
  IconClock,
  IconDeviceMobile,
  IconMail,
  IconUsers,
  IconUserShield,
} from "@tabler/icons-react";
import { useTranslations } from "next-intl";

const features = [
  {
    icon: IconCalendarEvent,
    titleKey: "featureScheduling",
    descKey: "featureSchedulingDesc",
    color: "primary",
  },
  {
    icon: IconUsers,
    titleKey: "featureTeams",
    descKey: "featureTeamsDesc",
    color: "success",
  },
  {
    icon: IconCalendar,
    titleKey: "featureAvailability",
    descKey: "featureAvailabilityDesc",
    color: "accent",
  },
  {
    icon: IconBell,
    titleKey: "featureNotifications",
    descKey: "featureNotificationsDesc",
    color: "info",
  },
  {
    icon: IconDeviceMobile,
    titleKey: "featureMobile",
    descKey: "featureMobileDesc",
    color: "primary",
  },
  {
    icon: IconChartBar,
    titleKey: "featureReports",
    descKey: "featureReportsDesc",
    color: "warning",
  },
];

export function FeaturesSection() {
  const t = useTranslations("Landing");

  return (
    <section className="relative py-20 md:py-32">
      <div className="container mx-auto px-4">
        {/* Section header */}
        <div className="mx-auto mb-16 max-w-2xl text-center">
          <p className="text-primary mb-4 text-sm font-medium tracking-wider uppercase">
            {t("featuresLabel")}
          </p>
          <h2 className="text-foreground mb-4 text-3xl font-bold tracking-tight md:text-4xl">
            {t("featuresTitle")}
          </h2>
          <p className="text-muted-foreground text-lg">{t("featuresSubtitle")}</p>
        </div>

        {/* Features grid */}
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, i) => (
            <div
              key={i}
              className="group bg-card hover:border-primary/50 relative rounded-2xl border p-6 transition-all hover:shadow-lg"
            >
              {/* Icon */}
              <div
                className={`mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-${feature.color}/10`}
              >
                <feature.icon className={`h-6 w-6 text-${feature.color}`} />
              </div>

              {/* Content */}
              <h3 className="text-foreground mb-2 text-xl font-semibold">{t(feature.titleKey)}</h3>
              <p className="text-muted-foreground">{t(feature.descKey)}</p>

              {/* Hover indicator */}
              <div className="bg-primary absolute bottom-0 left-0 h-1 w-0 rounded-b-2xl transition-all group-hover:w-full" />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export function HowItWorksSection() {
  const t = useTranslations("Landing");

  const steps = [
    {
      icon: IconUserShield,
      step: "01",
      titleKey: "step1Title",
      descKey: "step1Desc",
    },
    {
      icon: IconUsers,
      step: "02",
      titleKey: "step2Title",
      descKey: "step2Desc",
    },
    {
      icon: IconClock,
      step: "03",
      titleKey: "step3Title",
      descKey: "step3Desc",
    },
    {
      icon: IconMail,
      step: "04",
      titleKey: "step4Title",
      descKey: "step4Desc",
    },
  ];

  return (
    <section className="bg-muted/50 relative py-20 md:py-32">
      <div className="container mx-auto px-4">
        {/* Section header */}
        <div className="mx-auto mb-16 max-w-2xl text-center">
          <p className="text-primary mb-4 text-sm font-medium tracking-wider uppercase">
            {t("howItWorksLabel")}
          </p>
          <h2 className="text-foreground mb-4 text-3xl font-bold tracking-tight md:text-4xl">
            {t("howItWorksTitle")}
          </h2>
          <p className="text-muted-foreground text-lg">{t("howItWorksSubtitle")}</p>
        </div>

        {/* Steps */}
        <div className="relative">
          {/* Connection line */}
          <div className="bg-border absolute top-0 left-1/2 hidden h-full w-0.5 -translate-x-1/2 md:block" />

          <div className="space-y-12 md:space-y-0">
            {steps.map((step, i) => (
              <div
                key={i}
                className={`relative flex flex-col items-center gap-8 md:flex-row ${
                  i % 2 === 1 ? "md:flex-row-reverse" : ""
                }`}
              >
                {/* Content */}
                <div className={`flex-1 ${i % 2 === 1 ? "md:text-left" : "md:text-right"}`}>
                  <div
                    className={`bg-card inline-block rounded-xl border p-6 shadow-sm ${
                      i % 2 === 1 ? "md:ml-0" : "md:ml-auto"
                    }`}
                  >
                    <p className="text-primary mb-2 text-sm font-bold">{step.step}</p>
                    <h3 className="text-foreground mb-2 text-xl font-semibold">
                      {t(step.titleKey)}
                    </h3>
                    <p className="text-muted-foreground max-w-sm">{t(step.descKey)}</p>
                  </div>
                </div>

                {/* Center icon */}
                <div className="border-background bg-primary relative z-10 flex h-16 w-16 items-center justify-center rounded-full border-4 shadow-lg">
                  <step.icon className="text-primary-foreground h-8 w-8" />
                </div>

                {/* Spacer */}
                <div className="hidden flex-1 md:block" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
