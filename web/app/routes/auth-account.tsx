import { redirectToAccountConsole } from "~/lib/server/auth.server";
import type { Route } from "./+types/auth-account";

export async function loader({ request }: Route.LoaderArgs) {
  return redirectToAccountConsole(request);
}
