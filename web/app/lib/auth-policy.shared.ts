import { appAccess } from "~/lib/app-settings.shared";
import type { CurrentUser } from "~/models/current-user";

export type AppAccessArea = keyof typeof appAccess;

export function getAccessRoles(area: AppAccessArea) {
  return [...appAccess[area]];
}

export function hasRole(user: CurrentUser, role: string) {
  return user.roles.includes(role);
}

export function hasAnyRole(user: CurrentUser, roles: readonly string[]) {
  return roles.some((role) => hasRole(user, role));
}

export function hasAccess(user: CurrentUser, area: AppAccessArea) {
  return hasAnyRole(user, getAccessRoles(area));
}
