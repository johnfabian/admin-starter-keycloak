---
type: Runbook
title: Restore the Postgres volume
description: Manual full-volume recovery outline for both local Postgres stacks.
tags: [restore, postgres, docker, destructive]
status: draft
generated: { by: codex/gpt-5, at: 2026-08-02T16:44:19Z }
stale_after: 2026-10-02
sources:
  - id: direct-compose
    resource: /postgres/docker-compose.yml
    title: Direct Postgres volume and initialization
    last_modified: 2026-05-21
  - id: gateway-compose
    resource: /postgres/docker-compose.gateway.yml
    title: Gateway Postgres volume and initialization
    last_modified: 2026-05-21
  - id: backup-format
    resource: /scripts/backup-lib.sh
    title: Backup file format and restore primitives
    last_modified: 2026-05-15
---

# Scope and confirmation

This is a manual, destructive recovery: removing the selected volume destroys both the Keycloak and application databases for that stack. Prefer the targeted Keycloak restore when only the realm database is damaged.

Before any `down -v`, record and obtain explicit confirmation for exactly one target:

| Mode    | Postgres compose                      | Keycloak compose                         | Container              | Named volume                           | Environment file   |
| ------- | ------------------------------------- | ---------------------------------------- | ---------------------- | -------------------------------------- | ------------------ |
| Direct  | `postgres/docker-compose.yml`         | `auth-server/docker-compose.yml`         | `app-postgres`         | `admin-starter-keycloak_postgres_data` | `.env.development` |
| Gateway | `postgres/docker-compose.gateway.yml` | `auth-server/docker-compose.gateway.yml` | `app-traefik-postgres` | `admin-starter-postgres-traefik-data`  | `.env.traefik`     |

# Recovery outline

1. Verify the chosen backup directory contains the matching `keycloak` and application dumps; gateway filenames carry `-traefik`.
2. Stop the matching Keycloak stack.
3. Stop the matching Postgres Compose project with `down -v` only after reconfirming the named volume above.
4. Start that Postgres Compose project empty. Its init SQL recreates the `keycloak` database and `web_bff_sessions` schema.[^direct-compose][^gateway-compose]
5. Restore `keycloak` and the database named by `POSTGRES_DB` using the environment's `POSTGRES_USER`, not an assumed `postgres` role. The checked-in helper shows the required `dropdb`, `createdb`, and `pg_restore --clean --if-exists` sequence.[^backup-format]
6. Restart the matching services and verify login, roles, client configuration, event-listener registration, and a guarded application route.

# Safety

Do not generalize this runbook to a production provider. Do not expose environment values in command history or handoffs. Preserve the pre-restore dump until verification succeeds.

# Related concepts

- [Backup scope](/operations/backup-scope.md)
- [Restore Keycloak locally](/operations/restore-keycloak-local.md)
- [Backup and restore drill](/operations/backup-restore-drill.md)

[^direct-compose]: Direct Postgres volume and initialization

[^gateway-compose]: Gateway Postgres volume and initialization

[^backup-format]: Backup file format and restore primitives

# Related decision records

These accepted ADRs record the decisions and tradeoffs; this page retains the current behavior or operational procedure.

- [ADR-0012: Recover local state from database dumps rather than realm exports (accepted)](/adr/ADR-0012-local-database-recovery.md)
