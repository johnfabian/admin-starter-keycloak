import type { JWTPayload } from "jose";

import { getAuthConfig } from "~/lib/server/auth-config.server";
import { getStringValue, joinNonEmpty } from "~/lib/string-helper.shared";
import type { CurrentUser } from "~/models/current-user";

const TOKEN_ROLE_CLAIMS = {
  realmAccess: "realm_access",
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
  const realmAccess = payload[TOKEN_ROLE_CLAIMS.realmAccess];
  const resourceAccess = payload[TOKEN_ROLE_CLAIMS.resourceAccess];
  const realmRoles =
    realmAccess && typeof realmAccess === "object"
      ? getStringArrayClaim(realmAccess as Record<string, unknown>, TOKEN_ROLE_CLAIMS.roles)
      : [];

  if (!resourceAccess || typeof resourceAccess !== "object") return uniqueValues(realmRoles);

  const clientAccess = (resourceAccess as Record<string, unknown>)[clientId];
  if (!clientAccess || typeof clientAccess !== "object") return uniqueValues(realmRoles);

  return uniqueValues([
    ...realmRoles,
    ...getStringArrayClaim(clientAccess as Record<string, unknown>, TOKEN_ROLE_CLAIMS.roles),
  ]);
}

function getStringArrayClaim(payload: Record<string, unknown>, claim: string) {
  const value = payload[claim];
  return Array.isArray(value)
    ? value.filter((item): item is string => typeof item === "string")
    : [];
}

function uniqueValues(values: string[]) {
  return [...new Set(values)];
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
