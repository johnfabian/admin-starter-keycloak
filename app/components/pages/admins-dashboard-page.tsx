import { ShieldCheck, UsersRound } from "lucide-react";

import { AppLayout } from "~/layouts/app-layout";
import type { CurrentUser } from "~/models/current-user";

export function AdminsDashboardPage({ user }: { user: CurrentUser }) {
  return (
    <AppLayout user={user}>
      <main className="mx-auto flex max-w-7xl flex-col gap-8 px-4 py-10 sm:px-6 lg:px-8">
        <section className="rounded-2xl border border-zinc-200 bg-white p-8 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-zinc-950 text-white dark:bg-zinc-50 dark:text-zinc-950">
            <ShieldCheck className="h-6 w-6" aria-hidden="true" />
          </div>
          <p className="mt-6 text-sm font-medium uppercase tracking-wider text-zinc-500">
            Admin dashboard
          </p>
          <h1 className="mt-3 text-4xl font-semibold tracking-tight">Admin access verified</h1>
          <p className="mt-4 max-w-2xl text-zinc-600 dark:text-zinc-300">
            You are signed in as {user.name} with the `Admins` role. User, group, and permission
            management screens will be added here next.
          </p>
        </section>

        <section className="grid gap-4 md:grid-cols-3">
          {["Manage users", "Manage groups", "Group permissions"].map((label) => (
            <div
              key={label}
              className="rounded-xl border border-zinc-200 bg-white p-5 shadow-sm dark:border-zinc-800 dark:bg-zinc-900"
            >
              <UsersRound className="mb-4 h-5 w-5 text-zinc-500" aria-hidden="true" />
              <h2 className="font-semibold">{label}</h2>
              <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
                Placeholder for the upcoming admin module.
              </p>
            </div>
          ))}
        </section>
      </main>
    </AppLayout>
  );
}
