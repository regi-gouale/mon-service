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
import { IconCheck, IconLoader2 } from "@tabler/icons-react";
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
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-green-500/10">
            <IconCheck className="h-6 w-6 text-green-600" />
          </div>
          <h2 className="text-foreground text-2xl font-bold">{t("checkYourEmail")}</h2>
          <p className="text-muted-foreground mt-2 text-sm">{t("resetEmailSent", { email })}</p>
        </div>

        <div className="space-y-4">
          <p className="text-muted-foreground text-center text-sm">{t("didNotReceiveEmail")}</p>
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
          <Link href="/login" className="text-primary text-sm font-medium hover:underline">
            {t("backToLogin")}
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-foreground text-2xl font-bold">{t("forgotPasswordTitle")}</h2>
        <p className="text-muted-foreground mt-2 text-sm">{t("forgotPasswordDescription")}</p>
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
          {error && <p className="text-destructive text-sm">{error}</p>}
        </div>

        <Button type="submit" className="w-full" disabled={isLoading}>
          {isLoading ? (
            <>
              <IconLoader2 className="mr-2 h-4 w-4 animate-spin" />
              {tCommon("loading")}
            </>
          ) : (
            t("sendResetLink")
          )}
        </Button>
      </form>

      <div className="text-center">
        <Link href="/login" className="text-primary text-sm font-medium hover:underline">
          {t("backToLogin")}
        </Link>
      </div>
    </div>
  );
}
