---
type: Architecture
title: Gateway routing
description: Implemented host-based routing for the local Traefik stack.
resource: /api-gateway/docker-compose.yml
tags: [traefik, docker, gateway, routing]
status: draft
generated: { by: codex/gpt-5, at: 2026-08-02T16:44:19Z }
stale_after: 2026-11-02
sources:
  - id: gateway-compose
    resource: /api-gateway/docker-compose.yml
    title: Traefik Compose configuration
    last_modified: 2026-05-15
  - id: web-gateway
    resource: /web/docker-compose.gateway.yml
    title: Web gateway Compose configuration
    last_modified: 2026-05-21
  - id: keycloak-gateway
    resource: /auth-server/docker-compose.gateway.yml
    title: Keycloak gateway Compose configuration
    last_modified: 2026-05-22
---

# Current routing

Gateway mode routes local browser traffic by hostname through Traefik on port 80. `app.localhost` reaches the React Router container on port 3000, and `auth.localhost` reaches Keycloak on port 8080.[^web-gateway][^keycloak-gateway]

Docker discovery is enabled with `exposedByDefault=false`, so a container is routable only when its labels opt in, declare a host rule and entrypoint, and name the internal service port. The configured API host aliases do not create routers; no API container is implemented.[^gateway-compose]

# Local-only boundary

The gateway has one HTTP entrypoint and an insecure dashboard at `http://localhost:8081`. It has no TLS, certificate resolver, or production middleware and must not be described as a production edge.

# Related concepts

- [Gateway network model](/architecture/gateway-network-model.md)
- [Traefik static configuration](/integrations/traefik-static-config.md)
- [Troubleshoot the gateway](/operations/troubleshoot-gateway.md)

[^gateway-compose]: Traefik Compose configuration

[^web-gateway]: Web gateway Compose configuration

[^keycloak-gateway]: Keycloak gateway Compose configuration
