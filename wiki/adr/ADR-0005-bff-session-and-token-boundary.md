---
type: Decision
title: "ADR-0005: Keep browser authentication and token custody in the BFF"
description: Proposed decision record extracted from current wiki and source evidence.
tags: [adr, architecture]
adr_id: ADR-0005
decision_status: proposed
status: draft
generated: { by: "codex/gpt-6", at: "2026-09-11T20:32:36Z" }
stale_after: 2026-12-11
sources:
  - id: source-1
    resource: /web/app/lib/server/auth.server.ts
    title: "web/app/lib/server/auth.server.ts"
    last_modified: 2026-07-19
  - id: source-2
    resource: /web/app/lib/server/session-storage.server.ts
    title: "web/app/lib/server/session-storage.server.ts"
    last_modified: 2026-05-21
  - id: source-3
    resource: /web/app/lib/server/bff-session.service.server.ts
    title: "web/app/lib/server/bff-session.service.server.ts"
    last_modified: 2026-05-22
  - id: source-4
    resource: /web/app/lib/server/token-crypto.server.ts
    title: "web/app/lib/server/token-crypto.server.ts"
    last_modified: 2026-05-21
  - id: source-5
    resource: /postgres/init-app-schema.sql
    title: "postgres/init-app-schema.sql"
    last_modified: 2026-05-21
---

# Context

The web application needs Keycloak login, refresh, server-side resource calls, and logout without exposing access or refresh tokens to application browser code.

# Decision proposal

Record the observed React Router server BFF boundary: authorization code with PKCE S256; an opaque HttpOnly browser session identifier; encrypted token payloads in Postgres; and server-only token forwarding. Logout requires a same-origin POST, clears the BFF session best-effort and cookie, and redirects to Keycloak with an ID-token hint when available.

# Alternatives for review

Browser-managed tokens, token-bearing cookies, a separate Express BFF, and local-only logout are comparison options. They are not asserted to have been evaluated or rejected by an identified original decision maker.

# Consequences and limits

The app depends on session storage and encryption-key management. An ID token can appear in the logout redirect URL; this exception is distinct from keeping access/refresh tokens out of browser storage and responses. No front/backchannel logout callback is implemented, and database deletion is best-effort. The exact public/confidential client mode and future API audience remain environment/design choices.

# Approval provenance

This is a proposed record of architecture observed in the cited source. The original approver, decision date and historical rationale were not established. Do not treat implemented behavior as approval or infer that the alternatives below were historically considered.
Acceptance requires an attributable record of the exact outcome and approver. This audit creates no accepted ADR and makes no application, realm, network, or tooling-policy change.

# Evidence and related guidance

Source revision inspected: 342ec668b7848fe0200a9c317812831ca546b885. Draft documents are evidence of design intent, not implemented behavior.

- [architecture/react-router-bff.md](/architecture/react-router-bff.md)
- [schemas/web-bff-sessions.md](/schemas/web-bff-sessions.md)
- [integrations/keycloak/web-client-settings.md](/integrations/keycloak/web-client-settings.md)
- [integrations/keycloak/web-client-logout-settings.md](/integrations/keycloak/web-client-logout-settings.md)
- [integrations/keycloak/web-client-advanced-settings.md](/integrations/keycloak/web-client-advanced-settings.md)
- [integrations/keycloak/realm-session-token-settings.md](/integrations/keycloak/realm-session-token-settings.md)
- [operations/environment-variables.md](/operations/environment-variables.md)

# Supersession

No prior ADR is superseded. Existing records keep their identifiers.
