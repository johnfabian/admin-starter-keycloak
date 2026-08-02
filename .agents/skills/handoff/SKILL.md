---
name: handoff
description: Create a provider-neutral, Markdown-first checkpoint for a GitHub issue or pull request so a clean Claude Code or Codex session can resume without conversation history. Use after a stage, before a human gate, compaction, provider/worktree transfer, or intentional stop.
---

# Create a durable handoff

Use [templates/checkpoint.md](templates/checkpoint.md) as the exact record shape.

## Workflow

1. Identify the target GitHub issue or pull request. If it is unknown, render a copy/paste checkpoint and do not post.
2. Capture the objective, bounded scope, feature/story links, base and current revisions, branch, worktree, and owned/excluded paths.
3. List completed work as observable artifacts, not a transcript or private reasoning.
4. Record the IDs of applied rules and retrieved wiki concepts. Use `none` or `unknown` explicitly; never omit the field.
5. Record each check with exact command/category, result, timestamp, revision, and evidence/report path or URL. Do not turn an agent claim into gate evidence.
6. Record decisions, assumptions, and human gate status. An agent, reaction, status field, or silence is not human approval.
7. List risks and blockers without secrets, tokens, raw prompts, sensitive data, or credentials.
8. Write exactly one next action. Make it bounded, imperative, and verifiable.
9. Post only when the user has authorized GitHub mutation and the target is explicit; otherwise return the Markdown.

Before handoff, verify that the current revision/worktree still matches the packet. A receiving session must re-check those values before acting.
