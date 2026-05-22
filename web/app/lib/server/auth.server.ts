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
  requestToken,
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
  logoutPath: "/protocol/openid-connect/logout",
  queryParams: {
    clientId: "client_id",
    codeChallenge: "code_challenge",
    codeChallengeMethod: "code_challenge_method",
    idTokenHint: "id_token_hint",
    keycloakAction: "kc_action",
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
  values: {
    promptLogin: "login",
    registerAction: "register",
  },
} as const;

type AuthAction = typeof AUTH_FLOW_CONFIG.values.registerAction;

async function refreshSessionIfNeeded(session: BffSession) {
  if (!shouldRefreshAccessToken(session.tokens)) return session;

  const refreshedTokens = await requestToken(
    createTokenRequestBody(createRefreshTokenParams(session.tokens.refreshToken))
  );

  if (!refreshedTokens) {
    await deleteBffSession(session.id);
    return null;
  }

  const tokens = createTokenSet(refreshedTokens, session.tokens);
  const { resourceServerAudience } = getAuthConfig();
  const accessPayload = await verifyToken(tokens.accessToken, resourceServerAudience || undefined);
  assertAccessTokenClient(accessPayload);

  const user = {
    ...session.user,
    roles: getRolesFromTokenPayload(accessPayload),
  };
  if (accessPayload.sub && accessPayload.sub !== session.user.id) {
    await deleteBffSession(session.id);
    return null;
  }

  const updatedSession = { ...session, tokens, user };
  await updateBffSession(updatedSession);

  return updatedSession;
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

  const authorizationUrl = new URL(getIssuerUrl(AUTH_FLOW_CONFIG.authorizationPath));
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

  if (action === AUTH_FLOW_CONFIG.values.registerAction) {
    authorizationUrl.searchParams.set(
      AUTH_FLOW_CONFIG.queryParams.keycloakAction,
      AUTH_FLOW_CONFIG.values.registerAction
    );
  }

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
    throw new Response("Invalid authentication callback.", { status: 400 });
  }

  const tokenResponse = await requestToken(
    createTokenRequestBody(createAuthorizationCodeParams(code, codeVerifier, redirectUri))
  );

  if (!tokenResponse) {
    throw new Response("Could not complete authentication with Keycloak.", {
      status: 502,
    });
  }

  const tokens = createTokenSet(tokenResponse);
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

  session.unset(AUTH_FLOW_CONFIG.queryParams.state);
  session.unset(AUTH_FLOW_CONFIG.sessionKeys.codeVerifier);
  session.unset(AUTH_FLOW_CONFIG.sessionKeys.returnTo);
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
  const bffSession = sessionId ? await getBffSession(sessionId) : null;

  if (sessionId) {
    await deleteBffSession(sessionId);
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
