import { createContext, useCallback, useEffect, useMemo, useState } from "react";

import { appTheme, type ColorMode, type ColorTheme } from "~/lib/app-settings.shared";
import { themeColors, themeModes } from "~/lib/theme.shared";

interface ThemeContextType {
  colorMode: ColorMode;
  colorTheme: ColorTheme;
  setColorMode: (mode: ColorMode) => void;
  setColorTheme: (theme: ColorTheme) => void;
}

export const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

const DEFAULT_COLOR_MODE = appTheme.defaultMode;
const DEFAULT_COLOR_THEME = appTheme.defaultTheme;

function setThemeCookie(key: string, value: string) {
  document.cookie = `${key}=${encodeURIComponent(value)}; Max-Age=${
    appTheme.cookieMaxAgeSeconds
  }; Path=${appTheme.cookiePath}; SameSite=Lax`;
}

export function ThemeProvider({
  children,
  initialColorMode = DEFAULT_COLOR_MODE,
  initialColorTheme = DEFAULT_COLOR_THEME,
}: {
  children: React.ReactNode;
  initialColorMode?: ColorMode;
  initialColorTheme?: ColorTheme;
}) {
  const [colorMode, setColorModeState] = useState(initialColorMode);
  const [colorTheme, setColorThemeState] = useState(initialColorTheme);

  const setColorMode = useCallback((mode: ColorMode) => {
    if (!themeModes.includes(mode)) return;
    setColorModeState(mode);
  }, []);

  const setColorTheme = useCallback((theme: ColorTheme) => {
    if (!themeColors.includes(theme)) return;
    setColorThemeState(theme);
  }, []);

  useEffect(() => {
    const root = document.documentElement;
    root.setAttribute("data-theme", colorTheme);

    const applyDarkMode = (enabled: boolean) => {
      root.classList.toggle("dark", enabled);
      root.style.colorScheme = enabled ? "dark" : "light";
    };

    if (colorMode === "system") {
      applyDarkMode(window.matchMedia(appTheme.systemDarkModeQuery).matches);
    } else {
      applyDarkMode(colorMode === "dark");
    }

    setThemeCookie(appTheme.cookieKeys.mode, colorMode);
    setThemeCookie(appTheme.cookieKeys.theme, colorTheme);
  }, [colorMode, colorTheme]);

  useEffect(() => {
    if (colorMode !== "system") return;

    const mediaQuery = window.matchMedia(appTheme.systemDarkModeQuery);
    const handleChange = (event: MediaQueryListEvent) => {
      document.documentElement.classList.toggle("dark", event.matches);
      document.documentElement.style.colorScheme = event.matches ? "dark" : "light";
    };

    mediaQuery.addEventListener("change", handleChange);
    return () => mediaQuery.removeEventListener("change", handleChange);
  }, [colorMode]);

  const value = useMemo(
    () => ({ colorMode, colorTheme, setColorMode, setColorTheme }),
    [colorMode, colorTheme, setColorMode, setColorTheme]
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}
