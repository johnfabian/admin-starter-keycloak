import { Link } from "react-router";
import { Blocks, X } from "lucide-react";

import { SidebarNav } from "~/components/layout/sidebar-nav";
import type { SidebarNavSection } from "~/components/layout/sidebar-nav-items";
import { Button } from "~/components/ui/button";
import { appInfo, appRoutes } from "~/lib/app-settings.shared";
import { cn } from "~/lib/tw.shared";

interface SidebarProps {
  ariaLabel?: string;
  collapsed: boolean;
  mobileOpen: boolean;
  navSections: SidebarNavSection[];
  onCloseMobile: () => void;
  pathname: string;
  side?: "left" | "right";
}

export function Sidebar({
  ariaLabel = "Application navigation",
  collapsed,
  mobileOpen,
  navSections,
  onCloseMobile,
  pathname,
  side = "left",
}: SidebarProps) {
  const isRight = side === "right";

  return (
    <aside
      className={cn(
        "fixed inset-y-0 z-50 flex w-72 flex-col overflow-hidden border-r bg-sidebar text-sidebar-foreground shadow-xl transition-[transform,width] duration-200 ease-linear will-change-[transform,width] md:sticky md:top-0 md:z-20 md:h-screen md:translate-x-0 md:shadow-none",
        isRight ? "right-0 translate-x-full md:border-l md:border-r-0" : "left-0 -translate-x-full",
        mobileOpen && "translate-x-0",
        collapsed && "md:w-16"
      )}
      aria-label={ariaLabel}
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

      <SidebarNav
        collapsed={collapsed}
        onNavigate={onCloseMobile}
        pathname={pathname}
        sections={navSections}
      />
    </aside>
  );
}
