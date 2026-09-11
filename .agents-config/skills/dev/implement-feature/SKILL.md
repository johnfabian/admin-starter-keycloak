---
name: implement-feature
description: Deliver an approved feature through isolated stories, testing, independent review and a verified pull request. Use when asked to implement an approved feature or resume delivery.
---

# implement feature

Record the package Git revision in checkpoints; identify uncommitted package changes as provisional.

Own the complete third flow. Read [the execution contract](references/execution.md) before dispatch. Use [the evidence templates](templates/evidence.md) for machine records.

1. Verify actual approval and spec/plan digests, repository/branch/base, matching rules and relevant wiki concepts. Run worktree preflight. Reuse granted scope through PR submission.
2. Detect actual harness capabilities. Native agent APIs perform delegation; the Python helper validates state and evidence. Declare independent review, worktrees, parallel support, harness and coordinator identity. If parallel writing is unavailable, use one worker at a time. If independent review is unavailable, stop at that gate.
3. Initialize/resume v2 state, record both critiques and scoped approval. Calculate dependency-ready stories and atomically reserve paths/worktrees before dispatch. Readiness requires verified, reviewed, integrated prerequisites.
4. Delegate `implement-story` with a complete packet to each writing agent in its own linked worktree. At most two writers globally; the coordinator counts when editing and must leave capacity accordingly. Keep shared integration paths under one owner.
5. Run tests, request a separate adversarial reviewer, fix and reverify. Use one feature-level budget of at most five review rounds including final integration. Record every failed review and never reset counters on retry, worker restart, or handoff.
6. Integrate reviewed commits in dependency order. Preserve interrupted workers and claims until their actual termination and worktree state are reconciled. Do not kill servers or discard work automatically.
7. Update relevant wiki concepts and proposed/approved ADRs honestly, refresh the local code graph, run mapped rules and explicitly invoke skills-audit/rules-audit after their changes. Run wiki audit after wiki edits.
8. Commit the integrated changes after `verify:commit`, then freeze that HEAD for `verify:story` and independent final adversarial review. Prepare sanitized evidence, handoff and PR body under ignored working files, then push/update the authorized PR with exact read-back. Any further source edit requires new applicable verification/review. No merge or deployment.
9. Report the PR, tested revision and remaining limitations. Do not call a feature complete with failed checks or unresolved blocking findings.

A human reviews the resulting implementation in the same integration worktree/PR. Separate spec-only approval PRs are optional, not a prerequisite.
