---
type: Runbook
title: Local stack
description: Supported direct and gateway startup modes, services, ports, and shutdown commands.
tags: [local-development, docker, pnpm, services]
status: draft
generated: { by: codex/gpt-5, at: 2026-08-02T16:44:19Z }
stale_after: 2026-10-02
sources:
  - id: root-scripts
    resource: /package.json
    title: Repository lifecycle scripts
    last_modified: 2026-08-01
  - id: direct-postgres
    resource: /postgres/docker-compose.yml
    title: Direct Postgres service
    last_modified: 2026-05-21
  - id: direct-keycloak
    resource: /auth-server/docker-compose.yml
    title: Direct Keycloak service
    last_modified: 2026-05-22
---

# Direct mode

Copy `.env.example` to `.env.development`, replace empty/placeholder secrets, then start dependencies before the web development server:

```bash
corepack pnpm mail:up
corepack pnpm db:up
corepack pnpm auth:up
corepack pnpm dev
```

The default endpoints are Mailpit `http://localhost:8025`, Postgres `localhost:5434`, Keycloak `http://localhost:8080`, and the app `http://localhost:5173`.[^direct-postgres][^direct-keycloak]

`corepack pnpm stop-app` stops Keycloak and Postgres. Stop Mailpit separately with `corepack pnpm mail:down`.[^root-scripts]

# Gateway mode

Copy `.env.traefik.example` to `.env.traefik`, replace placeholders, then use:

```bash
corepack pnpm dev:gateway
corepack pnpm dev:gateway:down
```

Gateway startup builds and starts Mailpit, Traefik, Postgres, Keycloak, and web in dependency order. Use `http://app.localhost`, `http://auth.localhost`, and `http://localhost:8081`.

# Boundaries

Use one mode at a time. Root web commands load `.env.development`; direct `pnpm --dir web dev` does not. Named volumes survive ordinary `down` commands. No command here establishes production readiness.

# Related concepts

- [Environment variables](/operations/environment-variables.md)
- [Gateway routing](/architecture/gateway-routing.md)
- [Local backup](/operations/local-backup.md)

[^root-scripts]: Repository lifecycle scripts

[^direct-postgres]: Direct Postgres service

[^direct-keycloak]: Direct Keycloak service

# Related decision records

These accepted ADRs record the decisions and tradeoffs; this page retains the current behavior or operational procedure.

- [ADR-0011: Separate the local gateway edge from database connectivity (accepted)](/adr/ADR-0011-local-gateway-isolation.md)
