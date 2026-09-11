---
type: Decision
title: "ADR-0009: Keep canonical agent procedures portable across harnesses"
description: Proposed decision record extracted from current wiki and source evidence.
tags: [adr, architecture]
adr_id: ADR-0009
decision_status: proposed
status: draft
generated: { by: "codex/gpt-6", at: "2026-09-11T20:32:36Z" }
stale_after: 2026-12-11
sources:
  - id: source-1
    resource: /AGENTS.md
    title: "AGENTS.md"
    last_modified: 2026-09-11
  - id: source-2
    resource: /.agents-config/rules/global.md
    title: ".agents-config/rules/global.md"
    last_modified: 2026-09-11
  - id: source-3
    resource: /.agents-config/rules/skills.md
    title: ".agents-config/rules/skills.md"
    last_modified: 2026-08-12
  - id: source-4
    resource: /.agents-config/skills/meta/skills-audit/scripts/audit_skills.py
    title: ".agents-config/skills/meta/skills-audit/scripts/audit_skills.py"
    last_modified: 2026-09-11
---

# Context

The same starter is used from multiple agent harnesses and linked worktrees.

# Decision proposal

Record the existing canonical .agents-config skill/rule catalogs with thin provider discovery links and portable Python automation invoked through uv. Keep operational knowledge separate from executable procedures. Each provider must preserve the same scope, worktree and approval boundaries.

# Alternatives for review

Independent copied skill bodies per provider or provider-specific orchestration scripts are alternatives, not verified historical rejections.

# Consequences and limits

Shared content reduces duplicated instructions, but discovery links do not supply a universal delegation API. Project-scoped adapter validation is now the default; global inspection/repair requires explicit opt-in, avoiding automatic cross-worktree global rewrites. ORCA compatibility is unverified. Preserve existing POSIX backup scripts unless a migration is separately requested.

# Approval provenance

This is a proposed record of architecture observed in the cited source. The original approver, decision date and historical rationale were not established. Do not treat implemented behavior as approval or infer that the alternatives below were historically considered.
Acceptance requires an attributable record of the exact outcome and approver. This audit creates no accepted ADR and makes no application, realm, network, or tooling-policy change.

# Evidence and related guidance

Source revision inspected: 342ec668b7848fe0200a9c317812831ca546b885. Draft documents are evidence of design intent, not implemented behavior.

- [conventions/repository-tooling.md](/conventions/repository-tooling.md)
- [conventions/agent-development-workflow.md](/conventions/agent-development-workflow.md)

# Supersession

No prior ADR is superseded. Existing records keep their identifiers.
