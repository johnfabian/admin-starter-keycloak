---
type: Decision
title: "ADR-0011: Separate the local gateway edge from database connectivity"
description: Accepted architectural decision with attributable conversation approval recorded in PR 20.
tags: [adr, architecture]
adr_id: ADR-0011
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
    resource: /api-gateway/docker-compose.yml
    title: "api-gateway/docker-compose.yml"
    last_modified: 2026-08-01
  - id: source-2
    resource: /postgres/docker-compose.gateway.yml
    title: "postgres/docker-compose.gateway.yml"
    last_modified: 2026-05-21
  - id: source-3
    resource: /web/docker-compose.gateway.yml
    title: "web/docker-compose.gateway.yml"
    last_modified: 2026-05-21
  - id: source-4
    resource: /auth-server/docker-compose.gateway.yml
    title: "auth-server/docker-compose.gateway.yml"
    last_modified: 2026-05-22
---

# Context

Gateway mode routes local web and identity traffic through Traefik while limiting database reachability.

# Decision

Record the observed gateway boundary: explicit Docker router opt-in, a public service network, and a separate internal Postgres network with no gateway-mode host database port. Web and Keycloak connect to both relevant networks; Traefik does not join the Postgres network.

# Alternatives for review

One shared network, a host-published gateway database port, or separate per-service infrastructure are comparison options. No original alternatives record is established.

# Consequences and limits

Host database tools cannot directly use gateway Postgres; container-scoped tools and mode-specific recovery are required. Direct mode differs. Local HTTP, the unauthenticated dashboard and Docker socket access are limitations, not accepted production security choices. Production TLS and forwarded-header trust require a separate design.

# Approval provenance

Accepted on 2026-09-11 by the requesting human user in the Codex conversation (human:requesting-user). The user said: "lets not worrry about orca right now, but the ADRs look good to me".

The approval covers ADR-0001 through ADR-0012 as presented at commit 04e3abe09195516104180fb4f10ba23394cd1f04. It was transcribed into [PR #20](https://github.com/johnfabian/admin-starter-keycloak/pull/20#adr-acceptance---2026-09-11) and exactly reread before acceptance. This is conversation approval recorded by the assistant, not a GitHub review submitted by the human. No GitHub identity is inferred.

Acceptance confirms the architectural choice; it does not claim historical approval, independent runtime verification, production readiness, deployment or PR merge authorization. ORCA is deferred and does not block the accepted workflow.

The previous proposed record remains available at the approved Git revision. Record-ADR skill version: 04e3abe09195516104180fb4f10ba23394cd1f04.

# Evidence and related guidance

Source revision inspected: 342ec668b7848fe0200a9c317812831ca546b885. Draft documents are evidence of design intent, not implemented behavior.

- [architecture/gateway-network-model.md](/architecture/gateway-network-model.md)
- [architecture/gateway-routing.md](/architecture/gateway-routing.md)
- [integrations/local-edge-and-identity.md](/integrations/local-edge-and-identity.md)
- [integrations/traefik-static-config.md](/integrations/traefik-static-config.md)
- [operations/local-stack.md](/operations/local-stack.md)
- [operations/troubleshoot-gateway.md](/operations/troubleshoot-gateway.md)

# Supersession

No prior ADR is superseded. Existing records keep their identifiers.
