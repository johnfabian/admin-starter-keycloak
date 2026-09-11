import type { ReactNode } from "react";

import { AppHeader } from "~/components/layout/app-header";
import type { CurrentUser } from "~/models/current-user";

interface PublicLayoutProps {
  background?: "white" | "muted";
  children: ReactNode;
  showHeader?: boolean;
  user: CurrentUser | null;
}

export function PublicLayout({
  background = "muted",
  children,
  showHeader = true,
  user,
}: PublicLayoutProps) {
  const backgroundClass =
    background === "white" ? "bg-background text-foreground" : "bg-muted/30 text-foreground";

  return (
    <div className={`min-h-screen ${backgroundClass}`}>
      {showHeader ? <AppHeader user={user} /> : null}
      {children}
    </div>
  );
}
