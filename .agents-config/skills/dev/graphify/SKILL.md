---
name: graphify
description: Query and refresh this repository's local code graph for dependency tracing, change impact, and code discovery. Keep durable explanations and decisions in the OKF wiki.
---

# Local code graph

Run from the linked worktree root. The pinned Graphify engine is invoked through repository commands;
do not run the upstream installer over the shared agent configuration.

- Run corepack pnpm graph:query -- "<question>" for a scoped code relationship query. It refreshes stale input automatically.
- Run corepack pnpm graph:update after edit batches and integration; graph:check verifies content hashes.
- Read graphify-out/coverage.json for files without extracted nodes and inspect those sources directly.
- Validate important relationships in source; inferred edges are navigation aids, not proof of behavior.
- Run corepack pnpm verify:commit before committing. It verifies a separate staged-source graph without staging files.
- On a fresh worktree use agent:setup with an explicit absolute environment path. Do not copy another worktree's graph.

The code-only corpus excludes secrets, environment files, dependencies, test artifacts, provider symlinks,
and planning drafts. Do not expand it to live databases, documentation model ingestion, or external
services without a scoped request. Wiki explanations and ADRs remain maintained knowledge, not graph output.
