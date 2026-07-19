import { redirect } from "react-router";

import { RouteErrorBoundary } from "~/components/error-page";
import { appRoutes } from "~/lib/app-settings.shared";
import { getNoStoreHeaders } from "~/lib/security-headers.shared";
import { logout } from "~/lib/server/auth.server";
import type { Route } from "./+types/auth-logout";

export async function loader({ request }: Route.LoaderArgs) {
  if (request.method !== "GET") {
    throw new Response("Method not allowed.", { status: 405 });
  }

  return redirect(appRoutes.home, { headers: getNoStoreHeaders() });
}

export async function action({ request }: Route.ActionArgs) {
  if (request.method !== "POST") {
    throw new Response("Method not allowed.", { status: 405 });
  }

  return logout(request);
}

export function ErrorBoundary({ error }: Route.ErrorBoundaryProps) {
  return <RouteErrorBoundary error={error} />;
}
