---
type: Integration
title: Web client advanced settings
description: Draft advanced-screen baseline for the admin-starter-web OIDC client.
tags: [keycloak, oidc, client, tokens]
status: draft
generated: { by: codex/gpt-5, at: 2026-08-02T16:44:19Z }
stale_after: 2026-10-02
sources:
  - id: token-verification
    resource: /web/app/lib/server/oauth-token.service.server.ts
    title: BFF token verification
    last_modified: 2026-05-22
  - id: pkce
    resource: /web/app/lib/server/oauth-pkce.server.ts
    title: PKCE implementation
    last_modified: 2026-05-12
---

# Draft baseline

Under Clients → `admin-starter-web` → Advanced, leave access-token and client-session lifetimes empty to inherit the realm unless a shorter, reviewed override is required. Keep PKCE Code Challenge Method at `S256`; the app generates an S256 challenge.[^pkce]

Device Authorization Grant, CIBA Grant, and Valid request URIs have no implemented consumer and should remain off or blank. The migrated setup guidance used RS256 for access and ID token signatures; the BFF verifies signed tokens against the issuer's JWKS, but the live algorithm configuration is not represented in the repository.[^token-verification]

If a lifetime is overridden, compare it with the realm limits and the BFF's refresh leeway. An apparently valid console value can still produce excessive refreshes or be bounded by the realm.

# Related concepts

- [Realm session and token settings](/integrations/keycloak/realm-session-token-settings.md)
- [Web client settings](/integrations/keycloak/web-client-settings.md)

[^token-verification]: BFF token verification

[^pkce]: PKCE implementation
