/**
 * Not Found Page
 * Displayed when a locale is not found
 */

import { IconArrowLeft, IconError404 } from "@tabler/icons-react";
import Link from "next/link";

export default function NotFound() {
  return (
    <html lang="fr">
      <body className="bg-background flex min-h-screen items-center justify-center">
        <div className="text-center">
          <IconError404 className="text-muted-foreground mx-auto h-16 w-16" />
          <h1 className="text-foreground mt-4 text-4xl font-bold">404</h1>
          <p className="text-muted-foreground mt-2">Page non trouvée</p>
          <Link
            href="/fr"
            className="text-primary mt-4 inline-flex items-center gap-2 hover:underline"
          >
            <IconArrowLeft className="h-4 w-4" />
            Retour à l&apos;accueil
          </Link>
        </div>
      </body>
    </html>
  );
}
