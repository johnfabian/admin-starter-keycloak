import { AppHeader } from "~/components/app-header";
import type { CurrentUser } from "~/models/current-user";

interface PublicLayoutProps {
  user: CurrentUser | null;
  children: React.ReactNode;
  background?: "white" | "muted";
  showHeader?: boolean;
}

export function PublicLayout({
  user,
  children,
  background = "muted",
  showHeader = true,
}: PublicLayoutProps) {
  const backgroundClass =
    background === "white"
      ? "bg-background text-foreground"
      : "bg-muted/30 text-foreground";

  return (
    <div className={`min-h-screen ${backgroundClass}`}>
      {showHeader ? <AppHeader user={user} /> : null}
      {children}
    </div>
  );
}
