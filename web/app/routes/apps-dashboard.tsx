import { LayoutDashboard } from "lucide-react";

import { DashboardPlaceholderPage } from "~/pages/dashboard-placeholder-page";
import { appInfo } from "~/lib/app-settings.shared";
import { requireAuthenticatedRoute } from "~/lib/server/route-guards.server";
import type { Route } from "./+types/apps-dashboard";

export function meta() {
  return [{ title: `${appInfo.pageTitles.appsDashboard} | ${appInfo.name}` }];
}

export async function loader({ request }: Route.LoaderArgs) {
  return {
    user: await requireAuthenticatedRoute(request),
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
