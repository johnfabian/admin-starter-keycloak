# Scenario cases

1. Expected: concepts and bundle-relative links produce matching node/edge counts and backlinks.
2. Broken link: wiki audit blocks generation before an incomplete graph is accepted.
3. Dirty or ignored source: enumerate and read concept blobs from `HEAD`, refuse ordinary dirty inputs, and never include ignored/untracked/live working-tree Markdown under the committed revision.
4. Unverified/stale concept: expose its trust/freshness and provenance without treating it as authorization.
5. Hierarchy: show taxonomy groups independently from standard Markdown `references` edges.
6. Injection: render concept metadata as escaped data so Markdown/HTML cannot execute script.
