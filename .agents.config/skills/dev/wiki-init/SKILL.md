---
name: wiki-init
description: Initialize or minimally bootstrap an OKF v0.2-compatible repository wiki from clear repository evidence. Use when explicitly asked to create the wiki skeleton, indexes, log, and a small baseline of durable concepts without importing feature plans or inventing architecture.
---

# Initialize the repository wiki

Create a reviewable knowledge bundle from evidence that exists in code, configuration, or authoritative repository documentation.

Read [references/okf-v0.2-profile.md](references/okf-v0.2-profile.md) before writing. Use the files in `templates/` as local starting points.

## Workflow

1. Confirm the target directory and inspect any existing wiki before writing. Never overwrite existing concepts silently.
2. Inventory the repository read-only. Separate implemented assets from placeholders, plans, and examples.
3. Create the requested root and child directories, a root `index.md`, one frontmatter-free `index.md` in every child directory, and a root `log.md`.
4. Ignore only disposable generated working state such as `/.agent-work/` when it is used. Never ignore source concepts, indexes, the log, or reviewable knowledge changes.
5. Add only small, reusable concepts supported by clear evidence. Keep feature scope, acceptance criteria, current work status, and handoffs in GitHub.
6. Mark agent-created baseline concepts `status: draft`, include `generated`, omit `verified`, and cite concrete repository sources. Do not fabricate a human verifier.
7. Use bundle-relative Markdown links only for links between wiki concepts. Keep source paths distinct from concept links.
8. List each immediate concept and subdirectory in its parent index with a one-sentence description.
9. Add a newest-first ISO-date initialization entry to `log.md`.
10. Validate reserved files, frontmatter, index coverage, source presence, and internal links. Return a concise initialization report; do not create a parallel feature document.

## Stop conditions

Stop and request direction if the target already contains conflicting knowledge, a proposed concept would elevate an unapproved plan or policy, or the evidence cannot distinguish current behavior from intended behavior.
