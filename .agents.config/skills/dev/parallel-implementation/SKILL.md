---
name: parallel-implementation
description: Prepare a bounded ownership, branch, isolation, merge-order, and integration-evidence plan for disjoint implementation slices. Use only when parallel writing is proposed; respect repository policy that currently prohibits worktrees and render a blocked or serial plan unless a human explicitly changes that policy.
---

# Plan implementation ownership

Use the full Git commit containing this package as the skill version ID and record it in every artifact. A dirty package is unversioned and cannot satisfy a completed gate.

1. Verify the approved story packets, common base revision, shared contracts, and integration owner.
2. Load repository branch/isolation policy. Repository-specific human direction dated 2026-08-02 prohibits worktrees and supersedes generic worktree language in the draft PRD; do not create one or authorize concurrent writers unless a later attributable human record changes the policy.
3. When parallel writing is prohibited, render a serial ownership plan and mark the parallel gate blocked/not applicable.
4. If policy is explicitly changed later, limit writers to two, require separate branches and isolated checkouts, and assign non-overlapping path budgets.
5. Keep lockfiles, migrations, shared/generated artifacts, CI, Keycloak/Traefik, deployment, and release state single-owner.
6. Require each worker's evidence/handoff and one integration owner to verify the combined revision.
7. Render [templates/coordination.md](templates/coordination.md). Do not create branches or mutate GitHub without separate authority.

Use [references/scenarios.md](references/scenarios.md) for ownership-conflict checks.
