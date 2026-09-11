---
type: Runbook
title: Troubleshoot the gateway
description: Evidence order for local Traefik 404s, backend failures, redirects, and database access.
tags: [traefik, docker, gateway, troubleshooting]
status: draft
generated: { by: codex/gpt-5, at: 2026-08-02T16:44:19Z }
stale_after: 2026-10-02
sources:
  - id: gateway-compose
    resource: /api-gateway/docker-compose.yml
    title: Traefik discovery and entrypoint configuration
    last_modified: 2026-05-15
  - id: web-gateway
    resource: /web/docker-compose.gateway.yml
    title: Web router configuration
    last_modified: 2026-05-21
  - id: keycloak-gateway
    resource: /auth-server/docker-compose.gateway.yml
    title: Keycloak router and proxy configuration
    last_modified: 2026-05-22
---

# Start with discovery

Open the local dashboard at `http://localhost:8081` and run `corepack pnpm gateway:logs`. Treat the dashboard as local-only because it has no authentication.[^gateway-compose]

# Traefik 404

A 404 usually means no router matched. Confirm the hostname, `traefik.enable=true`, `web` entrypoint, public network, and `traefik.docker.network=admin-starter-public`. API host aliases have no implemented router and are expected to 404.[^web-gateway]

# Backend unreachable

Confirm the container is running, shares the public network, listens on `0.0.0.0`, and that `loadbalancer.server.port` is the container's internal port rather than a host port.

# Wrong login host

Confirm gateway Keycloak receives `KEYCLOAK_EXTERNAL_URL`, `KC_PROXY_HEADERS=xforwarded`, and HTTP enabled, then restart the container. Confirm the app callback and post-login variables use `app.localhost`.[^keycloak-gateway]

# Postgres unreachable from host

This is expected in gateway mode: Postgres publishes no host port and is on the internal network. Use container-scoped inspection or the gateway backup scripts.

# Related concepts

- [Gateway routing](/architecture/gateway-routing.md)
- [Gateway network model](/architecture/gateway-network-model.md)
- [Traefik static configuration](/integrations/traefik-static-config.md)

[^gateway-compose]: Traefik discovery and entrypoint configuration

[^web-gateway]: Web router configuration

[^keycloak-gateway]: Keycloak router and proxy configuration

# Related decision records

These proposals record the decision and tradeoffs; this page retains the current behavior or operational procedure.

- [ADR-0011: Separate the local gateway edge from database connectivity (proposed)](/adr/ADR-0011-local-gateway-isolation.md)
