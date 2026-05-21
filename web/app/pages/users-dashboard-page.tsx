import { DashboardLayout } from "~/layouts/dashboard-layout";
import { appInfo } from "~/lib/app-settings.shared";
import { joinNonEmpty } from "~/lib/string-helper.shared";
import type { CurrentUser } from "~/models/current-user";

export function UsersDashboardPage({ user }: { user: CurrentUser }) {
  const displayName = joinNonEmpty([user.firstName, user.lastName]) || user.name || "User";

  return (
    <DashboardLayout user={user} title={appInfo.pageTitles.usersDashboard}>
      <section className="rounded-xl border bg-card p-8 shadow-sm">
        <p className="text-sm font-medium uppercase text-muted-foreground">User dashboard</p>
        <h1 className="mt-3 text-4xl font-semibold tracking-tight">Welcome, {displayName}</h1>
        <p className="mt-4 max-w-2xl text-muted-foreground">
          This is your default authenticated landing page. Navigation and app modules will plug in
          here later.
        </p>
      </section>
    </DashboardLayout>
  );
}
