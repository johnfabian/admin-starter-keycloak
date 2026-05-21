import { createContext, useCallback, useEffect, useMemo, useSyncExternalStore } from "react";

import { appTheme, type ColorMode, type ColorTheme } from "~/lib/app-settings.shared";
import { getLocalStorageValue, setLocalStorageValue } from "~/lib/local-storage.shared";
import { getValidColorMode, getValidColorTheme, themeColors, themeModes } from "~/lib/theme.shared";

interface ThemeContextType {
  colorMode: ColorMode;
  colorTheme: ColorTheme;
  setColorMode: (mode: ColorMode) => void;
  setColorTheme: (theme: ColorTheme) => void;
}

export const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

const DEFAULT_COLOR_MODE = appTheme.defaultMode;
const DEFAULT_COLOR_THEME = appTheme.defaultTheme;

function subscribeToThemeStorage(callback: () => void) {
  if (typeof window === "undefined") return () => {};

  window.addEventListener("storage", callback);
  window.addEventListener(appTheme.storageEvent, callback);

  return () => {
    window.removeEventListener("storage", callback);
    window.removeEventListener(appTheme.storageEvent, callback);
  };
}

function getSavedColorMode(): ColorMode {
  if (typeof window === "undefined") return DEFAULT_COLOR_MODE;

  return getValidColorMode(getLocalStorageValue(appTheme.storageKeys.mode));
}

function getSavedColorTheme(): ColorTheme {
  if (typeof window === "undefined") return DEFAULT_COLOR_THEME;

  return getValidColorTheme(getLocalStorageValue(appTheme.storageKeys.theme));
}

function notifyThemeStorage() {
  window.dispatchEvent(new Event(appTheme.storageEvent));
}

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
  const colorMode = useSyncExternalStore(
    subscribeToThemeStorage,
    getSavedColorMode,
    () => initialColorMode
  );
  const colorTheme = useSyncExternalStore(
    subscribeToThemeStorage,
    getSavedColorTheme,
    () => initialColorTheme
  );

  const setColorMode = useCallback((mode: ColorMode) => {
    if (!themeModes.includes(mode)) return;
    if (setLocalStorageValue(appTheme.storageKeys.mode, mode)) {
      setThemeCookie(appTheme.cookieKeys.mode, mode);
      notifyThemeStorage();
    }
  }, []);

  const setColorTheme = useCallback((theme: ColorTheme) => {
    if (!themeColors.includes(theme)) return;
    if (setLocalStorageValue(appTheme.storageKeys.theme, theme)) {
      setThemeCookie(appTheme.cookieKeys.theme, theme);
      notifyThemeStorage();
    }
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
