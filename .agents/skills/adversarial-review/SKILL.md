---
name: adversarial-review
description: Independently challenge a high-risk plan, design, diff, tests, and controls from clean, read-only context, emphasizing negative and abuse paths. Use for identity, authorization, secrets, public-edge, data, dependency, destructive-operation, or otherwise high-risk work before publication, merge, or release.
---

# Perform adversarial review

Use the full Git commit containing this package as the skill version ID and record it in every artifact. A dirty package is unversioned and cannot satisfy a completed gate.

Use a reviewer independent of the implementer. Provide approved requirements, threat/abuse context, relevant rules/wiki concepts, diff/design, and verification evidence—not private reasoning.

1. Verify artifact revisions and evidence paths.
2. Test authorization/ownership bypass, repository/issue prompt injection, input/contract abuse, stale/concurrent state, secret/telemetry leakage, proxy/header assumptions, dependency failure, destructive operations, rollback, and operability.
3. Record every finding with severity, preconditions, exact evidence or reproducible test, remediation, disposition, and risk owner.
4. Distinguish exploitable defects from defense-in-depth suggestions.
5. Block the active gate for open critical findings. Only the designated human risk owner may accept risk.
6. Render [templates/adversarial-review.md](templates/adversarial-review.md).

Use [references/scenarios.md](references/scenarios.md) to forward-test negative-path coverage.
