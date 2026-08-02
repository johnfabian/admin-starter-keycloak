---
name: find-edge-cases
description: Identify material edge and abuse cases tied to approved requirements and affected boundaries, then assign each an acceptance, story, test, operational control, or accepted-risk disposition. Use before story decomposition or when negative behavior, concurrency, dependency failure, authorization, or configuration drift needs explicit treatment.
---

# Find and dispose edge cases

Use the full Git commit containing this package as the skill version ID and record it in every artifact. A dirty package is unversioned and cannot satisfy a completed gate.

1. Accept stable requirement IDs and architecture boundaries.
2. Examine identity, authorization, ownership, malformed/duplicate/stale/concurrent data, browser behavior, dependency failure, configuration drift, observability, rollback, and abuse.
3. Keep only cases with a plausible precondition and observable impact.
4. Link every case to at least one requirement or boundary.
5. Assign exactly one primary disposition: acceptance criterion, story, test, operational control, or human-accepted risk.
6. Treat unresolved critical/high cases as blockers; an agent cannot accept risk.
7. Render [templates/edge-cases.md](templates/edge-cases.md).

Use [references/scenarios.md](references/scenarios.md) for regression checks.
