import { UserRound } from "lucide-react";

import { DashboardPlaceholderPage } from "~/pages/dashboard-placeholder-page";
import { appInfo } from "~/lib/app-settings.shared";
import { requireAuthenticatedRoute } from "~/lib/server/route-guards.server";
import type { Route } from "./+types/profile";

export function meta() {
  return [{ title: `${appInfo.pageTitles.profile} | ${appInfo.name}` }];
}

export async function loader({ request }: Route.LoaderArgs) {
  return {
    user: await requireAuthenticatedRoute(request),
  };
}

export default function Profile({ loaderData }: Route.ComponentProps) {
  return (
    <DashboardPlaceholderPage
      user={loaderData.user}
      title={appInfo.pageTitles.profile}
      eyebrow="User"
      description="Profile details and account preferences will live here."
      icon={UserRound}
    />
  );
}
