import { RouteErrorBoundary } from "~/components/error-page";
import { isErrorPreviewStatus } from "~/lib/error-preview.shared";
import { requireAuthenticatedRoute } from "~/lib/server/route-guards.server";
import type { Route } from "./+types/users-dashboard-error-preview";

const ERROR_PREVIEW_CONFIG = {
  defaultStatus: 500,
  disabledStatus: 404,
  invalidStatusMessage: "Invalid error preview status.",
} as const;

export async function loader({ params, request }: Route.LoaderArgs) {
  if (!import.meta.env.DEV) {
    throw new Response(null, { status: ERROR_PREVIEW_CONFIG.disabledStatus });
  }

  await requireAuthenticatedRoute(request);

  const status = Number(params.status);
  if (!isErrorPreviewStatus(status)) {
    throw new Response(ERROR_PREVIEW_CONFIG.invalidStatusMessage, {
      status: ERROR_PREVIEW_CONFIG.defaultStatus,
    });
  }

  throw new Response(null, { status });
}

export function ErrorBoundary({ error }: Route.ErrorBoundaryProps) {
  return <RouteErrorBoundary error={error} />;
}
