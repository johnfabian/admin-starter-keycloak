---
name: adversarial-review
description: Independently challenge a plan, design, diff, tests, and controls from clean, read-only context, emphasizing negative and abuse paths. Use for high-risk work or independent delivery review requested by an authorized feature coordinator.
---

# Perform adversarial review

Record the package Git revision in review evidence; identify uncommitted package changes as provisional.

The authorized coordinator may invoke this specialist through actual native harness delegation without a separate developer invocation. The reviewer must be a separate agent or human who did not implement the reviewed changes. Final integration review excludes every contributing writer and the actual editing coordinator. A JSON reviewer identity or a second role label in the same implementation context is not independent review.

Provide the approved specification and plan, relevant threat/abuse context, scoped rules/wiki concepts, the exact diff/design revision, and verification evidence. Do not provide the implementer's private reasoning or tell the reviewer the intended verdict.

1. Verify the reviewed revision, artifact/evidence digests, reviewer identity, and feature-level round. Changed code or evidence invalidates the affected review.
2. Examine material authorization/ownership bypass, repository/issue prompt injection, input/contract abuse, stale/concurrent state, secret/telemetry leakage, proxy assumptions, dependency failure, destructive operations, rollback, and operability. Scale the review to the actual change.
3. Record each finding with severity, preconditions, exact evidence or a reproducible test, remediation, disposition, and risk owner. Distinguish demonstrated defects from optional hardening suggestions.
4. Block integration or publication for open critical or high findings or failed required checks. No agent may convert an unresolved blocking finding into accepted risk. Any material human decision must be attributable and reflected in the approved scope; it does not make a failed check pass.
5. For feature delivery, use the coordinator's single budget of at most five review rounds, including all stories and final integration. Preserve failed results. Review each subject at most once per round, apart from an identical evidence retry; a new attempt advances the shared round. Exhaustion with unresolved findings means stop and report the blocker.
6. Render [templates/adversarial-review.md](templates/adversarial-review.md) and return evidence to the coordinator. Remain read-only; the authorized writer performs fixes, reruns affected checks, and requests review of the resulting revision.

Use [references/scenarios.md](references/scenarios.md) to forward-test negative-path coverage.
