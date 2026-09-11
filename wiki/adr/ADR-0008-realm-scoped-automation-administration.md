---
type: Decision
title: "ADR-0008: Use realm-local credentials for routine application administration"
description: Accepted architectural decision with attributable conversation approval recorded in PR 20.
tags: [adr, architecture]
adr_id: ADR-0008
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
    resource: /.agents-config/skills/ops/keycloak-admin/scripts/keycloak.py
    title: ".agents-config/skills/ops/keycloak-admin/scripts/keycloak.py"
    last_modified: 2026-09-11
  - id: source-2
    resource: /tests/tooling/test_keycloak.py
    title: "tests/tooling/test_keycloak.py"
    last_modified: 2026-09-11
---

# Context

Application automation needs to manage its realm without routinely using a master-realm administrator.

# Decision

Use a separately configured realm-local administrator for this application's routine automation, with the authentication realm configured independently from the target realm. Load the target from the explicitly selected environment configuration, keep credentials out of logs and Git, and preserve master configuration. Treat persistent administrators separately from run-owned test accounts.

# Alternatives for review

Master credentials for routine work or a narrower delegated role/service-account design are alternatives. The current realm-admin grant is realm-scoped but broad within that realm; this proposal does not claim least privilege within the realm.

# Consequences and limits

The reusable helper still supports other explicitly configured administrative realms and defaults to master when the admin realm is omitted. Isolation therefore depends on the selected credentials and permissions, not a universal helper prohibition. Initial bootstrap and later role changes are separate operations. No live credentials or privileges were inspected or changed in this audit.

# Approval provenance

Accepted on 2026-09-11 by the requesting human user in the Codex conversation (human:requesting-user). The user said: "lets not worrry about orca right now, but the ADRs look good to me".

The approval covers ADR-0001 through ADR-0012 as presented at commit 04e3abe09195516104180fb4f10ba23394cd1f04. It was transcribed into [PR #20](https://github.com/johnfabian/admin-starter-keycloak/pull/20#adr-acceptance---2026-09-11) and exactly reread before acceptance. This is conversation approval recorded by the assistant, not a GitHub review submitted by the human. No GitHub identity is inferred.

Acceptance confirms the architectural choice; it does not claim historical approval, independent runtime verification, production readiness, deployment or PR merge authorization. ORCA is deferred and does not block the accepted workflow.

The previous proposed record remains available at the approved Git revision. Record-ADR skill version: 04e3abe09195516104180fb4f10ba23394cd1f04.

# Evidence and related guidance

Source revision inspected: 342ec668b7848fe0200a9c317812831ca546b885. Draft documents are evidence of design intent, not implemented behavior.

- [operations/keycloak-cli.md](/operations/keycloak-cli.md)

# Supersession

No prior ADR is superseded. Existing records keep their identifiers.
