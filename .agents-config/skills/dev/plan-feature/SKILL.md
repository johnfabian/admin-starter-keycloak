---
name: plan-feature
description: Create a dated feature specification with a brief interview and independent critique. Use to start or resume feature planning from a natural-language request.
---

# plan feature

Record the package Git revision in checkpoints; identify uncommitted package changes as provisional.

1. Start at the wiki index, inspect relevant source and rules, and preserve unrelated work. Use a dedicated linked writing worktree and run `corepack pnpm agent:check`.
2. Interview only for material scope, behavior, compatibility, or ownership decisions. Reuse existing answers. Internally use research, requirements, architecture-impact, edge-case and test-strategy procedures where useful; the developer does not invoke each step.
3. Write `specs/features/YYYY-MM-DD-feature-slug.md` using [the specification template](templates/feature-spec.md). Include actors, allowed/denied/failure behavior, non-goals, requirement IDs and objective acceptance evidence. Resolve material decisions.
4. Run `corepack pnpm workflow check-spec <path>`. Request an independent, read-only `critique-feature-spec` agent with the exact file digest and relevant source, not the author's reasoning. If a separate reviewer is unavailable, preserve the draft and report that limitation.
5. Resolve findings and repeat critique after material edits. A spec critique does not approve implementation.
6. Proceed internally to `plan-implementation` when the user requested planning through delivery. Otherwise hand off the critiqued spec. There is one routine human approval at the end of implementation planning; do not insert extra per-specialist approvals.

Legacy `scripts/validate_state.py` and its [stage contract](references/stage-contract.md) read historical 1.x records only. They cannot authorize the v2 flow. Current contracts are validated by repository `scripts/workflow.py`.

For read-only historical recovery only, run `uv run .agents-config/skills/dev/plan-feature/scripts/validate_state.py <legacy-state.json>` from the repository root. New planning uses `corepack pnpm workflow`.
