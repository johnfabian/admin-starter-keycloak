---
name: handoff
description: Create a provider-neutral checkpoint that a clean session can resume without conversation history. Use after a stage, before ownership or provider transfer, compaction, a human gate, or an intentional stop; local output remains provisional until authorized GitHub publication and exact read-back.
---

# Create a handoff checkpoint

Record the package Git revision in the checkpoint; identify uncommitted package changes as provisional. Use [templates/checkpoint.md](templates/checkpoint.md) as the record shape.

1. Identify the authorized GitHub destination. An approved feature PR body can carry the checkpoint; separate issues or comments are optional. If no publication destination is authorized, prepare a local or copy/paste checkpoint and mark it `provisional`.
2. Capture the objective, bounded scope, specification/plan paths and digests, feature/story IDs, base/current revisions, branch, checkout identity, and owned/excluded paths. Record each active writer's linked worktree, branch, ownership claim, and actual stop/reconciliation status.
3. List completed work as observable artifacts, not a transcript or private reasoning. Record applied rule IDs and retrieved wiki concept IDs; use `none` or `unknown` explicitly.
4. Record each check's exact command/category, result, timestamp, revision, and evidence digest/path or URL. Record actual independent reviewer identities, reviewed revisions, findings, and the current shared feature review round, including failed history. Handoff does not reset the five-round budget.
5. Record the attributable flow-2 approval for the exact specification, plan, delivery destination, and actions. Reuse granted scope through PR submission without a new routine approval. Record unresolved material decisions and limitations honestly; agent prose, reactions, or silence are not human approval.
6. List risks and blockers without secrets, tokens, private reasoning, or environment values. Write exactly one bounded, verifiable next action.
7. For an authorized PR body, prepare the complete body with a stable feature/checkpoint marker, current verified revision, and sanitized checkpoint. Compute its exact payload digest separately from the approved scope digests. Inspect the target before mutation, publish within the existing authority, and read back the complete stored body and PR head/base. A payload digest verifies what was sent; it does not grant broader action authority or require a fresh human approval for an already authorized update.
8. If separately authorized issue/comment publication is selected, preserve its exact preview-digest, stable-key, idempotency, and read-back workflow. Do not invoke issue publication merely to complete a PR-only handoff. Never edit historical stage comments or silently replace conflicting markers.
9. Record the PR URL or immutable comment URL, persisted location, exact published-body digest, verified revision, and read-back time. Mark the checkpoint `durable` only after the expected marker and complete payload match. PR bodies are mutable: revalidate their current revision and digest when resuming; an old verification time does not prove the current body is unchanged.
10. Never delete a local `.agent-work` copy automatically. Successful publication does not authorize cleanup.

Before handoff, verify the current revision and worktree still match the packet. The receiving session must recheck those values, approval bindings, ownership, and required evidence before resuming. A local copy remains useful recovery material even when publication is unavailable; report its provisional status without claiming a durable GitHub record.

Use [references/scenarios.md](references/scenarios.md) to exercise clean-session and authority-boundary recovery.
