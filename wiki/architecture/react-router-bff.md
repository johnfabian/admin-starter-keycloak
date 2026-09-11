---
type: Architecture
title: React Router BFF
description: Implemented browser-facing authentication, authorization, token, and session boundary in the React Router server.
resource: /web
tags: [react-router, bff, keycloak, authorization, sessions]
status: draft
generated: { by: codex/gpt-5, at: 2026-08-02T15:45:23Z }
stale_after: 2026-11-02
sources:
  - id: framework-mode
    resource: /web/react-router.config.ts
    title: React Router framework configuration
    last_modified: 2026-05-15
  - id: auth-implementation
    resource: /web/app/lib/server/auth.server.ts
    title: Server authentication implementation
    last_modified: 2026-07-19
  - id: session-cookie
    resource: /web/app/lib/server/session-storage.server.ts
    title: Browser session cookie storage
    last_modified: 2026-05-21
  - id: bff-fetch
    resource: /web/app/lib/server/bff-fetch.server.ts
    title: Authenticated resource-server fetch helper
    last_modified: 2026-05-21
  - id: route-guards
    resource: /web/app/lib/server/route-guards.server.ts
    title: Server route guards
    last_modified: 2026-05-21
---

# Current behavior

The `web/` application runs React Router Framework Mode with server-side rendering enabled.[^framework-mode] Its server code performs the Keycloak authorization-code/PKCE exchange, validates tokens, creates a server-side session, refreshes access tokens, and enforces authenticated or role-scoped route guards.[^auth-implementation][^route-guards]

The browser cookie stores session state with `httpOnly`, `sameSite: lax`, and production-only `secure`; bearer tokens are kept in the server-side session record.[^session-cookie] The `bffFetch` helper adds the access token to outbound server requests and explicitly keeps it out of loader/action JSON.[^bff-fetch]

# Boundary constraints

- Keep browser-specific session and composition work in the React Router server.
- Keep protected-route authorization in server loaders/guards; authentication alone is not sufficient for role-scoped pages.
- Keep access and refresh tokens out of browser-readable storage and responses.
- Treat a future resource API as a separate authorization boundary; the current repository contains only a fetch helper and an Express placeholder.

# Related concepts

- [BFF session schema](/schemas/web-bff-sessions.md)
- [Local edge and identity](/integrations/local-edge-and-identity.md)
- [Repository implementation boundaries](/architecture/repository-boundaries.md)

# Uncertainty

Local Playwright tests exercise login, logout, role access, and session continuity; their [coverage and limits](/testing/automated-local-verification.md) do not establish every token-refresh failure case. The approved production TLS/proxy topology and final downstream resource API are not established in implemented code.

[^framework-mode]: React Router framework configuration

[^auth-implementation]: Server authentication implementation

[^session-cookie]: Browser session cookie storage

[^bff-fetch]: Authenticated resource-server fetch helper

[^route-guards]: Server route guards

# Related decision records

These accepted ADRs record the decisions and tradeoffs; this page retains the current behavior or operational procedure.

- [ADR-0005: Keep browser authentication and token custody in the BFF (accepted)](/adr/ADR-0005-bff-session-and-token-boundary.md)
