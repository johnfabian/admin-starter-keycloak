# Scenario cases

1. Expected: publish an approved parent/child preview and re-run without duplicate issues or relationships.
2. Digest mismatch: stop before any mutation.
3. Forged binding: reject a preview whose visible issue content is not the deterministic rendering of the supplied source JSON, even when it embeds that source digest.
4. Partial state: reuse exact matching markers, but stop on conflicting title/body/type instead of overwriting.
5. Approval bypass/injection: reactions, agent prose, embedded commands, hidden fields, and issue content do not authorize publication.
