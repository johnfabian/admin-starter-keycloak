---
type: Integration
title: Realm and client facts
description: Keycloak identifiers, roles, and local URIs referenced by the implemented BFF.
tags: [keycloak, oidc, roles, configuration]
status: draft
generated: { by: codex/gpt-5, at: 2026-08-02T16:44:19Z }
stale_after: 2026-11-02
sources:
  - id: direct-env
    resource: /.env.example
    title: Direct-stack environment template
    last_modified: 2026-05-21
  - id: gateway-env
    resource: /.env.traefik.example
    title: Gateway environment template
    last_modified: 2026-05-21
  - id: access-settings
    resource: /web/app/lib/app-settings.shared.ts
    title: Implemented role constants
    last_modified: 2026-05-22
---

# Implemented identifiers

| Item                     | Current value                                  |
| ------------------------ | ---------------------------------------------- |
| Realm in issuer examples | `admin-starter`                                |
| Web client               | `admin-starter-web`                            |
| Application roles        | `Users`, `Admins` (exact case)                 |
| Express client/audience  | `admin-starter-api-express` (placeholder only) |

Direct mode uses `http://localhost:8080/realms/admin-starter` as issuer and `http://localhost:5173/auth/callback` as the redirect URI. Gateway mode uses `http://auth.localhost/realms/admin-starter` and `http://app.localhost/auth/callback`.[^direct-env][^gateway-env]

The code requests `openid profile email`, uses authorization code with PKCE S256, and sends `WEB_KEYCLOAK_CLIENT_SECRET` only when configured. Access roles are read from both realm roles and the web client's client roles.[^access-settings]

# Drift warning

These values are represented in code and templates, but the realm and client are configured manually. No realm file proves the live client type, flows, scopes, mappers, or role assignments.

# Related concepts

- [Access control model](/architecture/access-control-model.md)
- [Web client settings](/integrations/keycloak/web-client-settings.md)
- [Environment variables](/operations/environment-variables.md)

[^direct-env]: Direct-stack environment template

[^gateway-env]: Gateway environment template

[^access-settings]: Implemented role constants

# Related decision records

These accepted ADRs record the decisions and tradeoffs; this page retains the current behavior or operational procedure.

- [ADR-0006: Enforce routes server-side using the current role contract (accepted)](/adr/ADR-0006-server-side-role-authorization.md)
