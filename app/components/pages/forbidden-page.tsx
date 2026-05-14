import { Link } from "react-router";

import { Button } from "~/components/ui/button";
import { AppLayout } from "~/layouts/app-layout";
import { appRoutes } from "~/lib/app-settings";
import type { CurrentUser } from "~/models/current-user";

export function ForbiddenPage({ user }: { user: CurrentUser | null }) {
  return (
    <AppLayout user={user}>
      <main className="mx-auto flex min-h-[calc(100vh-4rem)] max-w-3xl items-center px-4 py-10 sm:px-6">
        <section className="rounded-2xl border border-zinc-200 bg-white p-8 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <p className="text-sm font-medium uppercase tracking-wider text-zinc-500">Forbidden</p>
          <h1 className="mt-3 text-4xl font-semibold tracking-tight">
            You do not have access to this area.
          </h1>
          <p className="mt-4 text-zinc-600 dark:text-zinc-300">
            This page requires one of the Keycloak client roles assigned for that app area.
          </p>
          <div className="mt-6">
            <Button asChild>
              <Link to={appRoutes.home}>Go home</Link>
            </Button>
          </div>
        </section>
      </main>
    </AppLayout>
  );
}
