/**
 * Google OAuth Callback Route
 * Handles the callback from Google OAuth and exchanges the code for tokens
 */

import { NextRequest, NextResponse } from "next/server";

const GOOGLE_CLIENT_ID = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "";
const GOOGLE_CLIENT_SECRET = process.env.GOOGLE_CLIENT_SECRET || "";
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_VERSION = process.env.NEXT_PUBLIC_API_VERSION || "v1";

interface GoogleTokenResponse {
  access_token: string;
  id_token: string;
  expires_in: number;
  token_type: string;
  scope: string;
  refresh_token?: string;
}

interface BackendAuthResponse {
  user: {
    id: string;
    email: string;
    firstName: string;
    lastName: string;
    avatarUrl?: string;
    role: string;
    organizationId: string;
    isEmailVerified: boolean;
  };
  accessToken: string;
  refreshToken: string;
}

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const code = searchParams.get("code");
  const error = searchParams.get("error");

  // Base URL for redirect
  const baseUrl = request.nextUrl.origin;

  // Handle errors from Google
  if (error) {
    console.error("Google OAuth error:", error);
    return NextResponse.redirect(
      `${baseUrl}/login?error=${encodeURIComponent("Erreur lors de la connexion avec Google")}`
    );
  }

  // Validate required parameters
  if (!code) {
    return NextResponse.redirect(
      `${baseUrl}/login?error=${encodeURIComponent("Code d'autorisation manquant")}`
    );
  }

  // Validate Google client configuration
  if (!GOOGLE_CLIENT_ID || !GOOGLE_CLIENT_SECRET) {
    console.error("Google OAuth not configured");
    return NextResponse.redirect(
      `${baseUrl}/login?error=${encodeURIComponent("Google OAuth n'est pas configuré")}`
    );
  }

  try {
    // Exchange authorization code for tokens
    const redirectUri = `${baseUrl}/api/auth/callback/google`;
    const tokenResponse = await fetch("https://oauth2.googleapis.com/token", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({
        code,
        client_id: GOOGLE_CLIENT_ID,
        client_secret: GOOGLE_CLIENT_SECRET,
        redirect_uri: redirectUri,
        grant_type: "authorization_code",
      }),
    });

    if (!tokenResponse.ok) {
      const errorData = await tokenResponse.text();
      console.error("Failed to exchange code for tokens:", errorData);
      return NextResponse.redirect(
        `${baseUrl}/login?error=${encodeURIComponent("Erreur lors de l'échange du code")}`
      );
    }

    const tokens: GoogleTokenResponse = await tokenResponse.json();

    // Send ID token to backend for authentication
    const backendResponse = await fetch(`${API_URL}/api/${API_VERSION}/auth/google`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        id_token: tokens.id_token,
      }),
    });

    if (!backendResponse.ok) {
      const errorData = await backendResponse.text();
      console.error("Backend authentication failed:", errorData);
      return NextResponse.redirect(
        `${baseUrl}/login?error=${encodeURIComponent("Erreur d'authentification")}`
      );
    }

    const authData: BackendAuthResponse = await backendResponse.json();

    // Create response with redirect to dashboard
    // We'll pass the tokens as query parameters to be handled by the client
    const successUrl = new URL(`${baseUrl}/auth/callback`);
    successUrl.searchParams.set("accessToken", authData.accessToken);
    successUrl.searchParams.set("refreshToken", authData.refreshToken);
    successUrl.searchParams.set("user", JSON.stringify(authData.user));

    return NextResponse.redirect(successUrl.toString());
  } catch (error) {
    console.error("Google OAuth callback error:", error);
    return NextResponse.redirect(
      `${baseUrl}/login?error=${encodeURIComponent("Erreur inattendue lors de la connexion")}`
    );
  }
}
