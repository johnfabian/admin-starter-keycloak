---
type: Decision
title: ADR-0002: Separate generated graphs from maintained knowledge
description: Accepted architectural decision with attributable conversation approval recorded in PR 20.
tags: [adr, automation]
adr_id: ADR-0002
decision_status: accepted
decided_on: 2026-09-11
approved_by: "human:requesting-user"
status: stable
generated: { by: "codex/gpt-6", at: "2026-09-11T15:57:51Z" }
stale_after: 2026-12-11
verified: { by: human:requesting-user, at: "2026-09-11T21:27:10.569994+00:00" }
sources:
  - id: acceptance
    resource: https://github.com/johnfabian/admin-starter-keycloak/pull/20#adr-acceptance---2026-09-11
    title: Conversation approval of the exact ADR set recorded in PR 20
    author: "human:requesting-user"
    last_modified: 2026-09-11
  - id: implementation
    resource: /AGENTS.md
    title: Implemented automation
    last_modified: 2026-09-11
---

# Context

The user approved the automation implementation plan in conversation on 2026-09-11.

# Decision

Keep a local source graph per worktree and version its tooling/configuration. Store maintained explanations and accepted ADRs in the wiki. Active delivery records belong in GitHub. Versioning generated graphs was considered but would add stale snapshots and merge churn.

# Approval provenance

Accepted on 2026-09-11 by the requesting human user in the Codex conversation (human:requesting-user). The user said: "lets not worrry about orca right now, but the ADRs look good to me".

The approval covers ADR-0001 through ADR-0012 as presented at commit 04e3abe09195516104180fb4f10ba23394cd1f04. It was transcribed into [PR #20](https://github.com/johnfabian/admin-starter-keycloak/pull/20#adr-acceptance---2026-09-11) and exactly reread before acceptance. This is conversation approval recorded by the assistant, not a GitHub review submitted by the human. No GitHub identity is inferred.

Acceptance confirms the architectural choice; it does not claim historical approval, independent runtime verification, production readiness, deployment or PR merge authorization. ORCA is deferred and does not block the accepted workflow.

The previous proposed record remains available at the approved Git revision. Record-ADR skill version: 04e3abe09195516104180fb4f10ba23394cd1f04.

# Supersession

No preceding ADR exists. Preserve this identifier if the decision is later superseded.

# Ownership clarification

The selected three-flow convention places feature specifications in specs/features and implementation plans in specs/implementation-plans, with GitHub delivery, review and approval records linked to their revisions. The wiki maintains explanations and decision records; skills/rules define procedures and constraints. This refines the same ownership decision rather than creating a competing ADR. The workflow implementation at the approved revision replaced the older GitHub-only artifact persistence model.

The configured Graphify corpus includes source files and supported tests/automation, but excludes Markdown, environment files and provider discovery links. Code relationships do not supply decision rationale, approval provenance or operational instructions. Both the local code graph and maintained wiki are required by this convention.

See [code graph ownership](/conventions/code-graph.md) and [three-flow development](/conventions/agent-development-workflow.md).
