---
type: Architecture
title: Realm export versus backup
description: Durable distinction between reviewable Keycloak configuration and recoverable database state.
tags: [keycloak, backup, recovery, configuration]
status: draft
generated: { by: codex/gpt-5, at: 2026-08-02T16:44:19Z }
stale_after: 2026-11-02
sources:
  - id: backup-scripts
    resource: /scripts/backup-lib.sh
    title: Postgres backup and restore primitives
    last_modified: 2026-05-15
  - id: keycloak-compose
    resource: /auth-server/docker-compose.yml
    title: Keycloak database configuration
    last_modified: 2026-05-22
---

# Distinction

In this repository, recovery is based on Postgres dumps of the `keycloak` database. The backup scripts use `pg_dump`, and the restore scripts drop, recreate, and `pg_restore` that database.[^backup-scripts]

A realm export is useful as a reviewable configuration snapshot or migration input, but it is not the recovery mechanism implemented here. No realm export/import artifact, startup import, or Terraform configuration exists in the current worktree. Do not claim that an export can replace the database dump or that a console setting is reproducible from code.

# Handling

Review exports for sensitive values before storing or committing them. Keep recovery dumps out of Git, protect the matching environment secrets separately, and prove backups with a restore drill.

# Related concepts

- [Backup scope](/operations/backup-scope.md)
- [Local backup](/operations/local-backup.md)
- [Restore Keycloak locally](/operations/restore-keycloak-local.md)

[^backup-scripts]: Postgres backup and restore primitives

[^keycloak-compose]: Keycloak database configuration

# Related decision records

These accepted ADRs record the decisions and tradeoffs; this page retains the current behavior or operational procedure.

- [ADR-0012: Recover local state from database dumps rather than realm exports (accepted)](/adr/ADR-0012-local-database-recovery.md)
