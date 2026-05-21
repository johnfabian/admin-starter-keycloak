export function joinNonEmpty(parts: Array<string | null | undefined>, separator = " ") {
  return parts.filter((part): part is string => Boolean(part)).join(separator);
}

export function getInitials(
  parts: Array<string | null | undefined>,
  fallback?: string | null,
  defaultValue = "U"
) {
  const initials = joinNonEmpty(
    parts.map((part) => part?.charAt(0).toUpperCase()),
    ""
  );

  return initials || fallback?.charAt(0).toUpperCase() || defaultValue;
}

export function getStringValue(source: Record<string, unknown>, key: string) {
  const value = source[key];
  return typeof value === "string" ? value : "";
}

export function trimTrailingSlash(value: string) {
  return value.replace(/\/$/, "");
}

export function isAppPath(value: string) {
  return value.startsWith("/");
}

export function isPathActive(pathname: string, targetPath: string, exact = false) {
  return exact
    ? pathname === targetPath
    : pathname === targetPath || pathname.startsWith(`${targetPath}/`);
}

export function toBase64Url(base64: string) {
  return base64.replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}
