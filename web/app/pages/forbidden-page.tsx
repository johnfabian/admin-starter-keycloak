import { Link } from "react-router";

import { Button } from "~/components/ui/button";
import { PublicLayout } from "~/layouts/public-layout";
import { appRoutes } from "~/lib/app-settings.shared";
import type { CurrentUser } from "~/models/current-user";

export function ForbiddenPage({ user }: { user: CurrentUser | null }) {
  return (
    <PublicLayout user={user}>
      <main className="mx-auto flex min-h-[calc(100vh-4rem)] max-w-3xl items-center px-4 py-10 sm:px-6">
        <section className="rounded-xl border bg-card p-8 shadow-sm">
          <p className="text-sm font-medium uppercase text-muted-foreground">Forbidden</p>
          <h1 className="mt-3 text-4xl font-semibold tracking-tight">
            You do not have access to this area.
          </h1>
          <p className="mt-4 text-muted-foreground">
            This page requires one of the Keycloak client roles assigned for that app area.
          </p>
          <div className="mt-6">
            <Button asChild>
              <Link to={appRoutes.home}>Go home</Link>
            </Button>
          </div>
        </section>
      </main>
    </PublicLayout>
  );
}
