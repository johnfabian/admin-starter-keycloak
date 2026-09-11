---
name: implement-story
description: Execute one approved implementation story with a verified baseline, characterization-first or TDD ordering, scoped ownership, deterministic evidence, independent review, and durable handoff. Use only when the story packet is ready and human gates are satisfied; never implement on the default branch or self-approve completion.
disable-model-invocation: true
---

# Implement an approved story

Use the full Git commit containing this package as the skill version ID and record it in every artifact. A dirty package is unversioned and cannot satisfy a completed gate.

1. Validate the story packet with [templates/story-packet.md](templates/story-packet.md): scope, criteria, paths, rules, wiki concepts, tests, dependencies, risks, approvals, and verification commands.
2. Confirm a dedicated linked worktree on a feature branch and run agent preflight. The user-approved 2026-09-11 automation plan supersedes the former worktree prohibition. Keep parallel writers disjoint and at most two.
3. Record the pre-change baseline and existing failures. Automated browser characterization may establish the baseline; a human browser session is not a prerequisite.
4. For existing/risky behavior, add characterization tests first. For new behavior, record a failing test before implementation when feasible.
5. Make the smallest scoped change, then record red, green, and refactor evidence separately.
6. Run matching rule checks and the complete story verification set. Do not collapse lint/build/test evidence.
7. Obtain independent review for the declared risk level; the implementer cannot approve its own work.
8. Create a durable handoff before a human gate, ownership change, compaction, or stop.

Use [references/scenarios.md](references/scenarios.md) for control regression checks.
