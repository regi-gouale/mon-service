/**
 * Verify Email Page
 * Verify user email with token from email link
 */

"use client";

import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { Link } from "@/i18n/navigation";
import { IconCheck, IconLoader2, IconX } from "@tabler/icons-react";
import { useTranslations } from "next-intl";
import { useSearchParams } from "next/navigation";
import { Suspense, startTransition, useCallback, useEffect, useRef, useState } from "react";

function VerifyEmailContent() {
  const t = useTranslations("Auth");
  const { verifyEmail, isLoading } = useAuth();
  const searchParams = useSearchParams();
  const token = searchParams.get("token");

  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [errorMessage, setErrorMessage] = useState("");
  const hasVerifiedRef = useRef(false);

  const verify = useCallback(async () => {
    if (!token) {
      startTransition(() => {
        setStatus("error");
        setErrorMessage(t("invalidVerificationLink"));
      });
      return;
    }

    try {
      await verifyEmail(token);
      startTransition(() => {
        setStatus("success");
      });
    } catch (err) {
      startTransition(() => {
        setStatus("error");
        setErrorMessage(t("verificationFailed"));
      });
      console.error("Email verification error:", err);
    }
  }, [token, verifyEmail, t]);

  useEffect(() => {
    if (!hasVerifiedRef.current) {
      hasVerifiedRef.current = true;
      void verify();
    }
  }, [verify]);

  if (status === "loading" || isLoading) {
    return (
      <div className="space-y-6 text-center">
        <IconLoader2 className="text-primary mx-auto h-12 w-12 animate-spin" />
        <h2 className="text-foreground text-2xl font-bold">{t("verifyingEmail")}</h2>
        <p className="text-muted-foreground text-sm">{t("pleaseWait")}</p>
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="space-y-6">
        <div className="text-center">
          <div className="bg-destructive/10 mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full">
            <IconX className="text-destructive h-6 w-6" />
          </div>
          <h2 className="text-foreground text-2xl font-bold">{t("verificationFailed")}</h2>
          <p className="text-muted-foreground mt-2 text-sm">{errorMessage}</p>
        </div>

        <div className="space-y-3">
          <Button onClick={() => verify()} className="w-full" variant="outline">
            {t("tryAgain")}
          </Button>
          <Link href="/login" className="block">
            <Button variant="ghost" className="w-full">
              {t("backToLogin")}
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-green-500/10">
          <IconCheck className="h-6 w-6 text-green-600" />
        </div>
        <h2 className="text-foreground text-2xl font-bold">{t("emailVerified")}</h2>
        <p className="text-muted-foreground mt-2 text-sm">{t("emailVerifiedDescription")}</p>
      </div>

      <Link href="/login" className="block">
        <Button className="w-full">{t("continueToLogin")}</Button>
      </Link>
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense
      fallback={
        <div className="flex justify-center p-8">
          <IconLoader2 className="text-primary h-8 w-8 animate-spin" />
        </div>
      }
    >
      <VerifyEmailContent />
    </Suspense>
  );
}
