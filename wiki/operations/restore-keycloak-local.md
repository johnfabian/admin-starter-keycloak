---
type: Runbook
title: Restore Keycloak locally
description: Guarded scripts for replacing only the local Keycloak database from a custom-format dump.
tags: [restore, keycloak, postgres, destructive]
status: draft
generated: { by: codex/gpt-5, at: 2026-08-02T16:44:19Z }
stale_after: 2026-10-02
sources:
  - id: direct-restore
    resource: /scripts/restore-keycloak-local-default.sh
    title: Direct-stack Keycloak restore script
    last_modified: 2026-05-15
  - id: gateway-restore
    resource: /scripts/restore-keycloak-local-traefik.sh
    title: Gateway Keycloak restore script
    last_modified: 2026-05-15
  - id: restore-primitive
    resource: /scripts/backup-lib.sh
    title: Database restore implementation
    last_modified: 2026-05-15
---

# Destructive boundary

This operation drops and recreates the `keycloak` database in one explicit running container. Confirm the stack, container, dump path, and recovery point with the operator before running it. Take a fresh backup first when the current state may be needed.

The scripts require both a positional dump path and the exact confirmation `CONFIRM_RESTORE=keycloak`; otherwise they refuse to run.[^direct-restore][^gateway-restore]

# Direct stack

```bash
CONFIRM_RESTORE=keycloak bash scripts/restore-keycloak-local-default.sh \
  ./backups/postgres/<timestamp>/keycloak.dump
```

Target: container `app-postgres`, database `keycloak`.

# Gateway stack

```bash
CONFIRM_RESTORE=keycloak bash scripts/restore-keycloak-local-traefik.sh \
  ./backups/postgres/<timestamp>/keycloak-traefik.dump
```

Target: container `app-traefik-postgres`, database `keycloak`.

The target Postgres container must already be running. The shared primitive copies the dump into the container, drops and recreates the database, restores it, and removes the temporary file.[^restore-primitive]

# Verify

Restart the matching Keycloak service. Confirm the realm, web client, roles, user login, and `disable-after-email-verify` event-listener registration. Do not treat container health alone as restore evidence.

# Related concepts

- [Local backup](/operations/local-backup.md)
- [Restore the Postgres volume](/operations/restore-postgres-volume.md)
- [Backup and restore drill](/operations/backup-restore-drill.md)

[^direct-restore]: Direct-stack Keycloak restore script

[^gateway-restore]: Gateway Keycloak restore script

[^restore-primitive]: Database restore implementation

# Related decision records

These accepted ADRs record the decisions and tradeoffs; this page retains the current behavior or operational procedure.

- [ADR-0012: Recover local state from database dumps rather than realm exports (accepted)](/adr/ADR-0012-local-database-recovery.md)
