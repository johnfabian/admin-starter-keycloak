---
type: Runbook
title: Backup and restore drill
description: Manual evidence loop for proving a local database backup can restore identity and application access.
tags: [backup, restore, testing, keycloak]
status: draft
generated: { by: codex/gpt-5, at: 2026-08-02T16:44:19Z }
stale_after: 2026-10-02
sources:
  - id: backup-entrypoint
    resource: /backup-all
    title: Local backup entrypoint
    last_modified: 2026-05-15
  - id: direct-volume
    resource: /postgres/docker-compose.yml
    title: Direct Postgres volume
    last_modified: 2026-05-21
  - id: gateway-volume
    resource: /postgres/docker-compose.gateway.yml
    title: Gateway Postgres volume
    last_modified: 2026-05-21
---

# Drill

Use a disposable local stack or the local mode whose volume the operator explicitly authorizes for destruction. Never run the drill against an ambiguous or shared target.

1. Record the mode, branch, exact container and named volume, and authorized recovery point.
2. Create a disposable role-bearing user and prove it can reach a guarded route.
3. Run `./backup-all` and identify that stack's exact dump files.[^backup-entrypoint]
4. Obtain explicit destructive-action confirmation for the named direct or gateway volume.[^direct-volume][^gateway-volume]
5. Follow [Restore the Postgres volume](/operations/restore-postgres-volume.md).
6. Sign in as the same disposable user and reach the same guarded route.
7. Confirm the `admin-starter-web` client, `Users` and `Admins` roles, and registration event listener are present.
8. Record the backup timestamp, restore target, commands, outcome, and any gap without recording secrets or tokens.

A dump file existing is not recovery evidence. The successful post-restore identity flow and guarded route are the material checks.

# Related concepts

- [Local backup](/operations/local-backup.md)
- [Create an admin user](/operations/create-admin-user.md)
- [Known production gaps](/architecture/known-production-gaps.md)

[^backup-entrypoint]: Local backup entrypoint

[^direct-volume]: Direct Postgres volume

[^gateway-volume]: Gateway Postgres volume

# Related decision records

These accepted ADRs record the decisions and tradeoffs; this page retains the current behavior or operational procedure.

- [ADR-0012: Recover local state from database dumps rather than realm exports (accepted)](/adr/ADR-0012-local-database-recovery.md)
