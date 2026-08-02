import { ListTodo } from "lucide-react";

import { RouteErrorBoundary } from "~/components/error-page";
import { DashboardPlaceholderPage } from "~/pages/dashboard-placeholder-page";
import { appInfo } from "~/lib/app-settings.shared";
import { requireUserRoute } from "~/lib/server/route-guards.server";
import type { Route } from "./+types/todos";

export function meta() {
  return [{ title: `${appInfo.pageTitles.todos} | ${appInfo.name}` }];
}

export async function loader({ request }: Route.LoaderArgs) {
  return {
    user: await requireUserRoute(request),
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

export function ErrorBoundary({ error }: Route.ErrorBoundaryProps) {
  return <RouteErrorBoundary error={error} />;
}
