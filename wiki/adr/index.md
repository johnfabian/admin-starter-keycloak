# Architecture decision records

ADR-0001 through ADR-0012 were accepted by the requesting user on 2026-09-11. [Approval recorded in PR #20](https://github.com/johnfabian/admin-starter-keycloak/pull/20#adr-acceptance---2026-09-11) identifies the exact reviewed revision and outcomes. Preserve superseded records and immutable ADR identifiers.

- [ADR-0001: Worktree isolation (accepted)](ADR-0001-worktree-isolation.md)
- [ADR-0002: Graph/wiki ownership (accepted)](ADR-0002-graph-and-wiki-ownership.md)
- [ADR-0003: Shared-realm testing (accepted)](ADR-0003-shared-realm-testing.md)

## Reconciled architectural decisions

The 2026-09-11 wiki review identified the following decisions in existing architecture, integration, convention, and runbook pages. Their guides remain in place and link here. Historical alternatives and approvals are not inferred from implementation.

- [ADR-0004: Use three developer flows with one routine approval (accepted)](ADR-0004-three-flow-development.md)
- [ADR-0005: Keep browser authentication and token custody in the BFF (accepted)](ADR-0005-bff-session-and-token-boundary.md)
- [ADR-0006: Enforce routes server-side using the current role contract (accepted)](ADR-0006-server-side-role-authorization.md)
- [ADR-0007: Require administrator approval after self-registration verification (accepted)](ADR-0007-registration-approval.md)
- [ADR-0008: Use realm-local credentials for routine application administration (accepted)](ADR-0008-realm-scoped-automation-administration.md)
- [ADR-0009: Keep canonical agent procedures portable across harnesses (accepted)](ADR-0009-portable-agent-tooling.md)
- [ADR-0010: Gate dependency adoption with explicit trust controls (accepted)](ADR-0010-dependency-trust-controls.md)
- [ADR-0011: Separate the local gateway edge from database connectivity (accepted)](ADR-0011-local-gateway-isolation.md)
- [ADR-0012: Recover local state from database dumps rather than realm exports (accepted)](ADR-0012-local-database-recovery.md)

## What remains outside ADRs

Exact URLs, ports, versions, console settings, schema columns, commands, troubleshooting, and test instructions remain in their current guides. Password and token-lifetime suggestions, the Express placeholder and production gaps are not accepted architectural decisions. ORCA is deferred for now and is not a delivery prerequisite. Future changes in those areas require scoped design or verification before a new ADR can claim an accepted outcome.

A runbook explains how; an ADR records the choice, alternatives, consequences, and approval. Link the two instead of moving or duplicating complete guides.
