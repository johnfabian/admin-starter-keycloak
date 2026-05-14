import { AppLayout } from "~/layouts/app-layout";
import type { CurrentUser } from "~/models/current-user";

export function UsersDashboardPage({ user }: { user: CurrentUser }) {
  const displayName =
    [user.firstName, user.lastName].filter(Boolean).join(" ") || user.name || "User";

  return (
    <AppLayout user={user}>
      <main className="mx-auto flex max-w-7xl flex-col gap-8 px-4 py-10 sm:px-6 lg:px-8">
        <section className="rounded-2xl border border-zinc-200 bg-white p-8 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <p className="text-sm font-medium uppercase tracking-wider text-zinc-500">
            User dashboard
          </p>
          <h1 className="mt-3 text-4xl font-semibold tracking-tight">Welcome, {displayName}</h1>
          <p className="mt-4 max-w-2xl text-zinc-600 dark:text-zinc-300">
            This is your default authenticated landing page. Navigation and app modules will plug in
            here later.
          </p>
        </section>
      </main>
    </AppLayout>
  );
}
