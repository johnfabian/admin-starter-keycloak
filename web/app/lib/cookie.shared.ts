export function getCookieValue(cookieHeader: string | null | undefined, key: string) {
  const value = cookieHeader
    ?.split(";")
    .map((cookie) => cookie.trim())
    .find((cookie) => cookie.startsWith(`${key}=`))
    ?.slice(key.length + 1);

  if (!value) return null;

  try {
    return decodeURIComponent(value);
  } catch {
    return null;
  }
}
