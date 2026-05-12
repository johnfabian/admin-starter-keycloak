import { logout } from "~/lib/auth.server";
import type { Route } from "./+types/auth-logout";

export async function loader({ request }: Route.LoaderArgs) {
  return logout(request);
}
