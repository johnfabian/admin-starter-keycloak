import type { LucideIcon } from "lucide-react";

import { DashboardLayout } from "~/layouts/dashboard-layout";
import type { CurrentUser } from "~/models/current-user";

interface DashboardPlaceholderPageProps {
  description: string;
  eyebrow: string;
  icon: LucideIcon;
  title: string;
  user: CurrentUser;
}

export function DashboardPlaceholderPage({
  description,
  eyebrow,
  icon: Icon,
  title,
  user,
}: DashboardPlaceholderPageProps) {
  return (
    <DashboardLayout user={user} title={title}>
      <section className="rounded-xl border bg-card p-8 shadow-sm">
        <div className="flex size-12 items-center justify-center rounded-xl bg-primary text-primary-foreground">
          <Icon className="size-6" aria-hidden="true" />
        </div>
        <p className="mt-6 text-sm font-medium uppercase text-muted-foreground">{eyebrow}</p>
        <h1 className="mt-3 text-4xl font-semibold tracking-tight">{title}</h1>
        <p className="mt-4 max-w-2xl text-muted-foreground">{description}</p>
      </section>
    </DashboardLayout>
  );
}

