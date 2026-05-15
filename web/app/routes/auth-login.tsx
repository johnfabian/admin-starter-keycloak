import { redirectToLogin } from "~/lib/auth.server";
import type { Route } from "./+types/auth-login";

export async function loader({ request }: Route.LoaderArgs) {
  return redirectToLogin(request);
}
