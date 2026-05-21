import { createContext, useCallback, useEffect, useMemo, useSyncExternalStore } from "react";

import { appTheme, type ColorMode, type ColorTheme } from "~/lib/app-settings.shared";
import { getLocalStorageValue, setLocalStorageValue } from "~/lib/local-storage.shared";

interface ThemeContextType {
  colorMode: ColorMode;
  colorTheme: ColorTheme;
  setColorMode: (mode: ColorMode) => void;
  setColorTheme: (theme: ColorTheme) => void;
}

export const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

const VALID_MODES: ColorMode[] = appTheme.modes.map((mode) => mode.value);
const VALID_THEMES: ColorTheme[] = appTheme.themes.map((theme) => theme.value);
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

  const savedMode = getLocalStorageValue(appTheme.storageKeys.mode) as ColorMode | null;
  return savedMode && VALID_MODES.includes(savedMode) ? savedMode : DEFAULT_COLOR_MODE;
}

function getSavedColorTheme(): ColorTheme {
  if (typeof window === "undefined") return DEFAULT_COLOR_THEME;

  const savedTheme = getLocalStorageValue(appTheme.storageKeys.theme) as ColorTheme | null;
  return savedTheme && VALID_THEMES.includes(savedTheme) ? savedTheme : DEFAULT_COLOR_THEME;
}

function notifyThemeStorage() {
  window.dispatchEvent(new Event(appTheme.storageEvent));
}

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const colorMode = useSyncExternalStore(
    subscribeToThemeStorage,
    getSavedColorMode,
    () => DEFAULT_COLOR_MODE
  );
  const colorTheme = useSyncExternalStore(
    subscribeToThemeStorage,
    getSavedColorTheme,
    () => DEFAULT_COLOR_THEME
  );

  const setColorMode = useCallback((mode: ColorMode) => {
    if (!VALID_MODES.includes(mode)) return;
    if (setLocalStorageValue(appTheme.storageKeys.mode, mode)) {
      notifyThemeStorage();
    }
  }, []);

  const setColorTheme = useCallback((theme: ColorTheme) => {
    if (!VALID_THEMES.includes(theme)) return;
    if (setLocalStorageValue(appTheme.storageKeys.theme, theme)) {
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
