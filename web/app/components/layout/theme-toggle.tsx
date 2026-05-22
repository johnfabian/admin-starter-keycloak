import { useCallback, useEffect, useRef, useState } from "react";
import { Moon, Palette, Sun } from "lucide-react";

import { Button } from "~/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuTrigger,
} from "~/components/ui/dropdown-menu";
import { useTheme } from "~/hooks/use-theme";
import { appTheme, type ColorMode, type ColorTheme } from "~/lib/app-settings.shared";

export function ThemeToggle() {
  const { colorMode, colorTheme, setColorMode, setColorTheme } = useTheme();
  // Announces theme changes to screen readers through the hidden status region below.
  const [srAnnouncement, setSrAnnouncement] = useState("");
  const [systemDark, setSystemDark] = useState(() =>
    typeof window === "undefined" ? false : window.matchMedia(appTheme.systemDarkModeQuery).matches
  );
  const srAnnouncementTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    return () => {
      if (srAnnouncementTimerRef.current) clearTimeout(srAnnouncementTimerRef.current);
    };
  }, []);

  useEffect(() => {
    const mediaQuery = window.matchMedia(appTheme.systemDarkModeQuery);
    const handleChange = (event: MediaQueryListEvent) => setSystemDark(event.matches);

    mediaQuery.addEventListener("change", handleChange);
    return () => mediaQuery.removeEventListener("change", handleChange);
  }, []);

  const isDark = colorMode === "dark" || (colorMode === "system" && systemDark);
  const currentThemeLabel =
    appTheme.themes.find((theme) => theme.value === colorTheme)?.label ?? colorTheme;

  const srAnnounce = useCallback((message: string) => {
    setSrAnnouncement(message);
    if (srAnnouncementTimerRef.current) clearTimeout(srAnnouncementTimerRef.current);
    srAnnouncementTimerRef.current = setTimeout(() => setSrAnnouncement(""), 1000);
  }, []);

  const handleColorThemeChange = useCallback(
    (theme: string) => {
      const nextTheme = theme as ColorTheme;
      if (!appTheme.themes.some((item) => item.value === nextTheme)) return;
      setColorTheme(nextTheme);
      srAnnounce(
        `Color theme changed to ${appTheme.themes.find((item) => item.value === nextTheme)?.label}`
      );
    },
    [setColorTheme, srAnnounce]
  );

  const handleColorModeToggle = useCallback(() => {
    const nextMode: ColorMode = isDark ? "light" : "dark";
    setColorMode(nextMode);
    srAnnounce(`Color mode changed to ${nextMode === "dark" ? "Dark" : "Light"}`);
  }, [isDark, setColorMode, srAnnounce]);

  return (
    <>
      <div className="flex items-center gap-1">
        <Button
          type="button"
          variant="ghost"
          size="icon"
          aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
          onClick={handleColorModeToggle}
        >
          {isDark ? <Sun className="size-5" /> : <Moon className="size-5" />}
        </Button>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              aria-label={`Accent theme settings, current theme: ${currentThemeLabel}`}
            >
              <Palette className="size-5" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-44">
            <DropdownMenuRadioGroup value={colorTheme} onValueChange={handleColorThemeChange}>
              {appTheme.themes.map((theme) => (
                <DropdownMenuRadioItem
                  key={theme.value}
                  value={theme.value}
                  className="cursor-pointer gap-2"
                >
                  <span
                    className={`size-3 shrink-0 rounded-full ring-1 ring-border ${theme.colorClass}`}
                    aria-hidden="true"
                  />
                  {theme.label}
                </DropdownMenuRadioItem>
              ))}
            </DropdownMenuRadioGroup>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
      <span className="sr-only" role="status">
        {srAnnouncement}
      </span>
    </>
  );
}
