/**
 * Not Found Page
 * Displayed when a locale is not found
 */

import Link from "next/link";

export default function NotFound() {
  return (
    <html lang="fr">
      <body className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900">404</h1>
          <p className="mt-2 text-gray-600">Page non trouvée</p>
          <Link href="/fr" className="mt-4 inline-block text-blue-600 hover:underline">
            Retour à l&apos;accueil
          </Link>
        </div>
      </body>
    </html>
  );
}
