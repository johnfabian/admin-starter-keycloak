---
type: Decision
title: ADR-0002: Separate generated graphs from maintained knowledge
description: Proposed durable automation decision awaiting GitHub approval provenance.
tags: [adr, automation]
adr_id: ADR-0002
decision_status: proposed
status: draft
generated: { by: "codex/gpt-6", at: "2026-09-11T15:57:51Z" }
stale_after: 2026-12-11
sources:
  - id: implementation
    resource: /AGENTS.md
    title: Implemented automation
    last_modified: 2026-09-11
---

# Context

The user approved the automation implementation plan in conversation on 2026-09-11.

# Decision proposal

Keep a local source graph per worktree and version its tooling/configuration. Store maintained explanations and accepted ADRs in the wiki. Active delivery records belong in GitHub. Versioning generated graphs was considered but would add stale snapshots and merge churn.

# Approval and consequences

Implementation authorization is recorded in the conversation. This concept remains draft/proposed until
the accepted outcome and attributable approval are persisted in a GitHub issue or PR. Do not invent an
approver identity or immutable approval URL. After that record exists, use record-adr to accept this ADR.

# Supersession

No preceding ADR exists. Preserve this identifier if the decision is later accepted or superseded.
