---
type: Decision
title: "ADR-0011: Separate the local gateway edge from database connectivity"
description: Proposed decision record extracted from current wiki and source evidence.
tags: [adr, architecture]
adr_id: ADR-0011
decision_status: proposed
status: draft
generated: { by: "codex/gpt-6", at: "2026-09-11T20:32:36Z" }
stale_after: 2026-12-11
sources:
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

# Decision proposal

Record the observed gateway boundary: explicit Docker router opt-in, a public service network, and a separate internal Postgres network with no gateway-mode host database port. Web and Keycloak connect to both relevant networks; Traefik does not join the Postgres network.

# Alternatives for review

One shared network, a host-published gateway database port, or separate per-service infrastructure are comparison options. No original alternatives record is established.

# Consequences and limits

Host database tools cannot directly use gateway Postgres; container-scoped tools and mode-specific recovery are required. Direct mode differs. Local HTTP, the unauthenticated dashboard and Docker socket access are limitations, not accepted production security choices. Production TLS and forwarded-header trust require a separate design.

# Approval provenance

This is a proposed record of architecture observed in the cited source. The original approver, decision date and historical rationale were not established. Do not treat implemented behavior as approval or infer that the alternatives below were historically considered.
Acceptance requires an attributable record of the exact outcome and approver. This audit creates no accepted ADR and makes no application, realm, network, or tooling-policy change.

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
