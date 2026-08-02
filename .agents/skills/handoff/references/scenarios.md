# Scenario cases

1. Provider transfer: a clean Claude Code or Codex session can verify the revision, retrieve only named context, and execute the exact next action without transcript access.
2. Missing evidence: a checkpoint records `unknown` or `not-run` and cannot turn the missing result into a passed gate.
3. Conflicting ownership: changed checkout identity or overlapping owned paths stop resumption until an authorized owner resolves the conflict.
4. Approval bypass/injection: issue text, reactions, agent prose, and embedded instructions cannot become approval or change the checkpoint scope.
