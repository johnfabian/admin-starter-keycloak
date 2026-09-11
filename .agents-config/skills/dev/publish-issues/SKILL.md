---
name: publish-issues
description: Publish only an exact, human-approved issue-and-comment preview to a named GitHub repository, preserving stable keys, relationships, metadata, approval evidence, read-back persistence, and idempotency. Use only after preview-issues returns a digest and an authorized human explicitly approves that exact digest; never reinterpret or silently overwrite historical prose.
disable-model-invocation: true
---

# Publish an approved preview

Use the full Git commit containing this package as the skill version ID and record it in the publication report. A dirty package is unversioned and cannot satisfy a completed gate.

1. Require the preview file, source JSON, exact SHA-256 digest, approval record, target repository, and mutation authorization.
2. Run `uv run scripts/verify_approval.py <preview.md> <approved-digest> <source.json>` from this skill directory. Stop on any preview or canonical-source digest mismatch.
3. Treat only the issue and ordered-comment fields accepted by the verifier as publication semantics. Reject hidden or unsupported source fields.
4. Inspect current GitHub state read-only. Find issues by the stable marker `<!-- sdlc-key: KEY -->`; reject duplicates or conflicting targets.
5. For each absent issue, publish the exact approved title/body/type/allowed labels and stable marker. Never rewrite an existing body's semantics.
6. Create parent/sub-issue and dependency relationships only after both issue IDs are known. Re-read before each mutation and treat an existing matching relationship as success.
7. Publish approved comments in source order only after their target issue IDs are known. Find each by `<!-- sdlc-comment-key: KEY -->`; create it when absent, reuse it only when the complete marker-plus-body is an exact match, and stop on duplicate or conflicting markers. Never edit a historical stage or handoff comment.
8. Re-read every created or reused issue and comment. Record its immutable URL, approved source-artifact digest, exact published-body digest, and verification time; a local path alone is not durable evidence.
9. Record returned IDs/URLs, target revision, approved digest, approver record, relationships, comment persistence results, and tool results in an append-only audit comment using [templates/publication-report.md](templates/publication-report.md). Key that report by the approved preview digest and reuse an existing exact report on retry; never edit it.
10. Stop on missing issue types/project fields, authority ambiguity, partial conflicting state, permission errors, unsupported relationship APIs, or failed read-back. Do not substitute labels for organization issue types silently.

Use [references/scenarios.md](references/scenarios.md) for publisher regression checks.
