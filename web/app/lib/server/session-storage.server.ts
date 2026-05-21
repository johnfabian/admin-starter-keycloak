import { createCookieSessionStorage } from "react-router";

import { getAuthConfig } from "~/lib/server/auth-config.server";
import type { CurrentUser } from "~/models/current-user";

interface SessionData {
  state: string;
  codeVerifier: string;
  returnTo: string;
  user: CurrentUser;
}

type SessionStorage = ReturnType<typeof createCookieSessionStorage<Partial<SessionData>>>;
type Session = Awaited<ReturnType<SessionStorage["getSession"]>>;

let sessionStorage: SessionStorage | undefined;

function getSessionStorage() {
  sessionStorage ??= createCookieSessionStorage<Partial<SessionData>>({
    cookie: {
      name: "__admin_starter_session",
      httpOnly: true,
      path: "/",
      sameSite: "lax",
      secrets: [getAuthConfig().sessionSecret],
      secure: process.env.NODE_ENV === "production",
    },
  });

  return sessionStorage;
}

export function getSession(cookieHeader: string | null) {
  return getSessionStorage().getSession(cookieHeader);
}

export function commitSession(session: Session) {
  return getSessionStorage().commitSession(session);
}

export function destroySession(session: Session) {
  return getSessionStorage().destroySession(session);
}
