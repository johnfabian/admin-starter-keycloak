import { appTheme, type ColorMode, type ColorTheme } from "~/lib/app-settings.shared";

export const themeModes = appTheme.modes.map((mode) => mode.value);
export const themeColors = appTheme.themes.map((theme) => theme.value);

export function isColorMode(value: string | null | undefined): value is ColorMode {
  return Boolean(value && themeModes.includes(value as ColorMode));
}

export function isColorTheme(value: string | null | undefined): value is ColorTheme {
  return Boolean(value && themeColors.includes(value as ColorTheme));
}

export function getValidColorMode(value: string | null | undefined) {
  return isColorMode(value) ? value : appTheme.defaultMode;
}

export function getValidColorTheme(value: string | null | undefined) {
  return isColorTheme(value) ? value : appTheme.defaultTheme;
}

