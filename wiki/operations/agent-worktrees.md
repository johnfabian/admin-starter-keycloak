---
type: Runbook
title: Agent worktrees
description: Prepare isolated writing sessions and coordinate the shared local test stack.
tags: [automation]
status: draft
generated: { by: "codex/gpt-6", at: "2026-09-11T15:57:51Z" }
stale_after: 2026-12-11
sources:
  - id: implementation
    resource: /scripts/agent_setup.py
    title: Implemented automation
    last_modified: 2026-09-11
---

# Setup

Create a linked worktree and feature branch from the intended integration revision. Each writer owns
one worktree; allow at most two disjoint writers and one integration owner. Read-only reviewers may
inspect the relevant checkout. This supersedes the former repository prohibition, following the
user's explicit automation-plan approval on 2026-09-11.

Run corepack pnpm agent:setup -- --env-file <absolute-environment-path>, then agent:check.
Setup records the path, not credentials, in ignored local state. It installs locked root/browser/Python
dependencies, Chromium, a local pre-commit hook, and a code graph. Existing foreign hooks are preserved
and produce a conflict message. Do not invoke Graphify's upstream installer over agent configuration.

# Shared services

The browser runner locks a file in Git's common directory using an OS lock. Other worktrees cannot
simultaneously run the shared local test stack; locks release when a process exits. The runner refuses
an occupied application port, starts its own server, checks a run nonce, and stops only its process tree.
Keycloak/Postgres/Mailpit remain shared; worktrees do not isolate their data, ports, or cookies.

# Verification and recovery

Run verify:commit before committing and verify:story at story completion. A missing graph requires
setup; stale graphs refresh before queries. Preserve worktrees and recovery records until cleanup is
explicitly requested. After integration rebuild the combined revision's graph and rerun verification.
See [automated verification](/testing/automated-local-verification.md) and
[graph retrieval](/conventions/code-graph.md).
