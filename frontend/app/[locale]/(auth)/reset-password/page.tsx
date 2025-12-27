/**
 * Reset Password Page
 * Set new password using reset token
 */

"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/hooks/useAuth";
import { Link } from "@/i18n/navigation";
import { IconCheck, IconLoader2, IconX } from "@tabler/icons-react";
import { useTranslations } from "next-intl";
import { useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";

function ResetPasswordForm() {
  const t = useTranslations("Auth");
  const tCommon = useTranslations("Common");
  const { resetPassword, isLoading } = useAuth();
  const searchParams = useSearchParams();
  const token = searchParams.get("token");

  const [formData, setFormData] = useState({
    password: "",
    confirmPassword: "",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSuccess, setIsSuccess] = useState(false);
  // Initialize invalid token state based on token presence
  const [isInvalidToken, setIsInvalidToken] = useState(!token);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.password) {
      newErrors.password = t("passwordRequired");
    } else if (formData.password.length < 8) {
      newErrors.password = t("passwordMin");
    }

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = t("passwordMismatch");
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm() || !token) {
      return;
    }

    try {
      await resetPassword(token, formData.password);
      setIsSuccess(true);
    } catch (err) {
      console.error("Reset password error:", err);
      setIsInvalidToken(true);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
    if (errors[e.target.name]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[e.target.name];
        return newErrors;
      });
    }
  };

  if (isInvalidToken) {
    return (
      <div className="space-y-6">
        <div className="text-center">
          <div className="bg-destructive/10 mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full">
            <IconX className="text-destructive h-6 w-6" />
          </div>
          <h2 className="text-foreground text-2xl font-bold">{t("invalidResetLink")}</h2>
          <p className="text-muted-foreground mt-2 text-sm">{t("invalidResetLinkDescription")}</p>
        </div>

        <Link href="/forgot-password" className="block">
          <Button variant="outline" className="w-full">
            {t("requestNewLink")}
          </Button>
        </Link>

        <div className="text-center">
          <Link href="/login" className="text-primary text-sm font-medium hover:underline">
            {t("backToLogin")}
          </Link>
        </div>
      </div>
    );
  }

  if (isSuccess) {
    return (
      <div className="space-y-6">
        <div className="text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-green-500/10">
            <IconCheck className="h-6 w-6 text-green-600" />
          </div>
          <h2 className="text-foreground text-2xl font-bold">{t("passwordResetSuccess")}</h2>
          <p className="text-muted-foreground mt-2 text-sm">
            {t("passwordResetSuccessDescription")}
          </p>
        </div>

        <Link href="/login" className="block">
          <Button className="w-full">{t("login")}</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-foreground text-2xl font-bold">{t("resetPasswordTitle")}</h2>
        <p className="text-muted-foreground mt-2 text-sm">{t("resetPasswordDescription")}</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="password">{t("newPassword")}</Label>
          <Input
            id="password"
            name="password"
            type="password"
            placeholder="••••••••"
            value={formData.password}
            onChange={handleChange}
            required
            disabled={isLoading}
          />
          {errors.password && <p className="text-destructive text-sm">{errors.password}</p>}
        </div>

        <div className="space-y-2">
          <Label htmlFor="confirmPassword">{t("confirmNewPassword")}</Label>
          <Input
            id="confirmPassword"
            name="confirmPassword"
            type="password"
            placeholder="••••••••"
            value={formData.confirmPassword}
            onChange={handleChange}
            required
            disabled={isLoading}
          />
          {errors.confirmPassword && (
            <p className="text-destructive text-sm">{errors.confirmPassword}</p>
          )}
        </div>

        <Button type="submit" className="w-full" disabled={isLoading}>
          {isLoading ? (
            <>
              <IconLoader2 className="mr-2 h-4 w-4 animate-spin" />
              {tCommon("loading")}
            </>
          ) : (
            t("resetPassword")
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

export default function ResetPasswordPage() {
  return (
    <Suspense
      fallback={
        <div className="flex justify-center p-8">
          <IconLoader2 className="text-primary h-8 w-8 animate-spin" />
        </div>
      }
    >
      <ResetPasswordForm />
    </Suspense>
  );
}
