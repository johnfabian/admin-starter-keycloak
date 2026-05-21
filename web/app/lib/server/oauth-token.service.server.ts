import { createRemoteJWKSet, jwtVerify } from "jose";

import { getAuthConfig, getIssuerUrl } from "~/lib/server/auth-config.server";
import type { BffTokenSet } from "~/lib/server/bff-session.service.server";
import { getStringValue } from "~/lib/string-helper.shared";

interface TokenResponse {
  access_token: string;
  refresh_token?: string;
  id_token?: string;
  token_type?: string;
  scope?: string;
  expires_in?: number;
  refresh_expires_in?: number;
}

const TOKEN_SERVICE_CONFIG = {
  bearerTokenType: "Bearer",
  defaultAccessTokenSeconds: 300,
  fallbackRefreshLeewayMs: 60_000,
  formContentType: "application/x-www-form-urlencoded",
  grantTypes: {
    authorizationCode: "authorization_code",
    refreshToken: "refresh_token",
  },
  jwksPath: "/protocol/openid-connect/certs",
  tokenPath: "/protocol/openid-connect/token",
} as const;

let remoteJwks: ReturnType<typeof createRemoteJWKSet> | undefined;

function getRemoteJwks() {
  remoteJwks ??= createRemoteJWKSet(new URL(getIssuerUrl(TOKEN_SERVICE_CONFIG.jwksPath)));

  return remoteJwks;
}

export async function verifyToken(token: string, expectedAudience?: string) {
  const { issuer } = getAuthConfig();
  const result = await jwtVerify(token, getRemoteJwks(), {
    issuer,
    audience: expectedAudience,
  });

  return result.payload;
}

export function assertAccessTokenClient(payload: Awaited<ReturnType<typeof verifyToken>>) {
  const { clientId, resourceServerAudience } = getAuthConfig();

  if (resourceServerAudience) return;

  const authorizedParty = getStringValue(payload, "azp");
  if (authorizedParty !== clientId) {
    throw new Response("Access token was not issued to this web client.", { status: 502 });
  }
}

function getExpiry(secondsFromNow: number) {
  return new Date(Date.now() + secondsFromNow * 1000).toISOString();
}

function getOptionalExpiry(secondsFromNow: number | undefined, previous?: string | null) {
  if (typeof secondsFromNow === "number") {
    return secondsFromNow > 0 ? getExpiry(secondsFromNow) : null;
  }

  return previous ?? null;
}

export function createTokenSet(tokens: TokenResponse, previous?: BffTokenSet): BffTokenSet {
  if (!tokens.access_token) {
    throw new Response("Keycloak did not return an access token.", { status: 502 });
  }

  const refreshToken = tokens.refresh_token ?? previous?.refreshToken;
  const idToken = tokens.id_token ?? previous?.idToken;

  if (!refreshToken) {
    throw new Response("Keycloak did not return a refresh token.", { status: 502 });
  }

  if (!idToken) {
    throw new Response("Keycloak did not return an ID token.", { status: 502 });
  }

  return {
    accessToken: tokens.access_token,
    refreshToken,
    idToken,
    tokenType: tokens.token_type || previous?.tokenType || TOKEN_SERVICE_CONFIG.bearerTokenType,
    scope: tokens.scope || previous?.scope || "",
    accessTokenExpiresAt: getExpiry(
      tokens.expires_in ?? TOKEN_SERVICE_CONFIG.defaultAccessTokenSeconds
    ),
    refreshTokenExpiresAt: getOptionalExpiry(
      tokens.refresh_expires_in,
      previous?.refreshTokenExpiresAt
    ),
  };
}

export function shouldRefreshAccessToken(tokens: BffTokenSet) {
  const { tokenRefreshLeewaySeconds } = getAuthConfig();
  const leewayMs = Number.isFinite(tokenRefreshLeewaySeconds)
    ? tokenRefreshLeewaySeconds * 1000
    : TOKEN_SERVICE_CONFIG.fallbackRefreshLeewayMs;

  return new Date(tokens.accessTokenExpiresAt).getTime() - Date.now() <= leewayMs;
}

export function createTokenRequestBody(params: Record<string, string>) {
  const { clientId, clientSecret } = getAuthConfig();
  const body = new URLSearchParams({
    client_id: clientId,
    ...params,
  });

  if (clientSecret) {
    body.set("client_secret", clientSecret);
  }

  return body;
}

export async function requestToken(body: URLSearchParams) {
  const tokenResponse = await fetch(getIssuerUrl(TOKEN_SERVICE_CONFIG.tokenPath), {
    method: "POST",
    headers: {
      "Content-Type": TOKEN_SERVICE_CONFIG.formContentType,
    },
    body,
  });

  if (!tokenResponse.ok) {
    return null;
  }

  return (await tokenResponse.json()) as TokenResponse;
}

export function createAuthorizationCodeParams(code: string, codeVerifier: string, redirectUri: string) {
  return {
    code,
    code_verifier: codeVerifier,
    grant_type: TOKEN_SERVICE_CONFIG.grantTypes.authorizationCode,
    redirect_uri: redirectUri,
  };
}

export function createRefreshTokenParams(refreshToken: string) {
  return {
    grant_type: TOKEN_SERVICE_CONFIG.grantTypes.refreshToken,
    refresh_token: refreshToken,
  };
}
