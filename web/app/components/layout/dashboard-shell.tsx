import { useCallback, useMemo, useState, type ReactNode } from "react";
import { useLocation } from "react-router";

import { DashboardHeader } from "~/components/layout/dashboard-header";
import { Sidebar } from "~/components/layout/sidebar";
import { sidebarNavSections } from "~/components/layout/sidebar-nav-items";
import { Button } from "~/components/ui/button";
import { useIsMobile } from "~/hooks/use-mobile";
import { appRoles } from "~/lib/app-settings.shared";
import { hasRole } from "~/lib/auth-policy.shared";
import { getLocalStorageValue, setLocalStorageValue } from "~/lib/local-storage.shared";
import type { CurrentUser } from "~/models/current-user";

interface DashboardShellProps {
  children: ReactNode;
  title: string;
  user: CurrentUser;
}

const DASHBOARD_SHELL_CONFIG = {
  storageKeys: {
    sidebarState: "admin-starter-dashboard-sidebar-state",
  },
  sidebarStates: {
    collapsed: "collapsed",
    open: "open",
  },
} as const;

function getSavedSidebarOpen() {
  return (
    getLocalStorageValue(DASHBOARD_SHELL_CONFIG.storageKeys.sidebarState) !==
    DASHBOARD_SHELL_CONFIG.sidebarStates.collapsed
  );
}

function saveSidebarOpen(open: boolean) {
  setLocalStorageValue(
    DASHBOARD_SHELL_CONFIG.storageKeys.sidebarState,
    open
      ? DASHBOARD_SHELL_CONFIG.sidebarStates.open
      : DASHBOARD_SHELL_CONFIG.sidebarStates.collapsed
  );
}

export function DashboardShell({ children, title, user }: DashboardShellProps) {
  const location = useLocation();
  const isMobileViewport = useIsMobile();
  const isMobile = isMobileViewport === true;
  const [sidebarOpen, setSidebarOpen] = useState(getSavedSidebarOpen);
  const [mobileOpen, setMobileOpen] = useState(false);
  const visibleNavSections = useMemo(
    () =>
      sidebarNavSections.filter(
        (section) => !section.adminOnly || hasRole(user, appRoles.admins)
      ),
    [user]
  );
  const collapsed = !sidebarOpen && !isMobile;

  const toggleSidebar = useCallback(() => {
    if (isMobile) {
      setMobileOpen(true);
      return;
    }

    setSidebarOpen((open) => {
      const nextOpen = !open;
      saveSidebarOpen(nextOpen);
      return nextOpen;
    });
  }, [isMobile]);

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="flex min-h-screen">
        <Sidebar
          ariaLabel="Dashboard navigation"
          collapsed={collapsed}
          navSections={visibleNavSections}
          pathname={location.pathname}
          mobileOpen={mobileOpen}
          onCloseMobile={() => setMobileOpen(false)}
        />

        {mobileOpen ? (
          <Button
            type="button"
            variant="ghost"
            className="fixed inset-0 z-40 h-auto w-auto rounded-none bg-black/55 p-0 backdrop-blur-[1px] hover:bg-black/55 md:hidden"
            aria-label="Close navigation"
            onClick={() => setMobileOpen(false)}
          />
        ) : null}

        <div className="flex min-w-0 flex-1 flex-col">
          <DashboardHeader
            isMobile={isMobile}
            onToggleSidebar={toggleSidebar}
            sidebarOpen={sidebarOpen}
            title={title}
            user={user}
          />

          <main className="flex flex-1 flex-col gap-6 p-4 sm:p-6 lg:p-8">{children}</main>
        </div>
      </div>
    </div>
  );
}
