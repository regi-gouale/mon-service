"use client";

import { Button } from "@/components/ui/button";
import { Link } from "@/i18n/navigation";
import {
  IconBrandFacebook,
  IconBrandInstagram,
  IconBrandTwitter,
  IconBrandYoutube,
  IconCalendarEvent,
  IconMenu2,
  IconMoon,
  IconSun,
  IconX,
} from "@tabler/icons-react";
import { useTranslations } from "next-intl";
import { useTheme } from "next-themes";
import { useState } from "react";

export function LandingHeader() {
  const t = useTranslations("Landing");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { theme, setTheme } = useTheme();

  const navItems = [
    { label: t("navFeatures"), href: "#features" },
    { label: t("navHowItWorks"), href: "#how-it-works" },
    { label: t("navPricing"), href: "#pricing" },
    { label: t("navTestimonials"), href: "#testimonials" },
  ];

  return (
    <header className="bg-background/95 supports-backdrop-filter:bg-background/60 sticky top-0 z-50 w-full border-b backdrop-blur">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2">
          <div className="bg-primary flex h-9 w-9 items-center justify-center rounded-lg">
            <IconCalendarEvent className="text-primary-foreground h-5 w-5" />
          </div>
          <span className="text-foreground text-xl font-bold">Mon Service</span>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden items-center gap-8 md:flex">
          {navItems.map((item) => (
            <a
              key={item.href}
              href={item.href}
              className="text-muted-foreground hover:text-foreground text-sm font-medium transition-colors"
            >
              {item.label}
            </a>
          ))}
        </nav>

        {/* Right side */}
        <div className="flex items-center gap-3">
          {/* Theme toggle */}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            className="hidden sm:flex"
          >
            <IconSun className="h-5 w-5 scale-100 rotate-0 transition-all dark:scale-0 dark:-rotate-90" />
            <IconMoon className="absolute h-5 w-5 scale-0 rotate-90 transition-all dark:scale-100 dark:rotate-0" />
            <span className="sr-only">Toggle theme</span>
          </Button>

          <Button variant="ghost" className="hidden sm:flex" render={<Link href="/login" />}>
            {t("navLogin")}
          </Button>
          <Button className="hidden sm:flex" render={<Link href="/register" />}>
            {t("navSignup")}
          </Button>

          {/* Mobile menu button */}
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <IconX className="h-5 w-5" /> : <IconMenu2 className="h-5 w-5" />}
          </Button>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileMenuOpen && (
        <div className="bg-background border-t md:hidden">
          <nav className="container mx-auto space-y-1 px-4 py-4">
            {navItems.map((item) => (
              <a
                key={item.href}
                href={item.href}
                className="text-muted-foreground hover:bg-muted hover:text-foreground block rounded-lg px-3 py-2 text-sm font-medium"
                onClick={() => setMobileMenuOpen(false)}
              >
                {item.label}
              </a>
            ))}
            <div className="flex gap-2 pt-4">
              <Button variant="outline" className="flex-1" render={<Link href="/login" />}>
                {t("navLogin")}
              </Button>
              <Button className="flex-1" render={<Link href="/register" />}>
                {t("navSignup")}
              </Button>
            </div>
          </nav>
        </div>
      )}
    </header>
  );
}

export function LandingFooter() {
  const t = useTranslations("Landing");
  const currentYear = new Date().getFullYear();

  const footerLinks = {
    product: [
      { label: t("footerFeatures"), href: "#features" },
      { label: t("footerPricing"), href: "#pricing" },
      { label: t("footerDemo"), href: "#" },
    ],
    resources: [
      { label: t("footerDocs"), href: "/docs" },
      { label: t("footerSupport"), href: "/support" },
      { label: t("footerBlog"), href: "/blog" },
    ],
    company: [
      { label: t("footerAbout"), href: "/about" },
      { label: t("footerContact"), href: "/contact" },
      { label: t("footerCareers"), href: "/careers" },
    ],
    legal: [
      { label: t("footerPrivacy"), href: "/privacy" },
      { label: t("footerTerms"), href: "/terms" },
    ],
  };

  const socialLinks = [
    { icon: IconBrandTwitter, href: "#", label: "Twitter" },
    { icon: IconBrandFacebook, href: "#", label: "Facebook" },
    { icon: IconBrandInstagram, href: "#", label: "Instagram" },
    { icon: IconBrandYoutube, href: "#", label: "YouTube" },
  ];

  return (
    <footer className="bg-muted/30 border-t">
      <div className="container mx-auto px-4 py-12">
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-5">
          {/* Brand column */}
          <div className="lg:col-span-2">
            <Link href="/" className="mb-4 flex items-center gap-2">
              <div className="bg-primary flex h-9 w-9 items-center justify-center rounded-lg">
                <IconCalendarEvent className="text-primary-foreground h-5 w-5" />
              </div>
              <span className="text-foreground text-xl font-bold">Mon Service</span>
            </Link>
            <p className="text-muted-foreground mb-4 max-w-sm text-sm">{t("footerDescription")}</p>
            {/* Social links */}
            <div className="flex gap-3">
              {socialLinks.map((social) => (
                <a
                  key={social.label}
                  href={social.href}
                  className="bg-muted text-muted-foreground hover:bg-primary hover:text-primary-foreground flex h-9 w-9 items-center justify-center rounded-lg transition-colors"
                  aria-label={social.label}
                >
                  <social.icon className="h-4 w-4" />
                </a>
              ))}
            </div>
          </div>

          {/* Product links */}
          <div>
            <h3 className="text-foreground mb-4 text-sm font-semibold">{t("footerProduct")}</h3>
            <ul className="space-y-2">
              {footerLinks.product.map((link) => (
                <li key={link.href}>
                  <a
                    href={link.href}
                    className="text-muted-foreground hover:text-foreground text-sm"
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Resources links */}
          <div>
            <h3 className="text-foreground mb-4 text-sm font-semibold">{t("footerResources")}</h3>
            <ul className="space-y-2">
              {footerLinks.resources.map((link) => (
                <li key={link.href}>
                  <a
                    href={link.href}
                    className="text-muted-foreground hover:text-foreground text-sm"
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Legal links */}
          <div>
            <h3 className="text-foreground mb-4 text-sm font-semibold">{t("footerLegal")}</h3>
            <ul className="space-y-2">
              {footerLinks.legal.map((link) => (
                <li key={link.href}>
                  <a
                    href={link.href}
                    className="text-muted-foreground hover:text-foreground text-sm"
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="mt-12 flex flex-col items-center justify-between gap-4 border-t pt-8 md:flex-row">
          <p className="text-muted-foreground text-sm">
            © {currentYear} Mon Service. {t("footerRights")}
          </p>
          <p className="text-muted-foreground text-sm">
            {t("footerMadeWith")} ❤️ {t("footerBy")}
          </p>
        </div>
      </div>
    </footer>
  );
}
