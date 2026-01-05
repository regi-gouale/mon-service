"use client";

import { Button } from "@/components/ui/button";
import { Link } from "@/i18n/navigation";
import { IconArrowRight, IconCheck, IconStar } from "@tabler/icons-react";
import { useTranslations } from "next-intl";

export function TestimonialsSection() {
  const t = useTranslations("Landing");

  const testimonials = [
    {
      quote: t("testimonial1Quote"),
      author: t("testimonial1Author"),
      role: t("testimonial1Role"),
      church: t("testimonial1Church"),
      rating: 5,
    },
    {
      quote: t("testimonial2Quote"),
      author: t("testimonial2Author"),
      role: t("testimonial2Role"),
      church: t("testimonial2Church"),
      rating: 5,
    },
    {
      quote: t("testimonial3Quote"),
      author: t("testimonial3Author"),
      role: t("testimonial3Role"),
      church: t("testimonial3Church"),
      rating: 5,
    },
  ];

  return (
    <section className="relative py-20 md:py-32">
      <div className="container mx-auto px-4">
        {/* Section header */}
        <div className="mx-auto mb-16 max-w-2xl text-center">
          <p className="text-primary mb-4 text-sm font-medium tracking-wider uppercase">
            {t("testimonialsLabel")}
          </p>
          <h2 className="text-foreground mb-4 text-3xl font-bold tracking-tight md:text-4xl">
            {t("testimonialsTitle")}
          </h2>
          <p className="text-muted-foreground text-lg">{t("testimonialsSubtitle")}</p>
        </div>

        {/* Testimonials grid */}
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          {testimonials.map((testimonial, i) => (
            <div key={i} className="bg-card relative rounded-2xl border p-6 shadow-sm">
              {/* Stars */}
              <div className="mb-4 flex gap-1">
                {Array.from({ length: testimonial.rating }).map((_, j) => (
                  <IconStar key={j} className="fill-warning text-warning h-5 w-5" />
                ))}
              </div>

              {/* Quote */}
              <blockquote className="text-foreground mb-6">
                &ldquo;{testimonial.quote}&rdquo;
              </blockquote>

              {/* Author */}
              <div className="flex items-center gap-3">
                <div className="bg-primary/10 text-primary flex h-10 w-10 items-center justify-center rounded-full text-sm font-semibold">
                  {testimonial.author
                    .split(" ")
                    .map((n) => n[0])
                    .join("")}
                </div>
                <div>
                  <p className="text-foreground font-semibold">{testimonial.author}</p>
                  <p className="text-muted-foreground text-sm">
                    {testimonial.role} • {testimonial.church}
                  </p>
                </div>
              </div>

              {/* Decorative quote mark */}
              <div className="text-primary/10 absolute -top-2 right-6 font-serif text-6xl">
                &ldquo;
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export function PricingSection() {
  const t = useTranslations("Landing");

  const plans = [
    {
      name: t("pricingFree"),
      price: "0€",
      period: t("pricingMonth"),
      description: t("pricingFreeDesc"),
      features: [
        t("pricingFreeFeature1"),
        t("pricingFreeFeature2"),
        t("pricingFreeFeature3"),
        t("pricingFreeFeature4"),
      ],
      cta: t("pricingStartFree"),
      highlighted: false,
    },
    {
      name: t("pricingPro"),
      price: "29€",
      period: t("pricingMonth"),
      description: t("pricingProDesc"),
      features: [
        t("pricingProFeature1"),
        t("pricingProFeature2"),
        t("pricingProFeature3"),
        t("pricingProFeature4"),
        t("pricingProFeature5"),
      ],
      cta: t("pricingStartTrial"),
      highlighted: true,
    },
    {
      name: t("pricingEnterprise"),
      price: t("pricingCustom"),
      period: "",
      description: t("pricingEnterpriseDesc"),
      features: [
        t("pricingEnterpriseFeature1"),
        t("pricingEnterpriseFeature2"),
        t("pricingEnterpriseFeature3"),
        t("pricingEnterpriseFeature4"),
      ],
      cta: t("pricingContact"),
      highlighted: false,
    },
  ];

  return (
    <section className="bg-muted/50 relative py-20 md:py-32">
      <div className="container mx-auto px-4">
        {/* Section header */}
        <div className="mx-auto mb-16 max-w-2xl text-center">
          <p className="text-primary mb-4 text-sm font-medium tracking-wider uppercase">
            {t("pricingLabel")}
          </p>
          <h2 className="text-foreground mb-4 text-3xl font-bold tracking-tight md:text-4xl">
            {t("pricingTitle")}
          </h2>
          <p className="text-muted-foreground text-lg">{t("pricingSubtitle")}</p>
        </div>

        {/* Pricing cards */}
        <div className="mx-auto grid max-w-5xl gap-8 lg:grid-cols-3">
          {plans.map((plan, i) => (
            <div
              key={i}
              className={`bg-card relative rounded-2xl border p-6 ${
                plan.highlighted ? "border-primary ring-primary/20 shadow-xl ring-2" : "shadow-sm"
              }`}
            >
              {plan.highlighted && (
                <div className="bg-primary text-primary-foreground absolute -top-4 left-1/2 -translate-x-1/2 rounded-full px-4 py-1 text-sm font-medium">
                  {t("pricingPopular")}
                </div>
              )}

              <div className="mb-6">
                <h3 className="text-foreground mb-2 text-xl font-semibold">{plan.name}</h3>
                <div className="flex items-baseline gap-1">
                  <span className="text-foreground text-4xl font-bold">{plan.price}</span>
                  {plan.period && <span className="text-muted-foreground">/{plan.period}</span>}
                </div>
                <p className="text-muted-foreground mt-2 text-sm">{plan.description}</p>
              </div>

              <ul className="mb-6 space-y-3">
                {plan.features.map((feature, j) => (
                  <li key={j} className="flex items-start gap-2">
                    <IconCheck className="text-success mt-0.5 h-5 w-5 shrink-0" />
                    <span className="text-foreground text-sm">{feature}</span>
                  </li>
                ))}
              </ul>

              <Button
                className="w-full"
                variant={plan.highlighted ? "default" : "outline"}
                render={<Link href="/register" />}
              >
                {plan.cta}
              </Button>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export function CTASection() {
  const t = useTranslations("Landing");

  return (
    <section className="relative py-20 md:py-32">
      <div className="container mx-auto px-4">
        <div className="bg-primary relative overflow-hidden rounded-3xl p-8 md:p-16">
          {/* Background decorations */}
          <div className="absolute -top-24 -right-24 h-96 w-96 rounded-full bg-white/10 blur-3xl" />
          <div className="absolute -bottom-24 -left-24 h-96 w-96 rounded-full bg-white/5 blur-3xl" />

          <div className="relative mx-auto max-w-2xl text-center">
            <h2 className="text-primary-foreground mb-4 text-3xl font-bold tracking-tight md:text-4xl">
              {t("ctaTitle")}
            </h2>
            <p className="text-primary-foreground/80 mb-8 text-lg">{t("ctaSubtitle")}</p>
            <div className="flex flex-wrap justify-center gap-4">
              <Button
                size="lg"
                variant="secondary"
                className="gap-2"
                render={<Link href="/register" />}
              >
                {t("ctaButton")}
                <IconArrowRight className="h-4 w-4" />
              </Button>
            </div>
            <p className="text-primary-foreground/60 mt-4 text-sm">{t("ctaNoCard")}</p>
          </div>
        </div>
      </div>
    </section>
  );
}
