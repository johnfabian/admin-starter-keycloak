import { logout } from "~/lib/server/auth.server";
import type { Route } from "./+types/auth-logout";

export async function loader({ request }: Route.LoaderArgs) {
  if (request.method !== "GET") {
    throw new Response("Method not allowed.", { status: 405 });
  }

  throw new Response("Logout requires POST.", { status: 405 });
}

export async function action({ request }: Route.ActionArgs) {
  return logout(request);
}
