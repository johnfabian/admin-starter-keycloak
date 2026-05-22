import { Settings } from "lucide-react";

import { RouteErrorBoundary } from "~/components/error-page";
import { DashboardPlaceholderPage } from "~/pages/dashboard-placeholder-page";
import { appInfo } from "~/lib/app-settings.shared";
import { requireAuthenticatedRoute } from "~/lib/server/route-guards.server";
import type { Route } from "./+types/settings";

export function meta() {
  return [{ title: `${appInfo.pageTitles.settings} | ${appInfo.name}` }];
}

export async function loader({ request }: Route.LoaderArgs) {
  return {
    user: await requireAuthenticatedRoute(request),
  };
}

export default function SettingsPage({ loaderData }: Route.ComponentProps) {
  return (
    <DashboardPlaceholderPage
      user={loaderData.user}
      title={appInfo.pageTitles.settings}
      eyebrow="User"
      description="Application and account settings placeholders are ready for future controls."
      icon={Settings}
    />
  );
}

export function ErrorBoundary({ error }: Route.ErrorBoundaryProps) {
  return <RouteErrorBoundary error={error} />;
}
