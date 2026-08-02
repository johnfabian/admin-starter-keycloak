---
name: react-pattern-review
description: Perform a clean-context, read-only React and React Router pattern review that separates proven defects from maintainability opportunities and specifies characterization coverage before refactoring. Use when assessing existing UI/BFF code, planning React stabilization, or independently reviewing React changes.
---

# Review React patterns

Use the full Git commit containing this package as the skill version ID and record it in every artifact. A dirty package is unversioned and cannot satisfy a completed gate.

Run from a clean, read-only reviewer context when the result is an independent gate. Do not edit code or approve your own findings.

1. Load only React-scoped rules and relevant wiki concepts; verify them against the current revision.
2. Inspect route/module boundaries, server/client separation, data loading/actions, component responsibility, effects/state, accessibility, error behavior, duplicated wrappers, performance, and test seams.
3. Separate reproducible defects from maintainability suggestions.
4. Record severity, exact path/line evidence, observable risk, recommended pattern, characterization coverage required first, and disposition.
5. Do not refactor until required characterization tests pass. Critical/high findings block stability unless fixed or attributable human risk acceptance is recorded.
6. Render [templates/react-review.md](templates/react-review.md).

Use [references/scenarios.md](references/scenarios.md) to forward-test this skill.
