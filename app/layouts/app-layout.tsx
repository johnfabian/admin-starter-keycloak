import { AppHeader } from "~/components/app-header";
import type { CurrentUser } from "~/models/current-user";

interface AppLayoutProps {
  user: CurrentUser | null;
  children: React.ReactNode;
  background?: "white" | "muted";
}

export function AppLayout({ user, children, background = "muted" }: AppLayoutProps) {
  const backgroundClass =
    background === "white"
      ? "bg-white text-zinc-950 dark:bg-zinc-950 dark:text-zinc-50"
      : "bg-zinc-50 text-zinc-950 dark:bg-zinc-950 dark:text-zinc-50";

  return (
    <div className={`min-h-screen ${backgroundClass}`}>
      <AppHeader user={user} />
      {children}
    </div>
  );
}
