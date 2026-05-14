import { appAccessAreas } from "~/lib/app-settings";
import { getAccessRoles, type AppAccessArea } from "~/lib/auth-policy";
import { requireAnyRole, requireUser } from "~/lib/auth.server";

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
