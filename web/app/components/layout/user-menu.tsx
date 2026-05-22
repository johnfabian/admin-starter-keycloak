import { User } from "lucide-react";

import { LogoutMenuItem } from "~/components/layout/logout-menu-item";
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
import { appRoutes } from "~/lib/app-settings.shared";
import { getInitials } from "~/lib/string-helper.shared";
import type { CurrentUser } from "~/models/current-user";

export function UserMenu({ user }: { user: CurrentUser }) {
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
