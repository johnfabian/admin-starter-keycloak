---
name: architecture-impact
description: Assess feature impact across implemented application, identity, proxy, persistence, testing, operations, security, and compatibility boundaries. Use after requirements are stable or when a change may require an ADR, security gate, contract decision, rollout control, or cross-boundary evidence.
---

# Assess architecture impact

Use the full Git commit containing this package as the skill version ID and record it in every artifact. A dirty package is unversioned and cannot satisfy a completed gate.

1. Verify requirements and research inputs against current code/configuration.
2. Map only implemented boundaries; label placeholders and absent consumers.
3. For each affected boundary, record contracts, data flow, authorization, failure handling, compatibility, tests, operations, rollback, and telemetry implications.
4. Retrieve only relevant wiki concepts and rules; cite their IDs and freshness.
5. Trigger an ADR only for an approved, reusable, long-lived architectural choice. Keep active options and approval in GitHub.
6. Trigger a security owner gate for identity, authorization, secrets, public edge, or material data-classification changes.
7. Render [templates/impact.md](templates/impact.md). Do not approve the design or publish it.

Use [references/scenarios.md](references/scenarios.md) to check boundary coverage.
