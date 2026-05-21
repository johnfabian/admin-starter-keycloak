import { SplashPage } from "~/pages/splash-page";
import { appInfo } from "~/lib/app-settings.shared";
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
  return {
    user: await getCurrentUser(request),
  };
}

export default function Splash({ loaderData }: Route.ComponentProps) {
  return <SplashPage user={loaderData.user} />;
}
