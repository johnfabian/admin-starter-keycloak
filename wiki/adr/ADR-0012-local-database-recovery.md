---
type: Decision
title: "ADR-0012: Recover local state from database dumps rather than realm exports"
description: Accepted architectural decision with attributable conversation approval recorded in PR 20.
tags: [adr, architecture]
adr_id: ADR-0012
decision_status: accepted
decided_on: 2026-09-11
approved_by: "human:requesting-user"
status: stable
generated: { by: "codex/gpt-6", at: "2026-09-11T20:32:36Z" }
stale_after: 2026-12-11
verified: { by: human:requesting-user, at: "2026-09-11T21:27:10.569994+00:00" }
sources:
  - id: acceptance
    resource: https://github.com/johnfabian/admin-starter-keycloak/pull/20#adr-acceptance---2026-09-11
    title: Conversation approval of the exact ADR set recorded in PR 20
    author: "human:requesting-user"
    last_modified: 2026-09-11
  - id: source-1
    resource: /scripts/backup-lib.sh
    title: "scripts/backup-lib.sh"
    last_modified: 2026-05-15
  - id: source-2
    resource: /scripts/restore-keycloak-local-default.sh
    title: "scripts/restore-keycloak-local-default.sh"
    last_modified: 2026-05-15
  - id: source-3
    resource: /scripts/restore-keycloak-local-traefik.sh
    title: "scripts/restore-keycloak-local-traefik.sh"
    last_modified: 2026-05-15
---

# Context

Local Keycloak and application database state must survive container rebuilds and be recoverable after a failed change.

# Decision

Record the implemented local recovery approach: Postgres database dumps and restore tools, with exact named targets and destructive-operation confirmation. A Keycloak realm export is a configuration/migration artifact, not a substitute for the implemented database recovery process. Keep dumps and matching secrets out of Git.

# Alternatives for review

Realm-export-only recovery, volume snapshots, or managed point-in-time recovery are comparison options. Original rationale and a production recovery choice are not established.

# Consequences and limits

Restore evidence requires a successful recovery exercise; a dump file alone is insufficient. The current backup scope excludes Mailpit and separately managed environment secrets. Shared Postgres volumes couple local blast radius. Scheduling, offsite retention, backup encryption and recovery objectives remain production gaps, not approved policy.

# Approval provenance

Accepted on 2026-09-11 by the requesting human user in the Codex conversation (human:requesting-user). The user said: "lets not worrry about orca right now, but the ADRs look good to me".

The approval covers ADR-0001 through ADR-0012 as presented at commit 04e3abe09195516104180fb4f10ba23394cd1f04. It was transcribed into [PR #20](https://github.com/johnfabian/admin-starter-keycloak/pull/20#adr-acceptance---2026-09-11) and exactly reread before acceptance. This is conversation approval recorded by the assistant, not a GitHub review submitted by the human. No GitHub identity is inferred.

Acceptance confirms the architectural choice; it does not claim historical approval, independent runtime verification, production readiness, deployment or PR merge authorization. ORCA is deferred and does not block the accepted workflow.

The previous proposed record remains available at the approved Git revision. Record-ADR skill version: 04e3abe09195516104180fb4f10ba23394cd1f04.

# Evidence and related guidance

Source revision inspected: 342ec668b7848fe0200a9c317812831ca546b885. Draft documents are evidence of design intent, not implemented behavior.

- [architecture/realm-export-vs-backup.md](/architecture/realm-export-vs-backup.md)
- [operations/backup-scope.md](/operations/backup-scope.md)
- [operations/local-backup.md](/operations/local-backup.md)
- [operations/backup-restore-drill.md](/operations/backup-restore-drill.md)
- [operations/restore-keycloak-local.md](/operations/restore-keycloak-local.md)
- [operations/restore-postgres-volume.md](/operations/restore-postgres-volume.md)

# Supersession

No prior ADR is superseded. Existing records keep their identifiers.
