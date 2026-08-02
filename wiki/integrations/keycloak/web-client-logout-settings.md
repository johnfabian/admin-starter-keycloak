---
type: Integration
title: Web client logout settings
description: Logout-screen settings supported by the current BFF routes.
tags: [keycloak, oidc, logout, sessions]
status: draft
generated: { by: codex/gpt-5, at: 2026-08-02T16:44:19Z }
stale_after: 2026-10-02
sources:
  - id: logout-flow
    resource: /web/app/lib/server/auth.server.ts
    title: Implemented local and Keycloak logout flow
    last_modified: 2026-07-19
  - id: routes
    resource: /web/app/routes.ts
    title: Implemented application routes
    last_modified: 2026-05-21
---

# Current contract

The app accepts a same-origin logout POST, deletes its server-side session best-effort, destroys the browser cookie, and redirects to Keycloak's OIDC end-session endpoint. It supplies `client_id`, the configured post-logout redirect URI, and an ID-token hint when available.[^logout-flow]

No front-channel or backchannel logout callback route exists.[^routes] Keep those URLs blank and their features off; configuring a callback before an implementation exists would point Keycloak at a 404. Register only the exact post-logout origins used by direct and gateway mode.

# Gap

A Keycloak-initiated logout cannot proactively delete the BFF session row because no backchannel endpoint exists. That is a future design decision, not a setting to preconfigure.

# Related concepts

- [Web client settings](/integrations/keycloak/web-client-settings.md)
- [BFF session schema](/schemas/web-bff-sessions.md)

[^logout-flow]: Implemented local and Keycloak logout flow

[^routes]: Implemented application routes
