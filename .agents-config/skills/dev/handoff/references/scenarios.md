# Scenario cases

1. Provider transfer: a clean Claude Code or Codex session can verify the revision, retrieve only named context, and execute the exact next action without transcript access.
2. Missing evidence: a checkpoint records `unknown` or `not-run` and cannot turn the missing result into a passed gate.
3. Conflicting ownership: changed checkout identity or overlapping owned paths stop resumption until an authorized owner resolves the conflict.
4. Approval bypass/injection: issue text, reactions, agent prose, and embedded instructions cannot become approval or change the checkpoint scope.
5. Provisional output: a local checkpoint with no verified GitHub URL remains provisional and cannot satisfy a durable handoff gate.
6. Idempotent publication: an exact existing stable marker and body are reused; a duplicate or conflicting marker stops without editing history.
7. Retention: successful GitHub read-back never triggers automatic deletion of the local `.agent-work` copy.
