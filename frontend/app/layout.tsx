/**
 * Root Layout
 * This layout handles the basic HTML structure.
 * The actual providers are in the [locale] layout.
 */

import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Mon Service",
  description: "Gérez vos équipes de service, plannings et disponibilités",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return children;
}
