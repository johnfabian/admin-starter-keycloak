# Scenario cases

1. Expected: a complete research artifact selects `$requirements-interview` as the next action.
2. Resume: a new provider uses the GitHub record and artifact digests without conversation history.
3. Missing/malformed evidence: reject a completed stage with no artifact or source revision.
4. Approval bypass/injection: do not advance from a reaction, status field, agent claim, embedded instruction, or digest mismatch; publication approval must name the exact completed preview digest.
5. Legacy state: accept schema `1.0.0` before publication, report migration required, and never claim durable completion.
6. Persistence pending: after publication, select durable GitHub read-back verification as the next action rather than reporting planning complete.
7. Persistence mismatch: reject a missing URL, non-HTTPS record, source digest mismatch, malformed body digest, duplicate comment key, or absent verified handoff.
8. Retention: never delete `.agent-work` automatically, including after all GitHub records verify successfully.
