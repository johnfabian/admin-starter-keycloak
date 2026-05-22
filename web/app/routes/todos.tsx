import { ListTodo } from "lucide-react";

import { DashboardPlaceholderPage } from "~/pages/dashboard-placeholder-page";
import { appInfo } from "~/lib/app-settings.shared";
import { requireAuthenticatedRoute } from "~/lib/server/route-guards.server";
import type { Route } from "./+types/todos";

export function meta() {
  return [{ title: `${appInfo.pageTitles.todos} | ${appInfo.name}` }];
}

export async function loader({ request }: Route.LoaderArgs) {
  return {
    user: await requireAuthenticatedRoute(request),
  };
}

export default function Todos({ loaderData }: Route.ComponentProps) {
  return (
    <DashboardPlaceholderPage
      user={loaderData.user}
      title={appInfo.pageTitles.todos}
      eyebrow="Apps"
      description="A placeholder for a future todos app module."
      icon={ListTodo}
    />
  );
}
