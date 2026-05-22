import { RouteErrorBoundary } from "~/components/error-page";
import { completeLogin } from "~/lib/server/auth.server";
import type { Route } from "./+types/auth-callback";

export async function loader({ request }: Route.LoaderArgs) {
  return completeLogin(request);
}

export function ErrorBoundary({ error }: Route.ErrorBoundaryProps) {
  return <RouteErrorBoundary error={error} />;
}
