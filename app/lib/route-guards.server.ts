import { requireRole, requireUser } from "~/lib/auth.server";

export async function requireAuthenticatedRoute(request: Request) {
  return requireUser(request);
}

export async function requireAdminRoute(request: Request) {
  return requireRole(request, "Admins");
}
