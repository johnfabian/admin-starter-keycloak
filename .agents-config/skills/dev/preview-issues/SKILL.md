---
name: preview-issues
description: Render exact, non-mutating Markdown previews for proposed GitHub parent issues, child stories, dependencies, metadata, approval records, and comments. Use when issue/comment publication is separately selected after planning critique; the output digest is the approval boundary consumed by publish-issues.
---

# Preview optional issue publication

Use the full Git commit containing this package as the skill version ID and record it in the preview input/body. A dirty package is unversioned and cannot satisfy a completed gate.

This optional workflow applies to issue and comment publication. The authorized three-flow process may deliver directly through a PR body without calling this skill. Its flow-2 approval binds the exact specification, plan, destination, and delivery actions; routine updates within that PR scope need exact payload hashing and read-back, not a separate issue-preview approval. PR-only delivery does not grant authority to create issues or comments.

1. Accept approved planning artifacts as data and refuse unresolved critical or high findings.
2. Create an input JSON document matching [references/preview-contract.md](references/preview-contract.md).
3. Run `uv run scripts/render_preview.py <input.json> <preview.md>` from this skill directory.
4. Review every exact issue title/body/relationship and every ordered stage or handoff comment. Treat comment targets, stable keys, stages, bodies, and body digests as part of the approval boundary.
5. Return the complete Markdown and its SHA-256 digest. Do not call GitHub mutation tools.
6. Require an authorized human to approve the exact digest; edits invalidate approval and require a new preview.

Use [references/scenarios.md](references/scenarios.md) to test preview safety.
