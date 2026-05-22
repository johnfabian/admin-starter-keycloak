import { LogOut } from "lucide-react";
import { useSubmit } from "react-router";

import { DropdownMenuItem } from "~/components/ui/dropdown-menu";
import { appRoutes } from "~/lib/app-settings.shared";

export function LogoutMenuItem() {
  const submit = useSubmit();

  return (
    <DropdownMenuItem
      className="text-red-600 focus:text-red-700 dark:text-red-400"
      onSelect={(event) => {
        event.preventDefault();
        submit(null, { action: appRoutes.authLogout, method: "post" });
      }}
    >
      <LogOut className="size-4" aria-hidden="true" />
      Logout
    </DropdownMenuItem>
  );
}
