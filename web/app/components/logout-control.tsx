import { LogOut } from "lucide-react";
import { Form, useSubmit } from "react-router";

import { Button } from "~/components/ui/button";
import { DropdownMenuItem } from "~/components/ui/dropdown-menu";
import { appRoutes } from "~/lib/app-settings.shared";

export function LogoutButton() {
  return (
    <Form method="post" action={appRoutes.authLogout}>
      <Button type="submit" variant="outline" size="sm">
        <LogOut className="h-4 w-4" aria-hidden="true" />
        Logout
      </Button>
    </Form>
  );
}

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
