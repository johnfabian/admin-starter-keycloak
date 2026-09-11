---
type: Integration
title: Traefik static configuration
description: Exact local Traefik version, flags, ports, and Docker provider controls.
resource: /api-gateway/docker-compose.yml
tags: [traefik, gateway, docker, configuration]
status: draft
generated: { by: codex/gpt-5, at: 2026-08-02T16:44:19Z }
stale_after: 2026-10-02
sources:
  - id: gateway-compose
    resource: /api-gateway/docker-compose.yml
    title: Traefik Compose configuration
    last_modified: 2026-05-15
---

# Implemented static settings

The local gateway pins `traefik:v3.2` and supplies static configuration as command arguments:[^gateway-compose]

```text
--api.dashboard=true
--api.insecure=true
--entrypoints.web.address=:80
--providers.docker=true
--providers.docker.exposedbydefault=false
```

Host port 80 carries the `web` entrypoint. Host port 8081 maps to the unauthenticated dashboard. Docker discovery uses a read-only `/var/run/docker.sock` mount. Dynamic routers and services live in labels on the web and Keycloak Compose services.

# Change boundary

Confirm any new flag against Traefik v3.2 or deliberately update the image pin. Preserve `exposedByDefault=false`. Treat the insecure dashboard, HTTP-only entrypoint, and Docker socket as local controls that require a separate production design.

# Related concepts

- [Gateway routing](/architecture/gateway-routing.md)
- [Gateway network model](/architecture/gateway-network-model.md)
- [Known production gaps](/architecture/known-production-gaps.md)

[^gateway-compose]: Traefik Compose configuration

# Related decision records

These proposals record the decision and tradeoffs; this page retains the current behavior or operational procedure.

- [ADR-0011: Separate the local gateway edge from database connectivity (proposed)](/adr/ADR-0011-local-gateway-isolation.md)
