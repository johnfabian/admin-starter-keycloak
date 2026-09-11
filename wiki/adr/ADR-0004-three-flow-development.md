---
type: Decision
title: "ADR-0004: Use three developer flows with one routine approval"
description: Proposed decision record extracted from current wiki and source evidence.
tags: [adr, architecture]
adr_id: ADR-0004
decision_status: proposed
status: draft
generated: { by: "codex/gpt-6", at: "2026-09-11T20:32:36Z" }
stale_after: 2026-12-11
sources:
  - id: source-1
    resource: /specs/features/2026-09-11-agent-development-workflow.md
    title: "specs/features/2026-09-11-agent-development-workflow.md"
    last_modified: 2026-09-11
  - id: source-2
    resource: /.agents-config/skills/dev/plan-feature/SKILL.md
    title: ".agents-config/skills/dev/plan-feature/SKILL.md"
    last_modified: 2026-08-12
---

# Context

The starter kit has many specialist procedures. Requiring a separate user invocation for each one makes small features cumbersome.

# Decision proposal

Organize work as feature specification plus critique; implementation plan plus critique and one routine human approval; then implementation, tests, independent adversarial review/fixes, integration, knowledge updates and PR submission. Approval binds the exact specification, plan, and delivery target. Merge and deployment remain separate human decisions. A small feature can remain one story.

# Alternatives for review

A separate command and approval for every specialist increases interaction overhead. Unbounded autonomous delivery removes the selected review boundary. These alternatives are identified for this proposal, not a historical rejection record.

# Consequences and limits

The coordinator must retain scope, evidence and approvals across internal steps and resume. Existing skills do not yet implement the combined interface. The five-round feature-level review budget is still a draft interpretation, not an accepted subdecision.

# Approval provenance

The user selected the three-flow grouping in conversation on 2026-09-11. This proposal records that direction without inventing a GitHub acceptance record or approving the implementation draft.
Acceptance requires an attributable record of the exact outcome and approver. This audit creates no accepted ADR and makes no application, realm, network, or tooling-policy change.

# Evidence and related guidance

Source revision inspected: 342ec668b7848fe0200a9c317812831ca546b885. Draft documents are evidence of design intent, not implemented behavior.

- [conventions/agent-development-workflow.md](/conventions/agent-development-workflow.md)

# Supersession

No prior ADR is superseded. Existing records keep their identifiers.
