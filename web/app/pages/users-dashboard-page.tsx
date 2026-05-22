import { ErrorPreviewPanel } from "~/components/dev-only/error-preview-panel";
import { DashboardLayout } from "~/layouts/dashboard-layout";
import { appInfo } from "~/lib/app-settings.shared";
import { joinNonEmpty } from "~/lib/string-helper.shared";
import type { CurrentUser } from "~/models/current-user";

export function UsersDashboardPage({ user }: { user: CurrentUser }) {
  const displayName = joinNonEmpty([user.firstName, user.lastName]) || user.name || "User";

  return (
    <DashboardLayout user={user} title={appInfo.pageTitles.usersDashboard}>
      <section className="rounded-xl border bg-card p-8 shadow-sm">
        <p className="text-sm font-medium uppercase text-muted-foreground">Dashboard</p>
        <h1 className="mt-3 text-4xl font-semibold tracking-tight">Welcome, {displayName}</h1>
        <p className="mt-4 max-w-2xl text-muted-foreground">
          This is your default authenticated landing page. The placeholder navigation is ready for
          profile, settings, and app modules.
        </p>
      </section>

      <section className="rounded-xl border bg-card p-6 shadow-sm">
        <div className="flex flex-col gap-1">
          <p className="text-sm font-medium uppercase text-muted-foreground">Current user</p>
          <h2 className="text-2xl font-semibold tracking-tight">Keycloak profile</h2>
          <p className="text-sm text-muted-foreground">
            These values come from the validated Keycloak token claims stored in the BFF session.
          </p>
        </div>

        <dl className="mt-6 grid gap-4 md:grid-cols-3">
          <div className="rounded-lg border bg-background p-4">
            <dt className="text-xs font-medium uppercase text-muted-foreground">Name</dt>
            <dd className="mt-2 truncate text-sm font-medium">{user.name || displayName}</dd>
          </div>
          <div className="rounded-lg border bg-background p-4">
            <dt className="text-xs font-medium uppercase text-muted-foreground">Email</dt>
            <dd className="mt-2 truncate text-sm font-medium">{user.email || "Not provided"}</dd>
          </div>
          <div className="rounded-lg border bg-background p-4">
            <dt className="text-xs font-medium uppercase text-muted-foreground">Subject</dt>
            <dd className="mt-2 truncate text-sm font-medium">{user.id}</dd>
          </div>
        </dl>

        <div className="mt-6">
          <TokenClaimList
            title="Roles"
            values={user.roles}
            emptyMessage="No realm or client roles were found on this user's access token."
          />
        </div>
      </section>

      <ErrorPreviewPanel />
    </DashboardLayout>
  );
}

function TokenClaimList({
  title,
  values,
  emptyMessage,
}: {
  title: string;
  values: string[];
  emptyMessage: string;
}) {
  return (
    <>
      <h3 className="text-sm font-medium">{title}</h3>
      {values.length > 0 ? (
        <ul className="mt-3 flex flex-wrap gap-2">
          {values.map((value) => (
            <li
              key={value}
              className="rounded-md border bg-muted px-2.5 py-1 text-xs font-medium text-muted-foreground"
            >
              {value}
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-3 text-sm text-muted-foreground">{emptyMessage}</p>
      )}
    </>
  );
}
