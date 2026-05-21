import { getAuthConfig } from "~/lib/server/auth-config.server";
import { getCurrentSession } from "~/lib/server/auth.server";

const BFF_FETCH_CONFIG = {
  authorizationHeader: "Authorization",
  bearerTokenPrefix: "Bearer",
  missingAuthMessage: "Authentication required.",
  missingResourceServerMessage: "WEB_RESOURCE_SERVER_BASE_URL is not configured.",
  resourceServerPathSeparator: "/",
} as const;

function getResourceServerUrl(input: string | URL) {
  const { resourceServerBaseUrl } = getAuthConfig();

  if (!resourceServerBaseUrl) {
    throw new Response(BFF_FETCH_CONFIG.missingResourceServerMessage, { status: 500 });
  }

  return new URL(
    input.toString(),
    `${resourceServerBaseUrl}${BFF_FETCH_CONFIG.resourceServerPathSeparator}`
  );
}

export async function getAccessTokenForBff(request: Request) {
  const session = await getCurrentSession(request);

  if (!session) {
    throw new Response(BFF_FETCH_CONFIG.missingAuthMessage, { status: 401 });
  }

  return session.tokens.accessToken;
}

export async function bffFetch(request: Request, input: string | URL, init: RequestInit = {}) {
  const accessToken = await getAccessTokenForBff(request);
  const headers = new Headers(init.headers);

  // Tokens stay inside the React Router server; loader/action JSON must never echo them.
  headers.set(
    BFF_FETCH_CONFIG.authorizationHeader,
    `${BFF_FETCH_CONFIG.bearerTokenPrefix} ${accessToken}`
  );

  return fetch(getResourceServerUrl(input), {
    ...init,
    headers,
  });
}
