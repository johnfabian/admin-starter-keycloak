import { HomePage } from "~/components/pages/home-page";
import { getCurrentUser } from "~/lib/auth.server";
import type { Route } from "./+types/home";

export function meta() {
  return [
    { title: "Admin Starter Keycloak" },
    {
      name: "description",
      content: "A Keycloak-powered admin starter for users, groups, permissions, and apps.",
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
