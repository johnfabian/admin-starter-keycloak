import { trimTrailingSlash } from "~/lib/string-helper.shared";

const REQUIRED_AUTH_ENV = [
  "KEYCLOAK_ISSUER",
  "WEB_KEYCLOAK_CLIENT_ID",
  "WEB_AUTH_REDIRECT_URI",
  "WEB_AUTH_POST_LOGIN_REDIRECT_URI",
  "WEB_AUTH_POST_LOGOUT_REDIRECT_URI",
  "WEB_SESSION_SECRET",
  "WEB_DATABASE_URL",
  "WEB_TOKEN_ENCRYPTION_KEY",
] as const;

const AUTH_CONFIG_DEFAULTS = {
  minSecretLength: 32,
  sessionLastSeenUpdateSeconds: 300,
  tokenRefreshLeewaySeconds: 60,
} as const;

function requiredEnv(name: (typeof REQUIRED_AUTH_ENV)[number]) {
  const value = process.env[name];
  if (!value) {
    throw new Error(`${name} is required. Add it to .env.development for local dev.`);
  }

  return value;
}

function requiredSecretEnv(name: "WEB_SESSION_SECRET" | "WEB_TOKEN_ENCRYPTION_KEY") {
  const value = requiredEnv(name);

  if (value.length < AUTH_CONFIG_DEFAULTS.minSecretLength) {
    throw new Error(
      `${name} must be at least ${AUTH_CONFIG_DEFAULTS.minSecretLength} characters long.`
    );
  }

  return value;
}

function optionalEnv(name: string) {
  return process.env[name] || "";
}

function optionalNumberEnv(name: string, defaultValue: number) {
  const value = Number(process.env[name] || defaultValue);
  return Number.isFinite(value) && value > 0 ? value : defaultValue;
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
    sessionSecret: requiredSecretEnv("WEB_SESSION_SECRET"),
    databaseUrl: requiredEnv("WEB_DATABASE_URL"),
    tokenEncryptionKey: requiredSecretEnv("WEB_TOKEN_ENCRYPTION_KEY"),
    resourceServerBaseUrl: trimTrailingSlash(optionalEnv("WEB_RESOURCE_SERVER_BASE_URL")),
    resourceServerAudience: optionalEnv("WEB_KEYCLOAK_API_AUDIENCE"),
    tokenRefreshLeewaySeconds: optionalNumberEnv(
      "WEB_TOKEN_REFRESH_LEEWAY_SECONDS",
      AUTH_CONFIG_DEFAULTS.tokenRefreshLeewaySeconds
    ),
    sessionLastSeenUpdateSeconds: optionalNumberEnv(
      "WEB_SESSION_LAST_SEEN_UPDATE_SECONDS",
      AUTH_CONFIG_DEFAULTS.sessionLastSeenUpdateSeconds
    ),
  };
}

export function getIssuerUrl(pathname: string) {
  return `${getAuthConfig().issuer}${pathname}`;
}
