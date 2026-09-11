---
name: implement-story
description: Implement one approved story with scoped worktree ownership, tests, independent review, and revision-bound evidence. Use for a ready story delegated by an authorized feature coordinator or requested directly by the user.
---

# Implement an approved story

Record the package Git revision in the story evidence; identify uncommitted package changes as provisional.

Accept a story delegated by the authorized `implement-feature` coordinator without requiring the developer to invoke this specialist separately. Verify the attributable approval for the exact specification and implementation-plan digests, repository, feature branch, target base, and delivery actions through commit, push, and PR submission. Reuse that approval within scope. Material scope or destination changes, missing authority, or unresolved blocking findings require resolution; merge and deployment are outside this delivery approval.

1. Validate [templates/story-packet.md](templates/story-packet.md): outcome, criteria, path ownership, rules, relevant wiki concepts, tests, dependencies, approved scope, and exact verification commands. A dependent story is ready only after its prerequisites are verified, reviewed, and integrated into the assigned base revision.
2. Confirm a dedicated linked worktree and feature branch, the coordinator's active ownership claim, and matching base revision. Run `corepack pnpm agent:setup -- --env-file <absolute-path>` for a fresh worktree and `corepack pnpm agent:check` before edits. Reference the selected environment file without copying or printing it.
3. Keep at most two writers active across the repository worktrees, including the integration owner when editing. Own only assigned paths; shared files and lockfiles have one integration owner. Stop and reconcile a conflicting claim before writing.
4. Record the pre-change baseline and existing failures. Use automated browser characterization where applicable. Add characterization for existing risky behavior or a failing test for new behavior when it meaningfully demonstrates the change.
5. Make the scoped change, run matching rule checks and story verification, and distinguish tests from lint/build evidence. Refresh the worktree's local graph after edit batches. Run `corepack pnpm verify:commit` before authorized commits and `corepack pnpm verify:story` at story completion.
6. Return the committed revision and exact command, result, time, and evidence digest to the coordinator. Request actual independent review through the harness; a written reviewer name or JSON record does not instantiate a reviewer. Never self-review or claim review that did not occur.
7. Participate in the coordinator's single feature budget of at most five review rounds, including final integration. Preserve failed reviews and the current round across retries, worker restarts, and handoffs. A new review attempt for the same subject needs the next shared round; do not create a per-story budget or reuse evidence after the reviewed revision changes. Open critical or high findings and failed checks block integration.
8. Return a scoped handoff for integration. Preserve interrupted work and ownership until the actual worker is stopped and its worktree is reconciled. Keep a local checkpoint provisional until it is included in the authorized PR body or another authorized GitHub record and exactly read back; no issue publication is required for PR-only delivery.

Use [references/scenarios.md](references/scenarios.md) for control regression checks.
