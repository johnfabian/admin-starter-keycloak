import { LogOut } from "lucide-react";
import { Form } from "react-router";

import { Button } from "~/components/ui/button";
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
