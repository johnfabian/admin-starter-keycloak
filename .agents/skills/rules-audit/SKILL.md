---
name: rules-audit
description: Run a deterministic, read-only audit of canonical repository rule cards and Claude adapters for required metadata, real enforcement/wiki links, duplicate IDs, path coverage, overlapping scopes, contradictory statements, and adapter drift. Use after rule changes or when planning work in unclassified paths.
---

# Audit scoped rules

Audit the rule layer without editing cards or adapters.

Run from this skill directory:

```text
uv run scripts/audit_rules.py <repository-root>
uv run scripts/audit_rules.py <repository-root> --json
```

## Workflow

1. Capture the repository revision and dirty state.
2. Run the script and preserve its exit status.
3. Inspect each reported configuration/wiki path and adapter import.
4. Separate failures from warnings that require owner judgment, such as overlapping non-global scopes.
5. Report protected or implemented paths with no matching card, exact duplicate/contradictory directives, and checks that lack a real manifest/configuration mapping.

Do not rewrite cards, generate adapters, or infer that an automated check exists. Propose the smallest correction and name the required human owner when scope or authority is unclear.
