---
type: Decision
title: "ADR-0009: Keep canonical agent procedures portable across harnesses"
description: Accepted architectural decision with attributable conversation approval recorded in PR 20.
tags: [adr, architecture]
adr_id: ADR-0009
decision_status: accepted
decided_on: 2026-09-11
approved_by: "human:requesting-user"
status: stable
generated: { by: "codex/gpt-6", at: "2026-09-11T20:32:36Z" }
stale_after: 2026-12-11
verified: { by: human:requesting-user, at: "2026-09-11T21:27:10.569994+00:00" }
sources:
  - id: acceptance
    resource: https://github.com/johnfabian/admin-starter-keycloak/pull/20#adr-acceptance---2026-09-11
    title: Conversation approval of the exact ADR set recorded in PR 20
    author: "human:requesting-user"
    last_modified: 2026-09-11
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

# Decision

Record the existing canonical .agents-config skill/rule catalogs with thin provider discovery links and portable Python automation invoked through uv. Keep operational knowledge separate from executable procedures. Each provider must preserve the same scope, worktree and approval boundaries.

# Alternatives for review

Independent copied skill bodies per provider or provider-specific orchestration scripts are alternatives, not verified historical rejections.

# Consequences and limits

Shared content reduces duplicated instructions, but discovery links do not supply a universal delegation API. Project-scoped adapter validation is now the default; global inspection/repair requires explicit opt-in, avoiding automatic cross-worktree global rewrites. ORCA compatibility is unverified. Preserve existing POSIX backup scripts unless a migration is separately requested.

# Approval provenance

Accepted on 2026-09-11 by the requesting human user in the Codex conversation (human:requesting-user). The user said: "lets not worrry about orca right now, but the ADRs look good to me".

The approval covers ADR-0001 through ADR-0012 as presented at commit 04e3abe09195516104180fb4f10ba23394cd1f04. It was transcribed into [PR #20](https://github.com/johnfabian/admin-starter-keycloak/pull/20#adr-acceptance---2026-09-11) and exactly reread before acceptance. This is conversation approval recorded by the assistant, not a GitHub review submitted by the human. No GitHub identity is inferred.

Acceptance confirms the architectural choice; it does not claim historical approval, independent runtime verification, production readiness, deployment or PR merge authorization. ORCA is deferred and does not block the accepted workflow.

The previous proposed record remains available at the approved Git revision. Record-ADR skill version: 04e3abe09195516104180fb4f10ba23394cd1f04.

# Evidence and related guidance

Source revision inspected: 342ec668b7848fe0200a9c317812831ca546b885. Draft documents are evidence of design intent, not implemented behavior.

- [conventions/repository-tooling.md](/conventions/repository-tooling.md)
- [conventions/agent-development-workflow.md](/conventions/agent-development-workflow.md)

# Supersession

No prior ADR is superseded. Existing records keep their identifiers.
