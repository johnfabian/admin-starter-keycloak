---
name: critique-plan
description: Independently challenge a feature or delivery plan from clean, read-only context for missing scope, weak evidence, horizontal stories, unresolved dependencies, test gaps, unsafe assumptions, and approval failures. Use before feature approval or after material plan changes; the critic must not implement or approve the plan.
---

# Critique a plan independently

Use the full Git commit containing this package as the skill version ID and record it in every artifact. A dirty package is unversioned and cannot satisfy a completed gate.

Use a clean reviewer context when available. Give it approved requirements, evidence links, relevant rules/wiki concepts, architecture impact, edge cases, story previews, and test strategy—not private reasoning.

1. Verify cited evidence and detect missing or stale inputs.
2. Trace each requirement and edge case to a story and acceptance/test evidence.
3. Challenge scope, verticality, compatibility, authorization, operations, rollback, dependencies, ownership, and human gates.
4. Record findings as critical/high/medium/low with exact evidence, impact, remediation, and disposition owner.
5. Block approval for unresolved critical findings. The critic cannot accept risk or approve its own recommendation.
6. Render [templates/critique.md](templates/critique.md).

Use [references/scenarios.md](references/scenarios.md) for independent forward tests.
