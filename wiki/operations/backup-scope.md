---
type: Runbook
title: Backup scope
description: Current local state locations and what the implemented backup scripts protect.
tags: [backup, postgres, keycloak, state]
status: draft
generated: { by: codex/gpt-5, at: 2026-08-02T16:44:19Z }
stale_after: 2026-10-02
sources:
  - id: backup-script
    resource: /scripts/backup-lib.sh
    title: Database backup implementation
    last_modified: 2026-05-15
  - id: direct-postgres
    resource: /postgres/docker-compose.yml
    title: Direct database volume
    last_modified: 2026-05-21
  - id: gateway-postgres
    resource: /postgres/docker-compose.gateway.yml
    title: Gateway database volume
    last_modified: 2026-05-21
---

# Stateful assets

Both local stacks keep the Keycloak database and application database in one Postgres volume. Direct mode uses `admin-starter-keycloak_postgres_data`; gateway mode uses `admin-starter-postgres-traefik-data`.[^direct-postgres][^gateway-postgres]

The implemented backup scripts dump the `keycloak` database, the database named by `POSTGRES_DB`, and a `pg_dumpall` snapshot for each running local stack.[^backup-script] Environment secrets are separate, gitignored state and are not included. Mailpit has its own local volume and is not included in `backup-all`.

# What is not a backup

Containers and images are rebuildable artifacts. `init-app-schema.sql` is first-boot schema, not data. A realm export is useful for configuration review but is not the repository's recovery mechanism.

# Production gap

No scheduled backup, encryption policy, offsite copy, retention, integrity monitor, provider integration, or production restore exists. Those require human ownership before deployment.

# Related concepts

- [Realm export versus backup](/architecture/realm-export-vs-backup.md)
- [Local backup](/operations/local-backup.md)
- [Known production gaps](/architecture/known-production-gaps.md)

[^backup-script]: Database backup implementation

[^direct-postgres]: Direct database volume

[^gateway-postgres]: Gateway database volume

# Related decision records

These accepted ADRs record the decisions and tradeoffs; this page retains the current behavior or operational procedure.

- [ADR-0012: Recover local state from database dumps rather than realm exports (accepted)](/adr/ADR-0012-local-database-recovery.md)
