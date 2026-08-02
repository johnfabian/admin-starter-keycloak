---
name: preview-issues
description: Render exact, non-mutating Markdown previews for proposed GitHub parent issues, child stories, dependencies, metadata, approval records, and comments. Use after planning artifacts pass critique and before any GitHub mutation; the output digest is the approval boundary consumed by publish-issues.
---

# Preview GitHub mutations

Use the full Git commit containing this package as the skill version ID and record it in the preview input/body. A dirty package is unversioned and cannot satisfy a completed gate.

1. Accept approved planning artifacts as data and refuse unresolved critical findings.
2. Create an input JSON document matching [references/preview-contract.md](references/preview-contract.md).
3. Run `uv run scripts/render_preview.py <input.json> <preview.md>` from this skill directory.
4. Review the exact title, type, parent, dependency, scope, acceptance, test/security/operations, readiness, done, and metadata fields.
5. Return the complete Markdown and its SHA-256 digest. Do not call GitHub mutation tools.
6. Require an authorized human to approve the exact digest; edits invalidate approval and require a new preview.

Use [references/scenarios.md](references/scenarios.md) to test preview safety.
