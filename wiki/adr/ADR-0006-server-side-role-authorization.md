---
type: Decision
title: "ADR-0006: Enforce routes server-side using the current role contract"
description: Proposed decision record extracted from current wiki and source evidence.
tags: [adr, architecture]
adr_id: ADR-0006
decision_status: proposed
status: draft
generated: { by: "codex/gpt-6", at: "2026-09-11T20:32:36Z" }
stale_after: 2026-12-11
sources:
  - id: source-1
    resource: /web/app/lib/server/current-user.server.ts
    title: "web/app/lib/server/current-user.server.ts"
    last_modified: 2026-09-11
  - id: source-2
    resource: /web/app/lib/server/route-guards.server.ts
    title: "web/app/lib/server/route-guards.server.ts"
    last_modified: 2026-05-21
  - id: source-3
    resource: /web/app/lib/app-settings.shared.ts
    title: "web/app/lib/app-settings.shared.ts"
    last_modified: 2026-05-22
---

# Context

Authentication alone does not grant access to the starter's user and administrator areas.

# Decision proposal

Record the observed server-guard contract: Users or Admins can access user areas; Admins is required for administrator areas. Role extraction unions realm roles with roles for the configured web client, using exact case-sensitive strings. Navigation visibility is not authorization. A future resource API needs its own token and permission checks.

# Alternatives for review

Client-only role checks, web-client roles only, realm roles only, or a new permission model are comparison options. No historical choice or rejection rationale is established here.

# Consequences and limits

Identically named realm and client roles are equivalent in today's union, which can matter when multiple applications share identity. New protected routes must use server guards. This ADR does not approve a cross-application role model or a new API audience; those decisions need separate requirements.

# Approval provenance

This is a proposed record of architecture observed in the cited source. The original approver, decision date and historical rationale were not established. Do not treat implemented behavior as approval or infer that the alternatives below were historically considered.
Acceptance requires an attributable record of the exact outcome and approver. This audit creates no accepted ADR and makes no application, realm, network, or tooling-policy change.

# Evidence and related guidance

Source revision inspected: 342ec668b7848fe0200a9c317812831ca546b885. Draft documents are evidence of design intent, not implemented behavior.

- [architecture/access-control-model.md](/architecture/access-control-model.md)
- [integrations/keycloak/realm-and-client-facts.md](/integrations/keycloak/realm-and-client-facts.md)
- [operations/create-admin-user.md](/operations/create-admin-user.md)
- [integrations/express-resource-api.md](/integrations/express-resource-api.md)

# Supersession

No prior ADR is superseded. Existing records keep their identifiers.
