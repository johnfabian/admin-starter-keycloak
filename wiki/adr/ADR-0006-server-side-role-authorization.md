---
type: Decision
title: "ADR-0006: Enforce routes server-side using the current role contract"
description: Accepted architectural decision with attributable conversation approval recorded in PR 20.
tags: [adr, architecture]
adr_id: ADR-0006
decision_status: accepted
decided_on: 2026-09-11
approved_by: "human:requesting-user"
status: stable
generated: { by: "codex/gpt-6", at: "2026-09-11T20:32:36Z" }
stale_after: 2026-12-11
verified: { by: human:requesting-user, at: "2026-09-11T21:27:10.569994+00:00" }
sources:
  - id: acceptance
    resource: https://github.com/johnfabian/admin-starter-keycloak/pull/20#adr-acceptance---2026-09-11
    title: Conversation approval of the exact ADR set recorded in PR 20
    author: "human:requesting-user"
    last_modified: 2026-09-11
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

# Decision

Record the observed server-guard contract: Users or Admins can access user areas; Admins is required for administrator areas. Role extraction unions realm roles with roles for the configured web client, using exact case-sensitive strings. Navigation visibility is not authorization. A future resource API needs its own token and permission checks.

# Alternatives for review

Client-only role checks, web-client roles only, realm roles only, or a new permission model are comparison options. No historical choice or rejection rationale is established here.

# Consequences and limits

Identically named realm and client roles are equivalent in today's union, which can matter when multiple applications share identity. New protected routes must use server guards. This ADR does not approve a cross-application role model or a new API audience; those decisions need separate requirements.

# Approval provenance

Accepted on 2026-09-11 by the requesting human user in the Codex conversation (human:requesting-user). The user said: "lets not worrry about orca right now, but the ADRs look good to me".

The approval covers ADR-0001 through ADR-0012 as presented at commit 04e3abe09195516104180fb4f10ba23394cd1f04. It was transcribed into [PR #20](https://github.com/johnfabian/admin-starter-keycloak/pull/20#adr-acceptance---2026-09-11) and exactly reread before acceptance. This is conversation approval recorded by the assistant, not a GitHub review submitted by the human. No GitHub identity is inferred.

Acceptance confirms the architectural choice; it does not claim historical approval, independent runtime verification, production readiness, deployment or PR merge authorization. ORCA is deferred and does not block the accepted workflow.

The previous proposed record remains available at the approved Git revision. Record-ADR skill version: 04e3abe09195516104180fb4f10ba23394cd1f04.

# Evidence and related guidance

Source revision inspected: 342ec668b7848fe0200a9c317812831ca546b885. Draft documents are evidence of design intent, not implemented behavior.

- [architecture/access-control-model.md](/architecture/access-control-model.md)
- [integrations/keycloak/realm-and-client-facts.md](/integrations/keycloak/realm-and-client-facts.md)
- [operations/create-admin-user.md](/operations/create-admin-user.md)
- [integrations/express-resource-api.md](/integrations/express-resource-api.md)

# Supersession

No prior ADR is superseded. Existing records keep their identifiers.
