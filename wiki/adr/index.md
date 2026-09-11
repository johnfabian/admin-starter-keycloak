# Architecture decision records

No accepted ADRs are recorded yet. Draft proposals have explicit pending approval. Accepted records require attributable approval evidence. Preserve superseded records and immutable ADR identifiers.

- [ADR-0001: Worktree isolation (proposed)](ADR-0001-worktree-isolation.md)
- [ADR-0002: Graph/wiki ownership (proposed)](ADR-0002-graph-and-wiki-ownership.md)
- [ADR-0003: Shared-realm testing (proposed)](ADR-0003-shared-realm-testing.md)

## Reconciled decision proposals

The 2026-09-11 wiki review identified the following decisions in existing architecture, integration, convention, and runbook pages. Their guides remain in place and link here. Historical alternatives and approvals are not inferred from implementation.

- [ADR-0004: Use three developer flows with one routine approval (proposed)](ADR-0004-three-flow-development.md)
- [ADR-0005: Keep browser authentication and token custody in the BFF (proposed)](ADR-0005-bff-session-and-token-boundary.md)
- [ADR-0006: Enforce routes server-side using the current role contract (proposed)](ADR-0006-server-side-role-authorization.md)
- [ADR-0007: Require administrator approval after self-registration verification (proposed)](ADR-0007-registration-approval.md)
- [ADR-0008: Use realm-local credentials for routine application administration (proposed)](ADR-0008-realm-scoped-automation-administration.md)
- [ADR-0009: Keep canonical agent procedures portable across harnesses (proposed)](ADR-0009-portable-agent-tooling.md)
- [ADR-0010: Gate dependency adoption with explicit trust controls (proposed)](ADR-0010-dependency-trust-controls.md)
- [ADR-0011: Separate the local gateway edge from database connectivity (proposed)](ADR-0011-local-gateway-isolation.md)
- [ADR-0012: Recover local state from database dumps rather than realm exports (proposed)](ADR-0012-local-database-recovery.md)

## What remains outside ADRs

Exact URLs, ports, versions, console settings, schema columns, commands, troubleshooting, and test instructions remain in their current guides. Password and token-lifetime suggestions, the Express placeholder, production gaps, and ORCA compatibility are not accepted architectural decisions. They require scoped design or verification before an ADR can claim an accepted outcome.

A runbook explains how; an ADR records the choice, alternatives, consequences, and approval. Link the two instead of moving or duplicating complete guides.
