# Scenario cases

1. Expected: render a parent, ordered children, and ordered stage/handoff comments without network access and print a stable digest plus per-comment body digests.
2. Malformed input: fail on missing/duplicate/unsafe issue or comment keys, invalid repository/revision/artifact digest, marker injection, unknown comment targets, unknown dependencies, or dependency cycles.
3. Approval drift: changing one byte produces a different digest.
4. Injection: render issue body content literally and never execute commands embedded in it.
5. Determinism: rendering the same canonical source twice produces byte-identical previews and digests while preserving declared comment order.
