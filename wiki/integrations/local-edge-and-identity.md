---
type: Integration
title: Local edge and identity
description: Current local gateway topology for Traefik, Keycloak, the React Router app, and Postgres.
tags: [traefik, keycloak, docker, postgres, local-development]
status: draft
generated: { by: codex/gpt-5, at: 2026-08-02T15:45:23Z }
stale_after: 2026-10-02
sources:
  - id: gateway-compose
    resource: /api-gateway/docker-compose.yml
    title: Traefik Compose configuration
    last_modified: 2026-05-15
  - id: keycloak-compose
    resource: /auth-server/docker-compose.gateway.yml
    title: Gateway-mode Keycloak Compose configuration
    last_modified: 2026-05-22
  - id: web-compose
    resource: /web/docker-compose.gateway.yml
    title: Gateway-mode web Compose configuration
    last_modified: 2026-05-21
  - id: postgres-compose
    resource: /postgres/docker-compose.gateway.yml
    title: Gateway-mode Postgres Compose configuration
    last_modified: 2026-05-21
---

# Implemented local topology

Traefik 3.2 listens on HTTP port 80, uses Docker discovery with `exposedByDefault=false`, and exposes an insecure local dashboard on host port 8081.[^gateway-compose] The web and Keycloak containers opt into host-based routing on the shared `admin-starter-public` network.[^web-compose][^keycloak-compose]

Keycloak also joins the gateway Postgres network and enables `xforwarded` proxy headers.[^keycloak-compose] Gateway Postgres is attached only to an internal Docker network and publishes no host port.[^postgres-compose]

# Security boundary

This is development configuration, not a production TLS topology. The current gateway file has no HTTPS entrypoint, certificate resolver, trusted forwarded-source configuration, or protected dashboard.[^gateway-compose] Do not present it as production-ready.

# Related concepts

- [React Router BFF](/architecture/react-router-bff.md)
- [Gateway routing](/architecture/gateway-routing.md)
- [Gateway network model](/architecture/gateway-network-model.md)
- [Traefik static configuration](/integrations/traefik-static-config.md)
- [Troubleshoot the gateway](/operations/troubleshoot-gateway.md)
- [BFF session schema](/schemas/web-bff-sessions.md)

# Uncertainty

The approved production TLS mode, trusted proxy addresses, management-path exposure, security middleware, telemetry, retention, and alert ownership are not established in the implemented Compose files.

[^gateway-compose]: Traefik Compose configuration

[^keycloak-compose]: Gateway-mode Keycloak Compose configuration

[^web-compose]: Gateway-mode web Compose configuration

[^postgres-compose]: Gateway-mode Postgres Compose configuration

# Related decision records

These proposals record the decision and tradeoffs; this page retains the current behavior or operational procedure.

- [ADR-0011: Separate the local gateway edge from database connectivity (proposed)](/adr/ADR-0011-local-gateway-isolation.md)
