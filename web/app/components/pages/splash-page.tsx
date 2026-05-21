import { ArrowRight, CheckCircle2, Database, KeyRound, ShieldCheck, Users } from "lucide-react";
import { Link } from "react-router";

import { Button } from "~/components/ui/button";
import { AppLayout } from "~/layouts/app-layout";
import { appRoles, appRoutes } from "~/lib/app-settings";
import type { CurrentUser } from "~/models/current-user";

export function SplashPage({ user }: { user: CurrentUser | null }) {
  return (
    <AppLayout user={user} background="white">
      <main>
        <section className="relative overflow-hidden border-b border-zinc-200 dark:border-zinc-800">
          <div className="absolute inset-0 -z-10 bg-[linear-gradient(120deg,#f8fafc_0%,#eef2ff_38%,#ecfeff_68%,#f7fee7_100%)] dark:bg-[linear-gradient(120deg,#09090b_0%,#111827_42%,#042f2e_72%,#1c1917_100%)]" />
          <div className="mx-auto grid min-h-[calc(100vh-4rem)] max-w-7xl items-center gap-10 px-4 py-14 sm:px-6 lg:grid-cols-[1fr_0.95fr] lg:px-8">
            <div className="max-w-3xl">
              <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-zinc-200 bg-white/80 px-3 py-1 text-sm text-zinc-700 shadow-sm dark:border-zinc-800 dark:bg-zinc-950/70 dark:text-zinc-300">
                <ShieldCheck className="h-4 w-4 text-emerald-600" aria-hidden="true" />
                Keycloak-backed admin foundation
              </div>
              <h1 className="max-w-4xl text-5xl font-semibold tracking-tight text-zinc-950 sm:text-6xl lg:text-7xl dark:text-zinc-50">
                Manage users, groups, and apps from one clean starter.
              </h1>
              <p className="mt-6 max-w-2xl text-lg leading-8 text-zinc-700 dark:text-zinc-300">
                A dashboard-first React Router app wired for Keycloak roles, protected routes, user
                dashboards, and future admin tooling.
              </p>
              <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                <Button asChild size="default">
                  <a href={user ? appRoutes.usersDashboard : appRoutes.authLoginWithPrompt}>
                    {user ? "Open dashboard" : "Login with Keycloak"}
                    <ArrowRight className="h-4 w-4" aria-hidden="true" />
                  </a>
                </Button>
                <Button asChild variant="outline" size="default">
                  <Link to={appRoutes.adminsDashboard}>View admin route</Link>
                </Button>
              </div>
              <div className="mt-10 grid max-w-2xl gap-3 sm:grid-cols-3">
                {[
                  "Server session cookie",
                  `${appRoles.admins} and ${appRoles.users} roles`,
                  "Postgres-ready apps",
                ].map((item) => (
                  <div
                    key={item}
                    className="flex items-center gap-2 rounded-lg bg-white/70 px-3 py-2 text-sm text-zinc-700 shadow-sm ring-1 ring-zinc-200 dark:bg-zinc-950/60 dark:text-zinc-300 dark:ring-zinc-800"
                  >
                    <CheckCircle2 className="h-4 w-4 text-emerald-600" aria-hidden="true" />
                    {item}
                  </div>
                ))}
              </div>
            </div>

            <div className="relative mx-auto w-full max-w-xl">
              <div className="rounded-2xl border border-zinc-200 bg-white shadow-2xl shadow-zinc-900/10 dark:border-zinc-800 dark:bg-zinc-900 dark:shadow-black/30">
                <div className="flex items-center justify-between border-b border-zinc-200 px-5 py-4 dark:border-zinc-800">
                  <div>
                    <p className="text-sm font-medium text-zinc-500 dark:text-zinc-400">
                      Live workspace
                    </p>
                    <p className="text-lg font-semibold">Admin Console</p>
                  </div>
                  <div className="flex gap-1.5">
                    <span className="h-3 w-3 rounded-full bg-rose-400" />
                    <span className="h-3 w-3 rounded-full bg-amber-400" />
                    <span className="h-3 w-3 rounded-full bg-emerald-400" />
                  </div>
                </div>
                <div className="grid gap-4 p-5">
                  <div className="grid grid-cols-3 gap-3">
                    <PreviewStat icon={Users} label="Users" value="1,248" />
                    <PreviewStat icon={ShieldCheck} label="Roles" value="2" />
                    <PreviewStat icon={Database} label="Apps" value="6" />
                  </div>
                  <div className="rounded-xl border border-zinc-200 dark:border-zinc-800">
                    <div className="grid grid-cols-[1fr_auto] gap-3 border-b border-zinc-200 px-4 py-3 text-sm font-medium dark:border-zinc-800">
                      <span>Recent access</span>
                      <span className="text-zinc-500">Role</span>
                    </div>
                    {[
                      ["Maya Chen", appRoles.admins, "bg-emerald-500"],
                      ["Jon Bell", appRoles.users, "bg-sky-500"],
                      ["Priya Shah", appRoles.users, "bg-violet-500"],
                    ].map(([name, role, color]) => (
                      <div
                        key={name}
                        className="grid grid-cols-[1fr_auto] items-center gap-3 border-b border-zinc-100 px-4 py-3 last:border-0 dark:border-zinc-800"
                      >
                        <span className="flex items-center gap-3 text-sm">
                          <span className={`h-8 w-8 rounded-full ${color}`} />
                          {name}
                        </span>
                        <span className="rounded-full bg-zinc-100 px-2.5 py-1 text-xs text-zinc-700 dark:bg-zinc-800 dark:text-zinc-200">
                          {role}
                        </span>
                      </div>
                    ))}
                  </div>
                  <div className="rounded-xl bg-zinc-950 p-4 text-white dark:bg-zinc-50 dark:text-zinc-950">
                    <div className="flex items-center gap-3">
                      <KeyRound className="h-5 w-5" aria-hidden="true" />
                      <div>
                        <p className="font-medium">Protected by Keycloak</p>
                        <p className="text-sm text-zinc-300 dark:text-zinc-600">
                          Server-checked routes with app roles.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
    </AppLayout>
  );
}

function PreviewStat({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof Users;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-xl border border-zinc-200 p-4 dark:border-zinc-800">
      <Icon className="mb-3 h-5 w-5 text-zinc-500" aria-hidden="true" />
      <p className="text-2xl font-semibold">{value}</p>
      <p className="text-sm text-zinc-500">{label}</p>
    </div>
  );
}
