---
type: Runbook
title: Local backup
description: Implemented command and outputs for backing up either running local Postgres stack.
tags: [backup, postgres, docker, local-development]
status: draft
generated: { by: codex/gpt-5, at: 2026-08-02T16:44:19Z }
stale_after: 2026-10-02
sources:
  - id: entrypoint
    resource: /backup-all
    title: Root backup entrypoint
    last_modified: 2026-05-15
  - id: orchestration
    resource: /scripts/backup-all.sh
    title: Local backup orchestration
    last_modified: 2026-05-15
  - id: primitives
    resource: /scripts/backup-lib.sh
    title: Postgres dump implementation
    last_modified: 2026-05-15
---

# Run

From a Bash-compatible shell at the repository root:

```bash
./backup-all
```

The command checks the direct and gateway Postgres containers, skips a stack that is absent or stopped, and writes the running stacks' dumps beneath `backups/postgres/<UTC timestamp>/`.[^entrypoint][^orchestration] Direct files have no suffix; gateway files use `-traefik`.

Each running stack produces a Keycloak custom-format dump, an application-database custom-format dump, and an all-databases SQL dump. The scripts source the matching gitignored environment file to obtain `POSTGRES_USER` and `POSTGRES_DB`.[^primitives]

# Verify

Confirm the output directory contains the expected stack-specific files, keep them out of Git, handle them as sensitive state, and complete a restore drill before calling them recoverable. A successful dump command alone is not restore evidence.

# Related concepts

- [Backup scope](/operations/backup-scope.md)
- [Restore Keycloak locally](/operations/restore-keycloak-local.md)
- [Backup and restore drill](/operations/backup-restore-drill.md)

[^entrypoint]: Root backup entrypoint

[^orchestration]: Local backup orchestration

[^primitives]: Postgres dump implementation
