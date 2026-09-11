---
type: Integration
title: Web client settings
description: Draft main-screen configuration for the admin-starter-web OIDC client.
tags: [keycloak, oidc, client, pkce]
status: draft
generated: { by: codex/gpt-5, at: 2026-08-02T16:44:19Z }
stale_after: 2026-10-02
sources:
  - id: auth-flow
    resource: /web/app/lib/server/auth.server.ts
    title: Implemented OIDC authorization flow
    last_modified: 2026-07-19
  - id: auth-config
    resource: /web/app/lib/server/auth-config.server.ts
    title: Implemented client configuration
    last_modified: 2026-05-21
  - id: env-templates
    resource: /.env.example
    title: Direct-stack URI template
    last_modified: 2026-05-21
---

# Client capabilities

For `admin-starter-web`, the implemented flow supports OpenID Connect standard flow with PKCE S256. Direct access grants, implicit flow, service accounts, device authorization, CIBA, and Keycloak Authorization Services have no implementation in this app and should remain off unless separately designed.[^auth-flow]

`WEB_KEYCLOAK_CLIENT_SECRET` is optional. Empty supports a public PKCE client; setting a secret supports a confidential client only when the Keycloak client authentication setting changes with it.[^auth-config]

# Local URL allowlists

Use exact callback and origins for the mode in use:

| Field              | Direct                                | Gateway                              |
| ------------------ | ------------------------------------- | ------------------------------------ |
| Root/Home URL      | `http://localhost:5173`               | `http://app.localhost`               |
| Callback           | `http://localhost:5173/auth/callback` | `http://app.localhost/auth/callback` |
| Post logout origin | `http://localhost:5173`               | `http://app.localhost`               |
| Web origin         | `http://localhost:5173`               | `http://app.localhost`               |

Prefer exact redirect URIs over broad wildcards. The code requests `openid profile email`; role claims must also be mapped so `Users` and `Admins` appear in the access token.[^env-templates]

# Uncertainty

The repository cannot verify the live client's authentication mode, scope mappings, redirect allowlist, or Full scope allowed setting.

# Related concepts

- [Realm and client facts](/integrations/keycloak/realm-and-client-facts.md)
- [Web client advanced settings](/integrations/keycloak/web-client-advanced-settings.md)
- [Web client logout settings](/integrations/keycloak/web-client-logout-settings.md)

[^auth-flow]: Implemented OIDC authorization flow

[^auth-config]: Implemented client configuration

[^env-templates]: Direct-stack URI template

# Related decision records

These accepted ADRs record the decisions and tradeoffs; this page retains the current behavior or operational procedure.

- [ADR-0005: Keep browser authentication and token custody in the BFF (accepted)](/adr/ADR-0005-bff-session-and-token-boundary.md)
