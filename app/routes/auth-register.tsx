import { redirectToLogin } from "~/lib/auth.server";
import type { Route } from "./+types/auth-register";

export async function loader({ request }: Route.LoaderArgs) {
  return redirectToLogin(request, "register");
}
