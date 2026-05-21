import { redirect } from "react-router";

import { appRoutes } from "~/lib/app-settings.shared";

export async function loader() {
  return redirect(appRoutes.usersDashboard);
}
