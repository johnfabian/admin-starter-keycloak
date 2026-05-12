import { AdminsDashboardPage } from "~/components/pages/admins-dashboard-page";
import { requireAdminRoute } from "~/lib/route-guards.server";
import type { Route } from "./+types/admins-dashboard";

export function meta() {
  return [{ title: "Admins | Admin Starter" }];
}

export async function loader({ request }: Route.LoaderArgs) {
  return {
    user: await requireAdminRoute(request),
  };
}

export default function AdminsDashboard({ loaderData }: Route.ComponentProps) {
  return <AdminsDashboardPage user={loaderData.user} />;
}
