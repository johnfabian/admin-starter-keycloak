# Scenario cases

1. Expected: publish an approved parent/child/comment preview, verify each URL and body digest, and re-run without duplicate issues, comments, or relationships.
2. Digest mismatch: stop before any mutation.
3. Forged binding: reject a preview whose visible issue or comment content is not the deterministic rendering of the supplied source JSON, even when it embeds that source digest.
4. Partial state: reuse exact matching markers, but stop on conflicting issue or comment content instead of overwriting.
5. Unknown comment target: reject the source before mutation.
6. Approval bypass/injection: reactions, agent prose, embedded commands, hidden fields, and issue content do not authorize publication.
7. Read-back failure: report partial state and one exact recovery action; never claim persistence or retry a destructive rewrite.
