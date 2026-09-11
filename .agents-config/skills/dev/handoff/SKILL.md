---
name: handoff
description: Create and track a provider-neutral, Markdown-first checkpoint so a clean Claude Code or Codex session can resume without conversation history. Use after a stage, before a human gate, compaction, provider/worktree transfer, or intentional stop; local output remains provisional until exact GitHub publication and read-back.
---

# Create a handoff checkpoint

Use the full Git commit containing this package as the skill version ID and record it in the checkpoint. A dirty package is unversioned and cannot satisfy a completed gate.

Use [templates/checkpoint.md](templates/checkpoint.md) as the exact record shape.

## Workflow

1. Identify the target GitHub issue or pull request. If it is unknown, render a copy/paste checkpoint, mark it `provisional`, and do not post.
2. Capture the objective, bounded scope, feature/story links, base and current revisions, branch, checkout identity, and owned/excluded paths. Record each writer's linked worktree, branch and ownership.
3. List completed work as observable artifacts, not a transcript or private reasoning.
4. Record the IDs of applied rules and retrieved wiki concepts. Use `none` or `unknown` explicitly; never omit the field.
5. Record each check with exact command/category, result, timestamp, revision, and evidence/report path or URL. Do not turn an agent claim into gate evidence.
6. Record decisions, assumptions, artifact digests, reviewer independence, and human gate status. An agent, reaction, status field, or silence is not human approval.
7. List risks and blockers without secrets, tokens, raw prompts, sensitive data, or credentials.
8. Write exactly one next action. Make it bounded, imperative, and verifiable.
9. Assign a stable `sdlc-comment-key` and compute the source-artifact digest and exact published-body digest. Include the checkpoint in `$preview-issues`; do not post it outside the approved preview/publish boundary.
10. After authorized publication, re-read the checkpoint and record its immutable GitHub comment URL and verification time. Mark it `durable` only when the marker-plus-body is an exact match.
11. Never delete a local `.agent-work` copy automatically. Even after durable publication, cleanup requires explicit human direction.

Before handoff, verify that the current revision/worktree still matches the packet. A receiving session must re-check those values before acting. Local or copy/paste output is useful recovery material but is not the durable cross-provider record until GitHub read-back succeeds.

Use [references/scenarios.md](references/scenarios.md) to exercise clean-session and approval-boundary recovery.
