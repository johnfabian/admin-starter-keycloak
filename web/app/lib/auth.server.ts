import crypto from "node:crypto";

import { createRemoteJWKSet, jwtVerify, type JWTPayload } from "jose";
import { createCookieSessionStorage, redirect } from "react-router";

import { appRoutes } from "~/lib/app-settings";
import { getAuthConfig, getIssuerUrl } from "~/lib/auth-config.server";
import { hasAnyRole, hasRole } from "~/lib/auth-policy";
import type { CurrentUser } from "~/models/current-user";

interface SessionData {
  state: string;
  codeVerifier: string;
  returnTo: string;
  user: CurrentUser;
}

interface TokenResponse {
  access_token: string;
  id_token: string;
}

const sessionStorage = createCookieSessionStorage<Partial<SessionData>>({
  cookie: {
    name: "__admin_starter_session",
    httpOnly: true,
    path: "/",
    sameSite: "lax",
    secrets: [getAuthConfig().sessionSecret],
    secure: process.env.NODE_ENV === "production",
  },
});

const { getSession, commitSession, destroySession } = sessionStorage;

function base64Url(buffer: Buffer) {
  return buffer.toString("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}

function randomToken() {
  return base64Url(crypto.randomBytes(32));
}

function createCodeChallenge(codeVerifier: string) {
  return base64Url(crypto.createHash("sha256").update(codeVerifier).digest());
}

function getRequestPath(request: Request) {
  const url = new URL(request.url);
  return `${url.pathname}${url.search}`;
}

function normalizeReturnTo(returnTo: string | null) {
  const { postLoginRedirectUri } = getAuthConfig();
  if (!returnTo) return new URL(postLoginRedirectUri).pathname;

  try {
    const parsed = new URL(returnTo, postLoginRedirectUri);
    if (parsed.origin !== new URL(postLoginRedirectUri).origin) {
      return new URL(postLoginRedirectUri).pathname;
    }

    return `${parsed.pathname}${parsed.search}`;
  } catch {
    return new URL(postLoginRedirectUri).pathname;
  }
}

function getStringClaim(payload: JWTPayload, key: string) {
  const value = payload[key];
  return typeof value === "string" ? value : "";
}

function getRoles(payload: JWTPayload) {
  const { clientId } = getAuthConfig();
  const resourceAccess = payload.resource_access;
  if (!resourceAccess || typeof resourceAccess !== "object") return [];

  const clientAccess = (resourceAccess as Record<string, unknown>)[clientId];
  if (!clientAccess || typeof clientAccess !== "object") return [];

  const roles = (clientAccess as Record<string, unknown>).roles;
  if (!Array.isArray(roles)) return [];

  return roles.filter((role): role is string => typeof role === "string");
}

function buildCurrentUser(idPayload: JWTPayload, accessPayload: JWTPayload): CurrentUser {
  const firstName = getStringClaim(idPayload, "given_name");
  const lastName = getStringClaim(idPayload, "family_name");
  const preferredUsername = getStringClaim(idPayload, "preferred_username");
  const name =
    getStringClaim(idPayload, "name") ||
    [firstName, lastName].filter(Boolean).join(" ") ||
    preferredUsername ||
    getStringClaim(idPayload, "email");

  return {
    id: idPayload.sub || "",
    firstName,
    lastName,
    name,
    email: getStringClaim(idPayload, "email"),
    image: getStringClaim(idPayload, "picture") || null,
    roles: getRoles(accessPayload),
  };
}

async function verifyToken(token: string, expectedAudience?: string) {
  const { issuer } = getAuthConfig();
  const jwks = createRemoteJWKSet(new URL(getIssuerUrl("/protocol/openid-connect/certs")));
  const result = await jwtVerify(token, jwks, {
    issuer,
    audience: expectedAudience,
  });

  return result.payload;
}

export async function getCurrentUser(request: Request): Promise<CurrentUser | null> {
  const session = await getSession(request.headers.get("Cookie"));
  return session.get("user") ?? null;
}

export async function requireUser(request: Request): Promise<CurrentUser> {
  const user = await getCurrentUser(request);
  if (!user) {
    throw redirect(
      `${appRoutes.authLogin}?returnTo=${encodeURIComponent(getRequestPath(request))}`
    );
  }

  return user;
}

export async function requireRole(request: Request, role: string): Promise<CurrentUser> {
  const user = await requireUser(request);
  if (!hasRole(user, role)) {
    throw redirect(appRoutes.forbidden);
  }

  return user;
}

export async function requireAnyRole(request: Request, roles: string[]): Promise<CurrentUser> {
  const user = await requireUser(request);
  if (!hasAnyRole(user, roles)) {
    throw redirect(appRoutes.forbidden);
  }

  return user;
}

export async function redirectToLogin(request: Request, action?: "register") {
  const { clientId, redirectUri } = getAuthConfig();
  const session = await getSession(request.headers.get("Cookie"));
  const url = new URL(request.url);
  const state = randomToken();
  const codeVerifier = randomToken();
  const returnTo = normalizeReturnTo(url.searchParams.get("returnTo"));
  const prompt = url.searchParams.get("prompt");

  session.set("state", state);
  session.set("codeVerifier", codeVerifier);
  session.set("returnTo", returnTo);

  const authorizationUrl = new URL(getIssuerUrl("/protocol/openid-connect/auth"));
  authorizationUrl.searchParams.set("client_id", clientId);
  authorizationUrl.searchParams.set("redirect_uri", redirectUri);
  authorizationUrl.searchParams.set("response_type", "code");
  authorizationUrl.searchParams.set("scope", "openid profile email");
  authorizationUrl.searchParams.set("state", state);
  authorizationUrl.searchParams.set("code_challenge", createCodeChallenge(codeVerifier));
  authorizationUrl.searchParams.set("code_challenge_method", "S256");

  if (action === "register") {
    authorizationUrl.searchParams.set("kc_action", "register");
  }

  if (prompt === "login") {
    authorizationUrl.searchParams.set("prompt", "login");
  }

  throw redirect(authorizationUrl.toString(), {
    headers: {
      "Set-Cookie": await commitSession(session),
    },
  });
}

export async function completeLogin(request: Request) {
  const { clientId, clientSecret, redirectUri, postLoginRedirectUri } = getAuthConfig();
  const session = await getSession(request.headers.get("Cookie"));
  const url = new URL(request.url);
  const code = url.searchParams.get("code");
  const state = url.searchParams.get("state");
  const expectedState = session.get("state");
  const codeVerifier = session.get("codeVerifier");
  const returnTo = session.get("returnTo") || new URL(postLoginRedirectUri).pathname;

  if (!code || !state || !expectedState || !codeVerifier || state !== expectedState) {
    throw new Response("Invalid authentication callback.", { status: 400 });
  }

  const body = new URLSearchParams({
    client_id: clientId,
    code,
    code_verifier: codeVerifier,
    grant_type: "authorization_code",
    redirect_uri: redirectUri,
  });

  if (clientSecret) {
    body.set("client_secret", clientSecret);
  }

  const tokenResponse = await fetch(getIssuerUrl("/protocol/openid-connect/token"), {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body,
  });

  if (!tokenResponse.ok) {
    throw new Response("Could not complete authentication with Keycloak.", {
      status: 502,
    });
  }

  const tokens = (await tokenResponse.json()) as TokenResponse;
  const idPayload = await verifyToken(tokens.id_token, clientId);
  const accessPayload = await verifyToken(tokens.access_token);
  const user = buildCurrentUser(idPayload, accessPayload);

  if (!user.id) {
    throw new Response("Authenticated user is missing a subject claim.", {
      status: 502,
    });
  }

  session.unset("state");
  session.unset("codeVerifier");
  session.unset("returnTo");
  session.set("user", user);

  throw redirect(returnTo, {
    headers: {
      "Set-Cookie": await commitSession(session),
    },
  });
}

export async function logout(request: Request) {
  const { postLogoutRedirectUri } = getAuthConfig();
  const session = await getSession(request.headers.get("Cookie"));

  throw redirect(postLogoutRedirectUri, {
    headers: {
      "Set-Cookie": await destroySession(session),
    },
  });
}
