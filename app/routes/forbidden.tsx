import { ForbiddenPage } from "~/components/pages/forbidden-page";
import { appInfo } from "~/lib/app-settings";
import { getCurrentUser } from "~/lib/auth.server";
import type { Route } from "./+types/forbidden";

export function meta() {
  return [{ title: `${appInfo.pageTitles.forbidden} | ${appInfo.name}` }];
}

export async function loader({ request }: Route.LoaderArgs) {
  return {
    user: await getCurrentUser(request),
  };
}

export default function Forbidden({ loaderData }: Route.ComponentProps) {
  return <ForbiddenPage user={loaderData.user} />;
}
