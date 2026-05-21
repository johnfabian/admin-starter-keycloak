import { Link } from "react-router";
import { Blocks, ExternalLink, Shield, UserRound } from "lucide-react";

import { LogoutButton, LogoutMenuItem } from "~/components/logout-control";
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
import { appInfo, appRoles, appRoutes } from "~/lib/app-settings.shared";
import { getInitials } from "~/lib/string-helper.shared";
import type { CurrentUser } from "~/models/current-user";

export function AppHeader({ user }: { user: CurrentUser | null }) {
  return (
    <header className="sticky top-0 z-40 border-b bg-background/90 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link
          to={appRoutes.home}
          className="flex items-center gap-3"
          aria-label={`${appInfo.name} home`}
        >
          <span className="flex size-9 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <Blocks className="h-5 w-5" aria-hidden="true" />
          </span>
          <span className="font-semibold tracking-tight text-foreground">{appInfo.name}</span>
        </Link>

        <div className="flex items-center gap-2">
          {user ? (
            <>
              {user.roles.includes(appRoles.admins) ? (
                <Button asChild variant="ghost" size="sm">
                  <Link to={appRoutes.adminsDashboard}>
                    <Shield className="h-4 w-4" aria-hidden="true" />
                    {appRoles.admins}
                  </Link>
                </Button>
              ) : null}
              <Button asChild variant="ghost" size="sm">
                <Link to={appRoutes.usersDashboard}>
                  <UserRound className="h-4 w-4" aria-hidden="true" />
                  Dashboard
                </Link>
              </Button>
              <LogoutButton />
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
                      <AvatarFallback>
                        {getInitials([user.firstName, user.lastName], user.name)}
                      </AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuLabel>
                    <span className="block truncate">{user.name}</span>
                    <span className="block truncate text-xs font-normal text-muted-foreground">
                      {user.email || "Signed in"}
                    </span>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem asChild>
                    <a href={appRoutes.authAccount} target="_blank" rel="noreferrer">
                      <ExternalLink className="mr-2 h-4 w-4" aria-hidden="true" />
                      My Profile
                    </a>
                  </DropdownMenuItem>
                  <LogoutMenuItem />
                </DropdownMenuContent>
              </DropdownMenu>
            </>
          ) : (
            <>
              <ThemeToggle />
              <Button asChild variant="ghost" size="sm">
                <a href={appRoutes.authLoginWithPrompt}>Login</a>
              </Button>
              <Button asChild size="sm">
                <a href={appRoutes.authRegister}>Register</a>
              </Button>
            </>
          )}
          {user ? <ThemeToggle /> : null}
        </div>
      </div>
    </header>
  );
}
