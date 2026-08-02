---
type: Integration
title: Realm session and token settings
description: Draft Keycloak realm lifetime baseline and its interaction with BFF refresh behavior.
tags: [keycloak, sessions, tokens, configuration]
status: draft
generated: { by: codex/gpt-5, at: 2026-08-02T16:44:19Z }
stale_after: 2026-10-02
sources:
  - id: auth-config
    resource: /web/app/lib/server/auth-config.server.ts
    title: BFF refresh configuration
    last_modified: 2026-05-21
  - id: token-service
    resource: /web/app/lib/server/oauth-token.service.server.ts
    title: Token refresh and validation service
    last_modified: 2026-05-22
---

# Draft console baseline

The migrated setup guidance used these realm-level values: SSO Session Idle 30 minutes, SSO Session Max 8 hours, Access Token Lifespan 5 minutes, Client Login Timeout 1 minute, Login Timeout 5 minutes, and Login Action Timeout 5 minutes. Client session overrides were left empty to inherit the realm.

These values are not stored or checked in this repository. Confirm them under Realm settings → Sessions and Tokens before treating them as current.

# Code coupling

The BFF refreshes an access token when it is within `WEB_TOKEN_REFRESH_LEEWAY_SECONDS` of expiry; the default is 60 seconds.[^auth-config][^token-service] Keep that window well below the live access-token lifetime. Realm SSO limits also bound whether a refresh token remains usable, regardless of how long a BFF session row exists.

# Related concepts

- [Web client advanced settings](/integrations/keycloak/web-client-advanced-settings.md)
- [Environment variables](/operations/environment-variables.md)
- [BFF session schema](/schemas/web-bff-sessions.md)

[^auth-config]: BFF refresh configuration

[^token-service]: Token refresh and validation service
