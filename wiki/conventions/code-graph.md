---
type: Convention
title: Code graph and wiki ownership
description: Use local source graphs for navigation and maintained wiki concepts for durable reasoning.
tags: [automation]
status: draft
generated: { by: "codex/gpt-6", at: "2026-09-11T15:57:51Z" }
stale_after: 2026-12-11
sources:
  - id: implementation
    resource: /scripts/graph.py
    title: Implemented automation
    last_modified: 2026-09-11
---

# Retrieval order

Start at the wiki index for architecture, constraints, and runbooks. Use corepack pnpm graph:query --
"<question>" to locate related code. Verify material claims in source; a graph edge, especially an
inferred edge, does not prove runtime behavior.

# Ownership

Graphify stores generated symbols and code relationships. The wiki stores maintained explanations,
runbooks, constraints, and [ADRs](/adr/index.md). Active scope, status, approvals and handoffs belong
in GitHub; reusable procedures belong in skills. Do not copy the full wiki into a generated graph or
turn graph reports into architectural decisions.

# Local index and commit gate

Pinned graphifyy 0.9.58 extracts the explicit source corpus locally. Each worktree owns its ignored
graphify-out directory. Configuration, tooling and uv.lock are versioned. No model backend is configured.
Environment files, secrets, test artifacts, dependencies and planning drafts are excluded before extraction.

graph:update refreshes code; graph:check validates source/control hashes and graph integrity.
coverage.json identifies input files with no extracted nodes. The pre-commit command uses a separate
index made from Git's staged blobs, preserving partial staging and the user's index. Tooling controls
must be fully staged when changed. Failed extraction preserves the prior graph and blocks verification.
Refresh after branch switches/merges before relying on the graph.

[Graphify source and documentation](https://github.com/Graphify-Labs/graphify) describe upstream
capabilities. Repository commands intentionally avoid upstream hook installation and semantic document ingestion.
