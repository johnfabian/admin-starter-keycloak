import { useEffect, useState } from "react";

import { appUi } from "~/lib/app-settings.shared";

export function useIsMobile() {
  const [isMobile, setIsMobile] = useState<boolean | undefined>(undefined);

  useEffect(() => {
    const mediaQuery = window.matchMedia(`(max-width: ${appUi.mobileBreakpoint - 1}px)`);
    const update = () => setIsMobile(window.innerWidth < appUi.mobileBreakpoint);

    mediaQuery.addEventListener("change", update);
    update();

    return () => mediaQuery.removeEventListener("change", update);
  }, []);

  return isMobile;
}
