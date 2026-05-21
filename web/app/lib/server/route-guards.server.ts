import { appAccessAreas } from "~/lib/app-settings.shared";
import { getAccessRoles, type AppAccessArea } from "~/lib/auth-policy.shared";
import { requireAnyRole, requireUser } from "~/lib/server/auth.server";

export async function requireAuthenticatedRoute(request: Request) {
  return requireUser(request);
}

export async function requireAccessRoute(request: Request, area: AppAccessArea) {
  return requireAnyRole(request, getAccessRoles(area));
}

export async function requireAdminRoute(request: Request) {
  return requireAccessRoute(request, appAccessAreas.adminRoutes);
}

export async function requireUserRoute(request: Request) {
  return requireAccessRoute(request, appAccessAreas.userRoutes);
}
