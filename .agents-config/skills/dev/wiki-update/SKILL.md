---
name: wiki-update
description: Add, refresh, deprecate, or correct a small set of durable OKF v0.2 repository concepts from verified evidence. Use after a merged change, approved architecture outcome, incident learning, or explicit correction; never use it to archive active feature plans or fabricate verification.
---

# Update durable wiki knowledge

Use the full Git commit containing this package as the skill version ID and record it in the change report. A dirty package is unversioned and cannot satisfy a completed gate.

1. Accept a scoped trigger and identify only affected concepts through the wiki index.
2. Verify changed claims against current code/configuration and attributable sources.
3. Keep feature scope and acceptance in versioned specs/features, stories and dependencies in specs/implementation-plans, and delivery status, approval/review evidence and handoffs in authorized GitHub issues/PRs. Keep those active artifacts out of the durable wiki.
4. Preserve `draft` and unverified status unless a real human verifier and evidence are provided.
5. Update required metadata, relevant immediate indexes, links, freshness, and root log without rewriting unrelated concepts.
6. Use bundle-relative links and preserve deprecated/superseded history.
7. Render the change summary with [templates/update-report.md](templates/update-report.md), then run the repository wiki audit.

Use [references/scenarios.md](references/scenarios.md) when changing this workflow.
