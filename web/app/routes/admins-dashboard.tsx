import { RouteErrorBoundary } from "~/components/error-page";
import { AdminsDashboardPage } from "~/pages/admins-dashboard-page";
import { appInfo } from "~/lib/app-settings.shared";
import { requireAdminRoute } from "~/lib/server/route-guards.server";
import type { Route } from "./+types/admins-dashboard";

export function meta() {
  return [{ title: `${appInfo.pageTitles.adminsDashboard} | ${appInfo.name}` }];
}

export async function loader({ request }: Route.LoaderArgs) {
  return {
    user: await requireAdminRoute(request),
  };
}

export default function AdminsDashboard({ loaderData }: Route.ComponentProps) {
  return <AdminsDashboardPage user={loaderData.user} />;
}

export function ErrorBoundary({ error }: Route.ErrorBoundaryProps) {
  return <RouteErrorBoundary error={error} />;
}
