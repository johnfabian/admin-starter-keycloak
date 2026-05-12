import { UsersDashboardPage } from "~/components/pages/users-dashboard-page";
import { requireAuthenticatedRoute } from "~/lib/route-guards.server";
import type { Route } from "./+types/users-dashboard";

export function meta() {
  return [{ title: "User Dashboard | Admin Starter" }];
}

export async function loader({ request }: Route.LoaderArgs) {
  return {
    user: await requireAuthenticatedRoute(request),
  };
}

export default function UsersDashboard({ loaderData }: Route.ComponentProps) {
  return <UsersDashboardPage user={loaderData.user} />;
}
