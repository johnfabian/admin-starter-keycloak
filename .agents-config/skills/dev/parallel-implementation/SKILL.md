---
name: parallel-implementation
description: Prepare a bounded ownership, branch, isolation, merge-order, and integration-evidence plan for disjoint implementation slices. Use only when parallel writing is proposed; require one linked worktree per writer, disjoint ownership, and one integration owner.
---

# Plan implementation ownership

Use the full Git commit containing this package as the skill version ID and record it in every artifact. A dirty package is unversioned and cannot satisfy a completed gate.

1. Verify the approved story packets, common base revision, shared contracts, and integration owner.
2. Require a dedicated linked worktree and feature branch per writer under the user-approved 2026-09-11 policy.
3. Serialize overlapping work; read-only reviewers may inspect the target worktree.
4. Limit writers to two and assign non-overlapping path budgets.
5. Keep lockfiles, migrations, shared/generated artifacts, CI, Keycloak/Traefik, deployment, and release state single-owner.
6. Require each worker's evidence/handoff and one integration owner to verify the combined revision.
7. Render [templates/coordination.md](templates/coordination.md). Do not create branches or mutate GitHub without separate authority.

Use [references/scenarios.md](references/scenarios.md) for ownership-conflict checks.
