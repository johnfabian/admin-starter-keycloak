import type { ReactNode } from "react";

import { DashboardShell } from "~/components/layout/dashboard-shell";
import { appInfo } from "~/lib/app-settings.shared";
import type { CurrentUser } from "~/models/current-user";

interface DashboardLayoutProps {
  children: ReactNode;
  title?: string;
  user: CurrentUser;
}

export function DashboardLayout({
  children,
  title = appInfo.pageTitles.usersDashboard,
  user,
}: DashboardLayoutProps) {
  return (
    <DashboardShell user={user} title={title}>
      {children}
    </DashboardShell>
  );
}
