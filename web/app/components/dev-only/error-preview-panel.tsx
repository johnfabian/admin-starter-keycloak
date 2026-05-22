import { AlertTriangle } from "lucide-react";
import { Link } from "react-router";

import { Button } from "~/components/ui/button";
import { appRoutes } from "~/lib/app-settings.shared";
import { errorPreviewStatuses } from "~/lib/error-preview.shared";

export function ErrorPreviewPanel() {
  if (!import.meta.env.DEV) return null;

  return (
    <section className="rounded-xl border bg-card p-6 shadow-sm">
      <div className="flex flex-col gap-1">
        <p className="text-sm font-medium uppercase text-muted-foreground">Error previews</p>
        <h2 className="text-2xl font-semibold tracking-tight">Simulate route errors</h2>
        <p className="text-sm text-muted-foreground">
          Use these to preview the shared error page for common application failures.
        </p>
      </div>

      <div className="mt-6 flex flex-wrap gap-3">
        {errorPreviewStatuses.map((preview) => (
          <Button key={preview.status} asChild variant="outline" size="sm">
            <Link to={`${appRoutes.usersDashboardErrorPreview}/${preview.status}`}>
              <AlertTriangle className="size-4" aria-hidden="true" />
              {preview.label}
            </Link>
          </Button>
        ))}
      </div>
    </section>
  );
}
