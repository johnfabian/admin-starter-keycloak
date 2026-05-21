import { trimTrailingSlash } from "~/lib/string-helper.shared";

const REQUIRED_AUTH_ENV = [
  "KEYCLOAK_ISSUER",
  "WEB_KEYCLOAK_CLIENT_ID",
  "WEB_AUTH_REDIRECT_URI",
  "WEB_AUTH_POST_LOGIN_REDIRECT_URI",
  "WEB_AUTH_POST_LOGOUT_REDIRECT_URI",
  "WEB_SESSION_SECRET",
] as const;

function requiredEnv(name: (typeof REQUIRED_AUTH_ENV)[number]) {
  const value = process.env[name];
  if (!value) {
    throw new Error(`${name} is required. Add it to .env.development for local dev.`);
  }

  return value;
}

function optionalEnv(name: string) {
  return process.env[name] || "";
}

export function hasAuthConfig() {
  return REQUIRED_AUTH_ENV.every((name) => Boolean(process.env[name]));
}

export function getAuthConfig() {
  const issuer = trimTrailingSlash(requiredEnv("KEYCLOAK_ISSUER"));

  return {
    issuer,
    clientId: requiredEnv("WEB_KEYCLOAK_CLIENT_ID"),
    clientSecret: optionalEnv("WEB_KEYCLOAK_CLIENT_SECRET"),
    redirectUri: requiredEnv("WEB_AUTH_REDIRECT_URI"),
    postLoginRedirectUri: requiredEnv("WEB_AUTH_POST_LOGIN_REDIRECT_URI"),
    postLogoutRedirectUri: requiredEnv("WEB_AUTH_POST_LOGOUT_REDIRECT_URI"),
    sessionSecret: requiredEnv("WEB_SESSION_SECRET"),
  };
}

export function getIssuerUrl(pathname: string) {
  return `${getAuthConfig().issuer}${pathname}`;
}
