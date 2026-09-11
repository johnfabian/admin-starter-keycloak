---
type: Decision
title: "ADR-0004: Use three developer flows with one routine approval"
description: Accepted architectural decision with attributable conversation approval recorded in PR 20.
tags: [adr, architecture]
adr_id: ADR-0004
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

# Decision

Organize work as feature specification plus critique; implementation plan plus critique and one routine human approval; then implementation, tests, independent adversarial review/fixes, integration, knowledge updates and PR submission. Approval binds the exact specification, plan, and delivery target. Merge and deployment remain separate human decisions. A small feature can remain one story.

# Alternatives for review

A separate command and approval for every specialist increases interaction overhead. Unbounded autonomous delivery removes the selected review boundary. These alternatives are identified for this proposal, not a historical rejection record.

# Consequences and limits

The coordinator must retain scope, evidence and approvals across internal steps and resume. The skills and portable helper now implement the combined interface with one shared five-round feature review budget. The architectural choice is now accepted through the approval recorded below.

# Approval provenance

Accepted on 2026-09-11 by the requesting human user in the Codex conversation (human:requesting-user). The user said: "lets not worrry about orca right now, but the ADRs look good to me".

The approval covers ADR-0001 through ADR-0012 as presented at commit 04e3abe09195516104180fb4f10ba23394cd1f04. It was transcribed into [PR #20](https://github.com/johnfabian/admin-starter-keycloak/pull/20#adr-acceptance---2026-09-11) and exactly reread before acceptance. This is conversation approval recorded by the assistant, not a GitHub review submitted by the human. No GitHub identity is inferred.

Acceptance confirms the architectural choice; it does not claim historical approval, independent runtime verification, production readiness, deployment or PR merge authorization. ORCA is deferred and does not block the accepted workflow.

The previous proposed record remains available at the approved Git revision. Record-ADR skill version: 04e3abe09195516104180fb4f10ba23394cd1f04.

# Evidence and related guidance

Source revision inspected: 342ec668b7848fe0200a9c317812831ca546b885. Draft documents are evidence of design intent, not implemented behavior.

- [conventions/agent-development-workflow.md](/conventions/agent-development-workflow.md)

# Supersession

No prior ADR is superseded. Existing records keep their identifiers.
