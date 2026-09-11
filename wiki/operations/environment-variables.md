---
type: Runbook
title: Environment variables
description: Required BFF variables, safe templates, mode differences, and restart-sensitive values.
tags: [environment, configuration, secrets, react-router]
status: draft
generated: { by: codex/gpt-5, at: 2026-08-02T16:44:19Z }
stale_after: 2026-10-02
sources:
  - id: auth-config
    resource: /web/app/lib/server/auth-config.server.ts
    title: BFF authentication configuration loader
    last_modified: 2026-05-21
  - id: direct-template
    resource: /.env.example
    title: Direct-stack environment template
    last_modified: 2026-05-21
  - id: gateway-template
    resource: /.env.traefik.example
    title: Gateway environment template
    last_modified: 2026-05-21
---

# Required by the BFF

`KEYCLOAK_ISSUER`, `WEB_KEYCLOAK_CLIENT_ID`, `WEB_AUTH_REDIRECT_URI`, `WEB_AUTH_POST_LOGIN_REDIRECT_URI`, `WEB_AUTH_POST_LOGOUT_REDIRECT_URI`, `WEB_SESSION_SECRET`, `WEB_DATABASE_URL`, and `WEB_TOKEN_ENCRYPTION_KEY` must be non-empty.[^auth-config]

The two secrets must each be at least 32 characters. Keep them distinct, private, and out of logs, issues, handoffs, and Git. Missing required values make `hasAuthConfig()` report no auth configuration; direct login attempts then surface the missing variable through `getAuthConfig()`.

# Optional BFF values

- `WEB_KEYCLOAK_CLIENT_SECRET`: empty for the documented public PKCE mode.
- `WEB_RESOURCE_SERVER_BASE_URL`: placeholder until a resource API exists.
- `WEB_KEYCLOAK_API_AUDIENCE`: empty in templates; an eventual API needs an explicit audience and matching Keycloak mapper.
- `WEB_TOKEN_REFRESH_LEEWAY_SECONDS`: defaults to 60.
- `WEB_SESSION_LAST_SEEN_UPDATE_SECONDS`: defaults to 300.

# Files and modes

Use `.env.development` for direct mode and `.env.traefik` for gateway mode. Both are gitignored; edit the example files only to change safe names or placeholders.[^direct-template][^gateway-template] Direct URLs use `localhost` ports, while gateway URLs use `app.localhost`, `auth.localhost`, and container DNS for the database.

Restart the affected app or container after changing configuration. Rotating either BFF secret signs users out; changing the token-encryption key also makes stored token payloads unreadable.

# Related concepts

- [Realm and client facts](/integrations/keycloak/realm-and-client-facts.md)
- [Local stack](/operations/local-stack.md)
- [BFF session schema](/schemas/web-bff-sessions.md)

[^auth-config]: BFF authentication configuration loader

[^direct-template]: Direct-stack environment template

[^gateway-template]: Gateway environment template

# Related decision records

These accepted ADRs record the decisions and tradeoffs; this page retains the current behavior or operational procedure.

- [ADR-0005: Keep browser authentication and token custody in the BFF (accepted)](/adr/ADR-0005-bff-session-and-token-boundary.md)
