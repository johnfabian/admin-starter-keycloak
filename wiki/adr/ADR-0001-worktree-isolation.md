---
type: Decision
title: ADR-0001: Isolate agent writes in linked worktrees
description: Proposed durable automation decision awaiting GitHub approval provenance.
tags: [adr, automation]
adr_id: ADR-0001
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

Use a dedicated linked worktree and feature branch per writer, at most two disjoint writers, and one integration owner. OS locking serializes the existing shared local test stack. The alternative shared writing checkout risks overwritten changes; independent service stacks add configuration and resource cost.

# Approval and consequences

Implementation authorization is recorded in the conversation. This concept remains draft/proposed until
the accepted outcome and attributable approval are persisted in a GitHub issue or PR. Do not invent an
approver identity or immutable approval URL. After that record exists, use record-adr to accept this ADR.

# Supersession

No preceding ADR exists. Preserve this identifier if the decision is later accepted or superseded.
