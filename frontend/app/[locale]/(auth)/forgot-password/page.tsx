/**
 * Forgot Password Page
 * Request password reset via email
 */

"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/hooks/useAuth";
import { Link } from "@/i18n/navigation";
import { useTranslations } from "next-intl";
import { useState } from "react";

export default function ForgotPasswordPage() {
  const t = useTranslations("Auth");
  const tCommon = useTranslations("Common");
  const { forgotPassword, isLoading } = useAuth();
  const [email, setEmail] = useState("");
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!email) {
      setError(t("emailRequired"));
      return;
    }

    if (!/\S+@\S+\.\S+/.test(email)) {
      setError(t("invalidEmail"));
      return;
    }

    try {
      await forgotPassword(email);
      setIsSubmitted(true);
    } catch (err) {
      console.error("Forgot password error:", err);
      // Don't reveal if email exists - always show success for security
      setIsSubmitted(true);
    }
  };

  if (isSubmitted) {
    return (
      <div className="space-y-6">
        <div className="text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-green-100">
            <svg
              className="h-6 w-6 text-green-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            {t("checkYourEmail")}
          </h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            {t("resetEmailSent", { email })}
          </p>
        </div>

        <div className="space-y-4">
          <p className="text-center text-sm text-gray-500">{t("didNotReceiveEmail")}</p>
          <Button
            type="button"
            variant="outline"
            className="w-full"
            onClick={() => setIsSubmitted(false)}
          >
            {t("tryAgain")}
          </Button>
        </div>

        <div className="text-center">
          <Link
            href="/login"
            className="text-sm font-medium text-blue-600 hover:text-blue-500 dark:text-blue-400"
          >
            {t("backToLogin")}
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          {t("forgotPasswordTitle")}
        </h2>
        <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
          {t("forgotPasswordDescription")}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="email">{t("email")}</Label>
          <Input
            id="email"
            name="email"
            type="email"
            placeholder="votre.email@exemple.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            disabled={isLoading}
          />
          {error && <p className="text-sm text-red-600">{error}</p>}
        </div>

        <Button type="submit" className="w-full" disabled={isLoading}>
          {isLoading ? tCommon("loading") : t("sendResetLink")}
        </Button>
      </form>

      <div className="text-center">
        <Link
          href="/login"
          className="text-sm font-medium text-blue-600 hover:text-blue-500 dark:text-blue-400"
        >
          {t("backToLogin")}
        </Link>
      </div>
    </div>
  );
}
