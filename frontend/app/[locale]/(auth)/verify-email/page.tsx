/**
 * Verify Email Page
 * Verify user email with token from email link
 */

"use client";

import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { Link } from "@/i18n/navigation";
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
        <div className="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-blue-600 border-t-transparent"></div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">{t("verifyingEmail")}</h2>
        <p className="text-sm text-gray-600 dark:text-gray-400">{t("pleaseWait")}</p>
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="space-y-6">
        <div className="text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-red-100">
            <svg
              className="h-6 w-6 text-red-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            {t("verificationFailed")}
          </h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">{errorMessage}</p>
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
        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-green-100">
          <svg
            className="h-6 w-6 text-green-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">{t("emailVerified")}</h2>
        <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
          {t("emailVerifiedDescription")}
        </p>
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
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent"></div>
        </div>
      }
    >
      <VerifyEmailContent />
    </Suspense>
  );
}
