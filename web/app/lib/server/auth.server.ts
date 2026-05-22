import { redirect } from "react-router";

import { appRoutes } from "~/lib/app-settings.shared";
import { hasAnyRole, hasRole } from "~/lib/auth-policy.shared";
import {
  assertSameOriginPost,
  getRequestPath,
  normalizeReturnTo,
} from "~/lib/server/auth-request.server";
import {
  createBffSession,
  deleteBffSession,
  getBffSession,
  updateBffSession,
  type BffSession,
} from "~/lib/server/bff-session.service.server";
import { getAuthConfig, getIssuerUrl, hasAuthConfig } from "~/lib/server/auth-config.server";
import {
  buildCurrentUser,
  getRolesFromTokenPayload,
} from "~/lib/server/current-user.server";
import {
  assertAccessTokenClient,
  createAuthorizationCodeParams,
  createRefreshTokenParams,
  createTokenRequestBody,
  createTokenSet,
  isTokenServiceUnavailable,
  isUserDisabledTokenError,
  requestTokenResult,
  shouldRefreshAccessToken,
  verifyToken,
} from "~/lib/server/oauth-token.service.server";
import {
  createCodeChallenge,
  createRandomToken,
  pkceCodeChallengeMethod,
} from "~/lib/server/oauth-pkce.server";
import { commitSession, destroySession, getSession } from "~/lib/server/session-storage.server";
import type { CurrentUser } from "~/models/current-user";

const AUTH_FLOW_CONFIG = {
  authorizationPath: "/protocol/openid-connect/auth",
  registrationPath: "/protocol/openid-connect/registrations",
  logoutPath: "/protocol/openid-connect/logout",
  queryParams: {
    clientId: "client_id",
    codeChallenge: "code_challenge",
    codeChallengeMethod: "code_challenge_method",
    idTokenHint: "id_token_hint",
    postLogoutRedirectUri: "post_logout_redirect_uri",
    prompt: "prompt",
    redirectUri: "redirect_uri",
    responseType: "response_type",
    returnTo: "returnTo",
    scope: "scope",
    state: "state",
  },
  responseTypes: {
    code: "code",
  },
  scopes: {
    defaultLogin: "openid profile email",
  },
  sessionKeys: {
    codeVerifier: "codeVerifier",
    returnTo: "returnTo",
    sessionId: "sessionId",
  },
  actions: {
    register: "register",
  },
  values: {
    promptLogin: "login",
  },
} as const;

type AuthAction = typeof AUTH_FLOW_CONFIG.actions.register;

const AUTH_ERROR_CONFIG = {
  keycloakUnavailableMessage: "Authentication service is temporarily unavailable.",
  keycloakUnavailableStatus: 503,
  tokenFailureStatus: 502,
  recoverableTokenErrorCodes: new Set([
    "ERR_JWS_SIGNATURE_VERIFICATION_FAILED",
    "ERR_JWT_EXPIRED",
    "ERR_JWT_INVALID",
  ]),
} as const;

function clearAuthAttempt(session: Awaited<ReturnType<typeof getSession>>) {
  session.unset(AUTH_FLOW_CONFIG.queryParams.state);
  session.unset(AUTH_FLOW_CONFIG.sessionKeys.codeVerifier);
  session.unset(AUTH_FLOW_CONFIG.sessionKeys.returnTo);
}

function getErrorCode(error: unknown) {
  if (!error || typeof error !== "object" || !("code" in error)) return null;

  const code = (error as { code: unknown }).code;
  return typeof code === "string" ? code : null;
}

export function isRecoverableSessionError(error: unknown) {
  if (error instanceof SyntaxError) return true;

  const code = getErrorCode(error);
  return Boolean(code && AUTH_ERROR_CONFIG.recoverableTokenErrorCodes.has(code));
}

export async function clearBffSessionBestEffort(sessionId: string) {
  try {
    await deleteBffSession(sessionId);
  } catch {
    // Logout and session recovery must still clear the browser cookie.
  }
}

function throwKeycloakUnavailable() {
  throw new Response(AUTH_ERROR_CONFIG.keycloakUnavailableMessage, {
    status: AUTH_ERROR_CONFIG.keycloakUnavailableStatus,
  });
}

async function refreshSessionIfNeeded(session: BffSession) {
  if (!shouldRefreshAccessToken(session.tokens)) return session;

  const refreshResult = await requestTokenResult(
    createTokenRequestBody(createRefreshTokenParams(session.tokens.refreshToken))
  );

  if (!refreshResult.ok) {
    if (isTokenServiceUnavailable(refreshResult)) {
      throwKeycloakUnavailable();
    }

    await clearBffSessionBestEffort(session.id);
    return null;
  }

  try {
    const tokens = createTokenSet(refreshResult.tokens, session.tokens);
    const { resourceServerAudience } = getAuthConfig();
    const accessPayload = await verifyToken(
      tokens.accessToken,
      resourceServerAudience || undefined
    );
    assertAccessTokenClient(accessPayload);

    const user = {
      ...session.user,
      roles: getRolesFromTokenPayload(accessPayload),
    };
    if (accessPayload.sub && accessPayload.sub !== session.user.id) {
      await clearBffSessionBestEffort(session.id);
      return null;
    }

    const updatedSession = { ...session, tokens, user };
    await updateBffSession(updatedSession);

    return updatedSession;
  } catch (error) {
    if (!isRecoverableSessionError(error)) {
      throw error;
    }

    await clearBffSessionBestEffort(session.id);
    return null;
  }
}

export async function getCurrentSession(request: Request) {
  if (!hasAuthConfig()) return null;

  const cookieSession = await getSession(request.headers.get("Cookie"));
  const sessionId = cookieSession.get(AUTH_FLOW_CONFIG.sessionKeys.sessionId);

  if (!sessionId) return null;

  const session = await getBffSession(sessionId);
  if (!session) return null;

  return refreshSessionIfNeeded(session);
}

export async function getCurrentUser(request: Request): Promise<CurrentUser | null> {
  return (await getCurrentSession(request))?.user ?? null;
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

export async function redirectToLogin(request: Request, action?: AuthAction) {
  const { clientId, redirectUri } = getAuthConfig();
  const session = await getSession(request.headers.get("Cookie"));
  const url = new URL(request.url);
  const state = createRandomToken();
  const codeVerifier = createRandomToken();
  const returnTo = normalizeReturnTo(url.searchParams.get(AUTH_FLOW_CONFIG.queryParams.returnTo));
  const prompt = url.searchParams.get(AUTH_FLOW_CONFIG.queryParams.prompt);

  session.unset(AUTH_FLOW_CONFIG.sessionKeys.sessionId);
  session.set(AUTH_FLOW_CONFIG.queryParams.state, state);
  session.set(AUTH_FLOW_CONFIG.sessionKeys.codeVerifier, codeVerifier);
  session.set(AUTH_FLOW_CONFIG.sessionKeys.returnTo, returnTo);

  const authorizationUrl = new URL(
    getIssuerUrl(
      action === AUTH_FLOW_CONFIG.actions.register
        ? AUTH_FLOW_CONFIG.registrationPath
        : AUTH_FLOW_CONFIG.authorizationPath
    )
  );
  authorizationUrl.searchParams.set(AUTH_FLOW_CONFIG.queryParams.clientId, clientId);
  authorizationUrl.searchParams.set(AUTH_FLOW_CONFIG.queryParams.redirectUri, redirectUri);
  authorizationUrl.searchParams.set(
    AUTH_FLOW_CONFIG.queryParams.responseType,
    AUTH_FLOW_CONFIG.responseTypes.code
  );
  authorizationUrl.searchParams.set(
    AUTH_FLOW_CONFIG.queryParams.scope,
    AUTH_FLOW_CONFIG.scopes.defaultLogin
  );
  authorizationUrl.searchParams.set(AUTH_FLOW_CONFIG.queryParams.state, state);
  authorizationUrl.searchParams.set(
    AUTH_FLOW_CONFIG.queryParams.codeChallenge,
    createCodeChallenge(codeVerifier)
  );
  authorizationUrl.searchParams.set(
    AUTH_FLOW_CONFIG.queryParams.codeChallengeMethod,
    pkceCodeChallengeMethod
  );

  if (prompt === AUTH_FLOW_CONFIG.values.promptLogin) {
    authorizationUrl.searchParams.set(
      AUTH_FLOW_CONFIG.queryParams.prompt,
      AUTH_FLOW_CONFIG.values.promptLogin
    );
  }

  throw redirect(authorizationUrl.toString(), {
    headers: {
      "Set-Cookie": await commitSession(session),
    },
  });
}

export async function completeLogin(request: Request) {
  const { clientId, redirectUri, postLoginRedirectUri, resourceServerAudience } = getAuthConfig();
  const session = await getSession(request.headers.get("Cookie"));
  const url = new URL(request.url);
  const code = url.searchParams.get("code");
  const state = url.searchParams.get(AUTH_FLOW_CONFIG.queryParams.state);
  const expectedState = session.get(AUTH_FLOW_CONFIG.queryParams.state);
  const codeVerifier = session.get(AUTH_FLOW_CONFIG.sessionKeys.codeVerifier);
  const returnTo =
    session.get(AUTH_FLOW_CONFIG.sessionKeys.returnTo) || new URL(postLoginRedirectUri).pathname;

  if (!code || !state || !expectedState || !codeVerifier || state !== expectedState) {
    clearAuthAttempt(session);

    throw redirect(appRoutes.authLoginWithPrompt, {
      headers: {
        "Set-Cookie": await commitSession(session),
      },
    });
  }

  const tokenResult = await requestTokenResult(
    createTokenRequestBody(createAuthorizationCodeParams(code, codeVerifier, redirectUri))
  );

  if (!tokenResult.ok) {
    if (isTokenServiceUnavailable(tokenResult)) {
      throwKeycloakUnavailable();
    }

    if (isUserDisabledTokenError(tokenResult)) {
      clearAuthAttempt(session);

      throw redirect(appRoutes.authLoginWithPrompt, {
        headers: {
          "Set-Cookie": await commitSession(session),
        },
      });
    }

    throw new Response("Could not complete authentication with Keycloak.", {
      status: AUTH_ERROR_CONFIG.tokenFailureStatus,
    });
  }

  const tokens = createTokenSet(tokenResult.tokens);
  const idPayload = await verifyToken(tokens.idToken, clientId);
  const accessPayload = await verifyToken(tokens.accessToken, resourceServerAudience || undefined);
  assertAccessTokenClient(accessPayload);
  const user = buildCurrentUser(idPayload, accessPayload);

  if (!user.id) {
    throw new Response("Authenticated user is missing a subject claim.", {
      status: 502,
    });
  }

  const sessionId = await createBffSession(user, tokens);

  clearAuthAttempt(session);
  session.set(AUTH_FLOW_CONFIG.sessionKeys.sessionId, sessionId);

  throw redirect(returnTo, {
    headers: {
      "Set-Cookie": await commitSession(session),
    },
  });
}

export async function logout(request: Request) {
  assertSameOriginPost(request);

  const { clientId, postLogoutRedirectUri } = getAuthConfig();
  const cookieSession = await getSession(request.headers.get("Cookie"));
  const sessionId = cookieSession.get(AUTH_FLOW_CONFIG.sessionKeys.sessionId);
  let bffSession: BffSession | null = null;

  if (sessionId) {
    try {
      bffSession = await getBffSession(sessionId);
    } catch {
      bffSession = null;
    }
  }

  if (sessionId) {
    await clearBffSessionBestEffort(sessionId);
  }

  const logoutUrl = new URL(getIssuerUrl(AUTH_FLOW_CONFIG.logoutPath));
  logoutUrl.searchParams.set(AUTH_FLOW_CONFIG.queryParams.clientId, clientId);
  logoutUrl.searchParams.set(
    AUTH_FLOW_CONFIG.queryParams.postLogoutRedirectUri,
    postLogoutRedirectUri
  );

  if (bffSession?.tokens.idToken) {
    logoutUrl.searchParams.set(AUTH_FLOW_CONFIG.queryParams.idTokenHint, bffSession.tokens.idToken);
  }

  throw redirect(logoutUrl.toString(), {
    headers: {
      "Set-Cookie": await destroySession(cookieSession),
    },
  });
}

export async function redirectToAccountConsole(request: Request) {
  await requireUser(request);
  throw redirect(getIssuerUrl("/account"));
}
