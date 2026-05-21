import { ShieldCheck, UsersRound } from "lucide-react";

import { DashboardLayout } from "~/layouts/dashboard-layout";
import { appInfo, appRoles } from "~/lib/app-settings.shared";
import type { CurrentUser } from "~/models/current-user";

export function AdminsDashboardPage({ user }: { user: CurrentUser }) {
  return (
    <DashboardLayout user={user} title={appInfo.pageTitles.adminsDashboard}>
      <section className="rounded-xl border bg-card p-8 shadow-sm">
        <div className="flex size-12 items-center justify-center rounded-xl bg-primary text-primary-foreground">
          <ShieldCheck className="h-6 w-6" aria-hidden="true" />
        </div>
        <p className="mt-6 text-sm font-medium uppercase text-muted-foreground">
          Admin dashboard
        </p>
        <h1 className="mt-3 text-4xl font-semibold tracking-tight">Admin access verified</h1>
        <p className="mt-4 max-w-2xl text-muted-foreground">
          You are signed in as {user.name} with the `{appRoles.admins}` role. User, group, and
          permission management screens will be added here next.
        </p>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {["Manage users", "Manage groups", "Group permissions"].map((label) => (
          <div key={label} className="rounded-xl border bg-card p-5 shadow-sm">
            <UsersRound className="mb-4 h-5 w-5 text-muted-foreground" aria-hidden="true" />
            <h2 className="font-semibold">{label}</h2>
            <p className="mt-2 text-sm text-muted-foreground">
              Placeholder for the upcoming admin module.
            </p>
          </div>
        ))}
      </section>
    </DashboardLayout>
  );
}
