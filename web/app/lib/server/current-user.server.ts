import type { JWTPayload } from "jose";

import { getAuthConfig } from "~/lib/server/auth-config.server";
import { getStringValue, joinNonEmpty } from "~/lib/string-helper.shared";
import type { CurrentUser } from "~/models/current-user";

const TOKEN_ROLE_CLAIMS = {
  resourceAccess: "resource_access",
  roles: "roles",
} as const;

const USER_CLAIMS = {
  email: "email",
  familyName: "family_name",
  givenName: "given_name",
  name: "name",
  picture: "picture",
  preferredUsername: "preferred_username",
} as const;

export function getRolesFromTokenPayload(payload: JWTPayload) {
  const { clientId } = getAuthConfig();
  const resourceAccess = payload[TOKEN_ROLE_CLAIMS.resourceAccess];
  if (!resourceAccess || typeof resourceAccess !== "object") return [];

  const clientAccess = (resourceAccess as Record<string, unknown>)[clientId];
  if (!clientAccess || typeof clientAccess !== "object") return [];

  const roles = (clientAccess as Record<string, unknown>)[TOKEN_ROLE_CLAIMS.roles];
  if (!Array.isArray(roles)) return [];

  return roles.filter((role): role is string => typeof role === "string");
}

export function buildCurrentUser(idPayload: JWTPayload, accessPayload: JWTPayload): CurrentUser {
  const firstName = getStringValue(idPayload, USER_CLAIMS.givenName);
  const lastName = getStringValue(idPayload, USER_CLAIMS.familyName);
  const preferredUsername = getStringValue(idPayload, USER_CLAIMS.preferredUsername);
  const name =
    getStringValue(idPayload, USER_CLAIMS.name) ||
    joinNonEmpty([firstName, lastName]) ||
    preferredUsername ||
    getStringValue(idPayload, USER_CLAIMS.email);

  return {
    id: idPayload.sub || "",
    firstName,
    lastName,
    name,
    email: getStringValue(idPayload, USER_CLAIMS.email),
    image: getStringValue(idPayload, USER_CLAIMS.picture) || null,
    roles: getRolesFromTokenPayload(accessPayload),
  };
}
