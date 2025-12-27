import { routing } from "@/i18n/routing";
import { redirect } from "next/navigation";

/**
 * Root Page
 * Redirects to the default locale
 */
export default function RootPage() {
  redirect(`/${routing.defaultLocale}`);
}
