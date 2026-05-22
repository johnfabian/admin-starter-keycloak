import { RouteErrorBoundary } from "~/components/error-page";
import { UsersDashboardPage } from "~/pages/users-dashboard-page";
import { appInfo } from "~/lib/app-settings.shared";
import { requireAuthenticatedRoute } from "~/lib/server/route-guards.server";
import type { Route } from "./+types/users-dashboard";

export function meta() {
  return [{ title: `${appInfo.pageTitles.usersDashboard} | ${appInfo.name}` }];
}

export async function loader({ request }: Route.LoaderArgs) {
  return {
    user: await requireAuthenticatedRoute(request),
  };
}

export default function UsersDashboard({ loaderData }: Route.ComponentProps) {
  return <UsersDashboardPage user={loaderData.user} />;
}

export function ErrorBoundary({ error }: Route.ErrorBoundaryProps) {
  return <RouteErrorBoundary error={error} />;
}
