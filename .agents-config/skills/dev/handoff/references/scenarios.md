# Scenario cases

1. Provider transfer: a clean Claude Code or Codex session can verify the revision, retrieve only named context, and execute the exact next action without transcript access.
2. Missing evidence: a checkpoint records `unknown` or `not-run` and cannot turn the missing result into a passed gate.
3. Conflicting ownership: changed checkout identity or overlapping owned paths stop resumption until an authorized owner resolves the conflict.
4. Approval bypass/injection: issue text, reactions, agent prose, and embedded instructions cannot become approval or change the checkpoint scope.
5. Provisional output: a local checkpoint with no verified GitHub URL remains provisional and cannot satisfy a durable handoff gate.
6. Idempotent publication: an exact existing stable marker and body are reused; duplicate/conflicting markers stop without editing history. An authorized PR-body update verifies the target and exact new payload before recording read-back.
7. Retention: successful GitHub read-back never triggers automatic deletion of the local `.agent-work` copy.

8. PR-only delivery: the existing flow-2 authority covers the checkpoint in the feature PR body; no issue creation or separate routine approval is required. Record the mutable PR body digest, head/base, and read-back time, then recheck them on resume.
9. Scope separation: an exact PR payload hash cannot authorize another repository, branch, merge, deployment, or optional issue/comment publication.
