---
type: Architecture
title: Known production gaps
description: Evidence-backed gaps between the current local starter and a production deployment.
tags: [production, security, operations, gaps]
status: draft
generated: { by: codex/gpt-5, at: 2026-08-02T16:44:19Z }
stale_after: 2026-10-02
sources:
  - id: security-headers
    resource: /web/app/lib/security-headers.shared.ts
    title: Web security headers
    last_modified: 2026-08-01
  - id: gateway-compose
    resource: /api-gateway/docker-compose.yml
    title: Local Traefik configuration
    last_modified: 2026-05-15
  - id: app-schema
    resource: /postgres/init-app-schema.sql
    title: First-boot application schema
    last_modified: 2026-05-21
  - id: root-scripts
    resource: /package.json
    title: Repository verification scripts
    last_modified: 2026-08-01
---

# Current gaps

- Production CSP emits `script-src 'self'` while the source comments state that React Router inline scripts require a per-request nonce that is not implemented. A production image therefore needs browser verification before it can be considered deployable.[^security-headers]
- The Traefik stack is local HTTP, exposes `api.insecure=true`, and mounts the Docker socket read-only. There is no TLS, certificate automation, dashboard authentication, or declared trusted-proxy source policy.[^gateway-compose]
- `init-app-schema.sql` runs only when an empty Postgres volume is initialized. There is no migration framework for an existing database.[^app-schema]
- The web container has no health check, and the repository has no implemented metrics, tracing, alerting, scheduled backup, offsite retention, or production restore procedure.
- `WEB_KEYCLOAK_API_AUDIENCE` is empty in the examples. Explicit resource-audience validation must be designed with the eventual resource API and matching Keycloak mapper.
- The repository has no test suite or CI workflow; the static gate formats, lints, and type-checks without exercising a browser or live identity flow.[^root-scripts]

These are observations, not an approved deployment design. Provider, TLS, secret, persistence, observability, and recovery choices still require human decisions.

# Related concepts

- [Build the app image](/operations/build-app-image.md)
- [Backup and restore drill](/operations/backup-restore-drill.md)
- [Verification baseline](/testing/verification-baseline.md)

[^security-headers]: Web security headers

[^gateway-compose]: Local Traefik configuration

[^app-schema]: First-boot application schema

[^root-scripts]: Repository verification scripts
