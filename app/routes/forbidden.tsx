import { ForbiddenPage } from "~/components/pages/forbidden-page";
import { getCurrentUser } from "~/lib/auth.server";
import type { Route } from "./+types/forbidden";

export function meta() {
  return [{ title: "Forbidden | Admin Starter" }];
}

export async function loader({ request }: Route.LoaderArgs) {
  return {
    user: await getCurrentUser(request),
  };
}

export default function Forbidden({ loaderData }: Route.ComponentProps) {
  return <ForbiddenPage user={loaderData.user} />;
}
