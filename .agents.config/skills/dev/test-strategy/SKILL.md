---
name: test-strategy
description: Design a risk-based, layered test and verification strategy for a feature, refactor, or legacy characterization effort. Use before implementation to map requirements and edge cases to deterministic unit, browser-component, integration, end-to-end, static, configuration, and human evidence without inventing unsupported coverage targets.
---

# Design test strategy

Use the full Git commit containing this package as the skill version ID and record it in every artifact. A dirty package is unversioned and cannot satisfy a completed gate.

1. Accept approved requirements, affected boundaries, edge cases, and current test capability.
2. Establish a pre-change baseline. For risky existing code, require characterization before refactoring.
3. Select the lowest reliable level for each behavior while preserving cross-boundary tests for contracts and journeys.
4. Cover positive and negative authentication, authorization, session, ownership, malformed input, dependency failure, and destructive-action guards when relevant.
5. Define deterministic fixtures, production-data exclusions, service prerequisites, cleanup, and evidence paths.
6. Use a risk-based coverage ratchet. Do not invent a global percentage without human policy.
7. Separate fast PR checks from slower integration/E2E gates and define a successful not-applicable result.
8. Render [templates/test-strategy.md](templates/test-strategy.md).

Use [references/scenarios.md](references/scenarios.md) for skill-level checks.
