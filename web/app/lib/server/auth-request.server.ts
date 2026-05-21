import { getAuthConfig } from "~/lib/server/auth-config.server";

export function getRequestPath(request: Request) {
  const url = new URL(request.url);
  return `${url.pathname}${url.search}`;
}

export function normalizeReturnTo(returnTo: string | null) {
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

export function assertSameOriginPost(request: Request) {
  const origin = request.headers.get("Origin");
  if (!origin) return;

  if (origin !== new URL(request.url).origin) {
    throw new Response("Invalid logout origin.", { status: 403 });
  }
}
