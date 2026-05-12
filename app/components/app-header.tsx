import { Link } from "react-router";
import { Blocks, LogOut, Shield, UserRound } from "lucide-react";

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
import type { CurrentUser } from "~/models/current-user";

function getInitials(user: CurrentUser) {
  const initials = [user.firstName, user.lastName]
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase())
    .join("");

  return initials || user.name.charAt(0).toUpperCase() || "U";
}

export function AppHeader({ user }: { user: CurrentUser | null }) {
  return (
    <header className="sticky top-0 z-40 border-b border-zinc-200/80 bg-white/90 backdrop-blur dark:border-zinc-800 dark:bg-zinc-950/90">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link to="/" className="flex items-center gap-3" aria-label="Admin Starter home">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-zinc-950 text-white dark:bg-zinc-50 dark:text-zinc-950">
            <Blocks className="h-5 w-5" aria-hidden="true" />
          </span>
          <span className="font-semibold tracking-tight text-zinc-950 dark:text-zinc-50">
            Admin Starter
          </span>
        </Link>

        <div className="flex items-center gap-2">
          {user ? (
            <>
              {user.roles.includes("Admins") ? (
                <Button asChild variant="ghost" size="sm">
                  <Link to="/admins/dashboard">
                    <Shield className="h-4 w-4" aria-hidden="true" />
                    Admins
                  </Link>
                </Button>
              ) : null}
              <Button asChild variant="ghost" size="sm">
                <Link to="/users/dashboard">
                  <UserRound className="h-4 w-4" aria-hidden="true" />
                  Dashboard
                </Link>
              </Button>
              <Button asChild variant="outline" size="sm">
                <a href="/auth/logout">
                  <LogOut className="h-4 w-4" aria-hidden="true" />
                  Logout
                </a>
              </Button>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button
                    className="rounded-full outline-none ring-offset-2 transition focus-visible:ring-2 focus-visible:ring-zinc-950 dark:focus-visible:ring-zinc-300"
                    aria-label="Open account menu"
                  >
                    <Avatar>
                      {user.image ? <AvatarImage src={user.image} alt={user.name} /> : null}
                      <AvatarFallback>{getInitials(user)}</AvatarFallback>
                    </Avatar>
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuLabel>
                    <span className="block truncate">{user.name}</span>
                    <span className="block truncate text-xs font-normal text-zinc-500">
                      {user.email || "Signed in"}
                    </span>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem asChild>
                    <a href="/auth/logout">
                      <LogOut className="mr-2 h-4 w-4" aria-hidden="true" />
                      Logout
                    </a>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </>
          ) : (
            <>
              <Button asChild variant="ghost" size="sm">
                <a href="/auth/login?prompt=login">Login</a>
              </Button>
              <Button asChild size="sm">
                <a href="/auth/register">Register</a>
              </Button>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
