import { redirect } from "react-router";

import { SplashPage } from "~/pages/splash-page";
import { appInfo, appRoutes } from "~/lib/app-settings.shared";
import { getCurrentUser } from "~/lib/server/auth.server";
import type { Route } from "./+types/splash";

export function meta() {
  return [
    { title: appInfo.title },
    {
      name: "description",
      content: appInfo.description,
    },
  ];
}

export async function loader({ request }: Route.LoaderArgs) {
  const user = await getCurrentUser(request);
  if (user) {
    throw redirect(appRoutes.usersDashboard);
  }

  return {
    user,
  };
}

export default function Splash({ loaderData }: Route.ComponentProps) {
  return <SplashPage user={loaderData.user} />;
}
