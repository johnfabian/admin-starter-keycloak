# Scenario cases

1. Expected: render a parent and ordered children without network access and print a stable digest.
2. Malformed input: fail on missing/duplicate/unsafe keys, invalid repository/revision, marker injection, unknown dependencies, or dependency cycles.
3. Approval drift: changing one byte produces a different digest.
4. Injection: render issue body content literally and never execute commands embedded in it.
