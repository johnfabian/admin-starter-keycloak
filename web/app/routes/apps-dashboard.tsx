import { LayoutDashboard } from "lucide-react";

import { RouteErrorBoundary } from "~/components/error-page";
import { DashboardPlaceholderPage } from "~/pages/dashboard-placeholder-page";
import { appInfo } from "~/lib/app-settings.shared";
import { requireUserRoute } from "~/lib/server/route-guards.server";
import type { Route } from "./+types/apps-dashboard";

export function meta() {
  return [{ title: `${appInfo.pageTitles.appsDashboard} | ${appInfo.name}` }];
}

export async function loader({ request }: Route.LoaderArgs) {
  return {
    user: await requireUserRoute(request),
  };
}

export default function AppsDashboard({ loaderData }: Route.ComponentProps) {
  return (
    <DashboardPlaceholderPage
      user={loaderData.user}
      title={appInfo.pageTitles.appsDashboard}
      eyebrow="Apps"
      description="Browse and launch future application modules from this dashboard."
      icon={LayoutDashboard}
    />
  );
}

export function ErrorBoundary({ error }: Route.ErrorBoundaryProps) {
  return <RouteErrorBoundary error={error} />;
}
