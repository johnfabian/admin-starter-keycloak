import { HomePage } from "~/components/pages/home-page";
import { appInfo } from "~/lib/app-settings";
import { getCurrentUser } from "~/lib/auth.server";
import type { Route } from "./+types/home";

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

export default function Home({ loaderData }: Route.ComponentProps) {
  return <HomePage user={loaderData.user} />;
}
