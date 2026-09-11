---
type: Architecture
title: Gateway network model
description: Public and internal Docker network boundaries in gateway mode.
tags: [docker, networking, traefik, postgres]
status: draft
generated: { by: codex/gpt-5, at: 2026-08-02T16:44:19Z }
stale_after: 2026-11-02
sources:
  - id: gateway-compose
    resource: /api-gateway/docker-compose.yml
    title: Traefik public network
    last_modified: 2026-05-15
  - id: postgres-gateway
    resource: /postgres/docker-compose.gateway.yml
    title: Gateway Postgres internal network
    last_modified: 2026-05-21
  - id: service-networks
    resource: /web/docker-compose.gateway.yml
    title: Web gateway networks
    last_modified: 2026-05-21
---

# Network placement

| Container              | Public network | Internal Postgres network |
| ---------------------- | -------------- | ------------------------- |
| `app-traefik`          | yes            | no                        |
| `app-traefik-web`      | yes            | yes                       |
| `app-traefik-keycloak` | yes            | yes                       |
| `app-traefik-postgres` | no             | yes                       |

The Postgres network is declared `internal: true`, and gateway Postgres publishes no host port.[^postgres-gateway] Web and Keycloak bridge the public and database networks; Traefik joins only the public network.[^gateway-compose][^service-networks]

Keycloak gateway mode sets `KC_PROXY_HEADERS=xforwarded`, `KC_HOSTNAME` from the external URL, and HTTP enabled behind the local proxy. Those settings keep generated redirects and email links aligned with `auth.localhost`; they do not establish a production trust policy.

# Operational consequence

Host database tools cannot connect to gateway Postgres. Use container-scoped tools and the gateway-specific backup/restore scripts, and confirm the exact container and volume before a destructive operation.

# Related concepts

- [Gateway routing](/architecture/gateway-routing.md)
- [Local edge and identity](/integrations/local-edge-and-identity.md)
- [Backup scope](/operations/backup-scope.md)

[^gateway-compose]: Traefik public network

[^postgres-gateway]: Gateway Postgres internal network

[^service-networks]: Web gateway networks

# Related decision records

These accepted ADRs record the decisions and tradeoffs; this page retains the current behavior or operational procedure.

- [ADR-0011: Separate the local gateway edge from database connectivity (accepted)](/adr/ADR-0011-local-gateway-isolation.md)
