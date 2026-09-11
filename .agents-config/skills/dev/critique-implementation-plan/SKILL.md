---
name: critique-implementation-plan
description: Independently challenge vertical stories, dependencies, ownership and verification before scoped delivery approval. Use inside plan-implementation or after material plan changes.
---

# critique implementation plan

Record the package Git revision in checkpoints; identify uncommitted package changes as provisional.

Use a separate read-only reviewer with the exact specification and plan digests.

1. Verify requirement coverage, observable story outcomes, acceptance and denied/failure paths.
2. Challenge cycles, missing dependencies, horizontal decomposition, shared migrations/lockfiles, overlapping ownership, unknown interfaces, rollback and integration order.
3. Confirm at most two writing agents, dedicated worktrees, one integration owner, serial fallback, real independent reviewers and the shared five-round implementation review budget.
4. Verify test commands exist and evidence can bind to actual revisions. Inspect real source for material claims.
5. Return findings using [the critique template](templates/critique.md). Unresolved critical/high findings block readiness. The critic cannot implement, self-approve or grant publication authority.
