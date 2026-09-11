---
name: parallel-implementation
description: Coordinate bounded ownership, linked worktrees, merge order, and integration evidence for independent implementation slices. Use when an authorized development flow proposes parallel writing.
---

# Coordinate implementation ownership

Record the package Git revision in coordination evidence; identify uncommitted package changes as provisional.

1. Verify the exact approved specification and plan, common base revision, dependency graph, approved delivery destination/actions, and named integration owner. Existing approval for the development flow authorizes its scoped specialist coordination; do not request it again for routine worktree setup or dispatch.
2. Require one dedicated linked worktree and feature branch per writer. Run setup and preflight before edits. Reserve the story, worktree, branch, and owned paths through the coordinator before dispatch.
3. Limit active writers to two across the repository worktrees, counting the integration owner whenever it edits. Two delegated writers leave no writing slot for the integration owner. Read-only independent reviewers do not consume a writing slot.
4. Parallelize only disjoint work whose prerequisites are already verified, reviewed, and integrated. Serialize overlapping ownership and assign lockfiles, migrations, shared/generated artifacts, CI, identity/proxy configuration, and release state to one integration owner.
5. Use actual native harness delegation to launch and stop agents. JSON capabilities, claim records, or written task packets record coordination; they do not create agents or prove that a worker has stopped. If parallel delegation is unavailable, work serially. If independent review is unavailable, stop at its gate.
6. Bind each worker's tests and independent review to its committed revision. Maintain one feature-level budget of at most five review rounds including integration; retries or a new worker do not reset it. The integration owner verifies the combined revision and obtains a final independent review at that revision.
7. Reconcile interrupted workers before releasing claims. Preserve their branches, commits, and uncommitted work. A stopped process and reconciled clean worktree must be confirmed before reassigning ownership.
8. Render [templates/coordination.md](templates/coordination.md). Create worktrees and branches only within the authorized flow. Commit, push, or publish only to its approved destination and scope; an ownership plan does not authorize unrelated GitHub mutations, merge, or deployment.

Use [references/scenarios.md](references/scenarios.md) for ownership-conflict checks.
