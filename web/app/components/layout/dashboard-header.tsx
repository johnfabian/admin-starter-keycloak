import { Menu, PanelLeftClose, PanelLeftOpen } from "lucide-react";

import { ThemeToggle } from "~/components/layout/theme-toggle";
import { Button } from "~/components/ui/button";
import { UserMenu } from "~/components/layout/user-menu";
import type { CurrentUser } from "~/models/current-user";

interface DashboardHeaderProps {
  isMobile: boolean;
  onToggleSidebar: () => void;
  sidebarOpen: boolean;
  title: string;
  user: CurrentUser;
}

export function DashboardHeader({
  isMobile,
  onToggleSidebar,
  sidebarOpen,
  title,
  user,
}: DashboardHeaderProps) {
  return (
    <header className="sticky top-0 z-30 flex h-header shrink-0 items-center justify-between gap-3 border-b bg-background/90 px-4 backdrop-blur">
      <div className="flex min-w-0 items-center gap-2">
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="h-8 w-8"
          aria-label={isMobile ? "Open navigation" : "Toggle navigation"}
          onClick={onToggleSidebar}
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
        <UserMenu user={user} />
      </div>
    </header>
  );
}
