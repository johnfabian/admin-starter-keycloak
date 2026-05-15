function requiredEnv(name: string) {
  const value = process.env[name];
  if (!value) {
    throw new Error(`${name} is required. Add it to .env.development for local dev.`);
  }

  return value;
}

function optionalEnv(name: string) {
  return process.env[name] || "";
}

export function getAuthConfig() {
  const issuer = requiredEnv("KEYCLOAK_ISSUER").replace(/\/$/, "");

  return {
    issuer,
    clientId: requiredEnv("KEYCLOAK_CLIENT_ID"),
    clientSecret: optionalEnv("KEYCLOAK_CLIENT_SECRET"),
    redirectUri: requiredEnv("AUTH_REDIRECT_URI"),
    postLoginRedirectUri: requiredEnv("AUTH_POST_LOGIN_REDIRECT_URI"),
    postLogoutRedirectUri: requiredEnv("AUTH_POST_LOGOUT_REDIRECT_URI"),
    sessionSecret: requiredEnv("SESSION_SECRET"),
  };
}

export function getIssuerUrl(pathname: string) {
  return `${getAuthConfig().issuer}${pathname}`;
}
