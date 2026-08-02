const SECURITY_HEADER_NAMES = {
  cacheControl: "Cache-Control",
  contentSecurityPolicy: "Content-Security-Policy",
  permissionsPolicy: "Permissions-Policy",
  pragma: "Pragma",
  referrerPolicy: "Referrer-Policy",
  strictTransportSecurity: "Strict-Transport-Security",
  xContentTypeOptions: "X-Content-Type-Options",
} as const;

const SECURITY_HEADER_VALUES = {
  cacheNoStore: "no-store",
  contentSecurityPolicy: [
    "default-src 'self'",
    "base-uri 'self'",
    "object-src 'none'",
    "frame-ancestors 'none'",
    "form-action 'self'",
    // The app authors no inline scripts (theme FOUC is prevented by server-rendered
    // <html> attributes, not a script). React Router does: <Scripts> emits the client
    // entry import and window.__reactRouterContext inline, and React's streaming
    // runtime emits its own. Without 'unsafe-inline' the browser blocks all of them,
    // hydration never runs, and every interactive control is dead.
    // Dev additionally needs 'unsafe-eval' for the Vite HMR client.
    // Production still needs a per-request nonce here; see entry.server.tsx.
    `script-src 'self'${import.meta.env.DEV ? " 'unsafe-inline' 'unsafe-eval'" : ""}`,
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "font-src 'self' https://fonts.gstatic.com data:",
    "img-src 'self' data: blob:",
    `connect-src 'self'${import.meta.env.DEV ? " ws: http://localhost:* http://127.0.0.1:*" : ""}`,
  ].join("; "),
  permissionsPolicy: "camera=(), microphone=(), geolocation=(), payment=()",
  pragmaNoCache: "no-cache",
  referrerPolicy: "no-referrer",
  strictTransportSecurity: "max-age=31536000; includeSubDomains",
  xContentTypeOptions: "nosniff",
} as const;

export function getSecurityHeaders() {
  const headers = new Headers();

  headers.set(
    SECURITY_HEADER_NAMES.contentSecurityPolicy,
    SECURITY_HEADER_VALUES.contentSecurityPolicy
  );
  headers.set(SECURITY_HEADER_NAMES.referrerPolicy, SECURITY_HEADER_VALUES.referrerPolicy);
  headers.set(
    SECURITY_HEADER_NAMES.xContentTypeOptions,
    SECURITY_HEADER_VALUES.xContentTypeOptions
  );
  headers.set(SECURITY_HEADER_NAMES.permissionsPolicy, SECURITY_HEADER_VALUES.permissionsPolicy);

  if (!import.meta.env.DEV) {
    headers.set(
      SECURITY_HEADER_NAMES.strictTransportSecurity,
      SECURITY_HEADER_VALUES.strictTransportSecurity
    );
  }

  return headers;
}

export function getNoStoreHeaders(headersInit?: HeadersInit) {
  const headers = new Headers(headersInit);

  headers.set(SECURITY_HEADER_NAMES.cacheControl, SECURITY_HEADER_VALUES.cacheNoStore);
  headers.set(SECURITY_HEADER_NAMES.pragma, SECURITY_HEADER_VALUES.pragmaNoCache);
  headers.set(SECURITY_HEADER_NAMES.referrerPolicy, SECURITY_HEADER_VALUES.referrerPolicy);

  return headers;
}
