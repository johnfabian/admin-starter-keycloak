import { Link, useLocation } from "react-router";
import {
  Blocks,
  Home,
  Menu,
  PanelLeftClose,
  PanelLeftOpen,
  Shield,
  User,
  X,
  type LucideIcon,
} from "lucide-react";
import { useMemo, useState } from "react";

import { LogoutMenuItem } from "~/components/logout-control";
import { ThemeToggle } from "~/components/theme-toggle/theme-toggle";
import { Avatar, AvatarFallback, AvatarImage } from "~/components/ui/avatar";
import { Button } from "~/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "~/components/ui/dropdown-menu";
import { useIsMobile } from "~/hooks/use-mobile";
import { appInfo, appRoles, appRoutes } from "~/lib/app-settings.shared";
import { getInitials, isPathActive } from "~/lib/string-helper.shared";
import { cn } from "~/lib/tw.shared";
import type { CurrentUser } from "~/models/current-user";

interface DashboardLayoutProps {
  user: CurrentUser;
  title?: string;
  children: React.ReactNode;
}

interface NavItem {
  label: string;
  to: string;
  icon: LucideIcon;
  exact?: boolean;
  adminOnly?: boolean;
}

const navItems: NavItem[] = [
  {
    label: appInfo.pageTitles.usersDashboard,
    to: appRoutes.usersDashboard,
    icon: Home,
    exact: true,
  },
  {
    label: appInfo.pageTitles.adminsDashboard,
    to: appRoutes.adminsDashboard,
    icon: Shield,
    exact: true,
    adminOnly: true,
  },
];

export function DashboardLayout({
  user,
  title = appInfo.pageTitles.usersDashboard,
  children,
}: DashboardLayoutProps) {
  const location = useLocation();
  const isMobile = useIsMobile();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mobileOpen, setMobileOpen] = useState(false);
  const isAdmin = user.roles.includes(appRoles.admins);

  const visibleNavItems = useMemo(
    () => navItems.filter((item) => !item.adminOnly || isAdmin),
    [isAdmin]
  );

  const collapsed = !sidebarOpen && !isMobile;

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="flex min-h-screen">
        <DashboardSidebar
          collapsed={collapsed}
          navItems={visibleNavItems}
          pathname={location.pathname}
          mobileOpen={mobileOpen}
          onCloseMobile={() => setMobileOpen(false)}
        />

        {mobileOpen ? (
          <Button
            type="button"
            variant="ghost"
            className="fixed inset-0 z-40 h-auto w-auto rounded-none bg-background/80 p-0 backdrop-blur-sm hover:bg-background/80 md:hidden"
            aria-label="Close navigation"
            onClick={() => setMobileOpen(false)}
          />
        ) : null}

        <div className="flex min-w-0 flex-1 flex-col">
          <header className="sticky top-0 z-30 flex h-header shrink-0 items-center justify-between gap-3 border-b bg-background/90 px-4 backdrop-blur">
            <div className="flex min-w-0 items-center gap-2">
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="h-8 w-8"
                aria-label={isMobile ? "Open navigation" : "Toggle navigation"}
                onClick={() => {
                  if (isMobile) {
                    setMobileOpen(true);
                  } else {
                    setSidebarOpen((open) => !open);
                  }
                }}
              >
                {isMobile ? (
                  <Menu className="size-4" aria-hidden="true" />
                ) : sidebarOpen ? (
                  <PanelLeftClose className="size-4" aria-hidden="true" />
                ) : (
                  <PanelLeftOpen className="size-4" aria-hidden="true" />
                )}
              </Button>
              <div className="h-5 w-px bg-border" aria-hidden="true" />
              <span className="truncate text-sm font-medium">{title}</span>
            </div>

            <div className="flex items-center gap-2">
              <ThemeToggle />
              <DashboardUserMenu user={user} />
            </div>
          </header>

          <main className="flex flex-1 flex-col gap-6 p-4 sm:p-6 lg:p-8">{children}</main>
        </div>
      </div>
    </div>
  );
}

function DashboardSidebar({
  collapsed,
  navItems,
  pathname,
  mobileOpen,
  onCloseMobile,
}: {
  collapsed: boolean;
  navItems: NavItem[];
  pathname: string;
  mobileOpen: boolean;
  onCloseMobile: () => void;
}) {
  return (
    <aside
      className={cn(
        "fixed inset-y-0 left-0 z-50 flex w-72 -translate-x-full flex-col overflow-hidden border-r bg-sidebar text-sidebar-foreground shadow-xl transition-[transform,width] duration-200 ease-linear will-change-[transform,width] md:sticky md:top-0 md:z-20 md:h-screen md:translate-x-0 md:shadow-none",
        mobileOpen && "translate-x-0",
        collapsed && "md:w-16"
      )}
      aria-label="Dashboard navigation"
    >
      <div className="flex h-header items-center justify-between gap-2 border-b border-sidebar-border px-3">
        <Link
          to={appRoutes.home}
          className={cn(
            "flex min-w-0 items-center gap-2 rounded-md text-sm font-semibold outline-none transition-[gap] duration-200 ease-linear focus-visible:ring-2 focus-visible:ring-sidebar-ring",
            collapsed && "md:gap-0"
          )}
          aria-label={`${appInfo.name} home`}
        >
          <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
            <Blocks className="size-5" aria-hidden="true" />
          </span>
          <span
            aria-hidden={collapsed}
            className={cn(
              "max-w-40 truncate opacity-100 transition-[max-width,opacity] duration-200 ease-linear",
              collapsed && "md:max-w-0 md:opacity-0"
            )}
          >
            {appInfo.name}
          </span>
        </Link>
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="h-8 w-8 md:hidden"
          aria-label="Close navigation"
          onClick={onCloseMobile}
        >
          <X className="size-4" aria-hidden="true" />
        </Button>
      </div>

      <nav className="flex-1 space-y-6 overflow-y-auto px-3 py-4" aria-label="Main navigation">
        <div>
          <p
            className={cn(
              "h-6 overflow-hidden px-2 pb-2 text-xs font-medium uppercase text-sidebar-foreground/60 opacity-100 transition-[height,padding,opacity] duration-200 ease-linear",
              collapsed && "md:h-0 md:pb-0 md:opacity-0"
            )}
          >
            Workspace
          </p>
          <ul className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = isPathActive(pathname, item.to, item.exact);

              return (
                <li key={item.to}>
                  <Link
                    to={item.to}
                    onClick={onCloseMobile}
                    aria-current={active ? "page" : undefined}
                    title={collapsed ? item.label : undefined}
                    className={cn(
                      "flex h-9 items-center gap-2 rounded-md px-2 text-sm outline-none transition-[background-color,color,padding] duration-200 ease-linear hover:bg-sidebar-accent hover:text-sidebar-accent-foreground focus-visible:ring-2 focus-visible:ring-sidebar-ring",
                      active && "bg-sidebar-accent font-medium text-sidebar-accent-foreground",
                      collapsed && "md:justify-center md:gap-0"
                    )}
                  >
                    <Icon className="size-4 shrink-0" aria-hidden="true" />
                    <span
                      aria-hidden={collapsed}
                      className={cn(
                        "max-w-44 truncate opacity-100 transition-[max-width,opacity] duration-200 ease-linear",
                        collapsed && "md:max-w-0 md:opacity-0"
                      )}
                    >
                      {item.label}
                    </span>
                  </Link>
                </li>
              );
            })}
          </ul>
        </div>
      </nav>
    </aside>
  );
}

function DashboardUserMenu({ user }: { user: CurrentUser }) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="rounded-full"
          aria-label="Open account menu"
        >
          <Avatar>
            {user.image ? <AvatarImage src={user.image} alt={user.name} /> : null}
            <AvatarFallback>{getInitials([user.firstName, user.lastName], user.name)}</AvatarFallback>
          </Avatar>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        <DropdownMenuLabel className="font-normal">
          <span className="block truncate text-sm font-medium">{user.name}</span>
          <span className="block truncate text-xs text-muted-foreground">
            {user.email || "Signed in"}
          </span>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem asChild>
          <a href={appRoutes.authAccount} target="_blank" rel="noreferrer">
            <User className="size-4" aria-hidden="true" />
            Account
          </a>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <LogoutMenuItem />
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
