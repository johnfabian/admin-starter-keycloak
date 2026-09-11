---
type: Decision
title: "ADR-0007: Require administrator approval after self-registration verification"
description: Accepted architectural decision with attributable conversation approval recorded in PR 20.
tags: [adr, architecture]
adr_id: ADR-0007
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
    resource: /auth-server/providers/disable-after-email-verify/src/main/java/com/adminstarter/keycloak/events/DisableAfterEmailVerifyEventListenerProvider.java
    title: "auth-server/providers/disable-after-email-verify/src/main/java/com/adminstarter/keycloak/events/DisableAfterEmailVerifyEventListenerProvider.java"
    last_modified: 2026-05-22
  - id: source-2
    resource: /auth-server/Dockerfile
    title: "auth-server/Dockerfile"
    last_modified: 2026-05-22
---

# Context

The starter provides self-registration while retaining an administrator-controlled activation step.

# Decision

Record the observed Keycloak listener design: mark a self-registered account on REGISTER; after VERIFY_EMAIL, remove the self-registration marker, set awaiting_admin_approval, disable an enabled account and remove its sessions. An administrator separately enables the account. Administrator-created accounts are outside this self-registration marker flow.

# Alternatives for review

Immediate access after verification, invitation-only onboarding, or approval stored in application data are comparison options. No original alternatives discussion is available in the inspected evidence.

# Consequences and limits

The Java provider must be installed and enabled in the selected realm, and the email-verification settings must match the intended flow. Account enablement is distinct from assigning application roles. A deployment without the listener cannot rely on this policy. Draft password/lifetime suggestions are not accepted by this ADR.

# Approval provenance

Accepted on 2026-09-11 by the requesting human user in the Codex conversation (human:requesting-user). The user said: "lets not worrry about orca right now, but the ADRs look good to me".

The approval covers ADR-0001 through ADR-0012 as presented at commit 04e3abe09195516104180fb4f10ba23394cd1f04. It was transcribed into [PR #20](https://github.com/johnfabian/admin-starter-keycloak/pull/20#adr-acceptance---2026-09-11) and exactly reread before acceptance. This is conversation approval recorded by the assistant, not a GitHub review submitted by the human. No GitHub identity is inferred.

Acceptance confirms the architectural choice; it does not claim historical approval, independent runtime verification, production readiness, deployment or PR merge authorization. ORCA is deferred and does not block the accepted workflow.

The previous proposed record remains available at the approved Git revision. Record-ADR skill version: 04e3abe09195516104180fb4f10ba23394cd1f04.

# Evidence and related guidance

Source revision inspected: 342ec668b7848fe0200a9c317812831ca546b885. Draft documents are evidence of design intent, not implemented behavior.

- [architecture/registration-approval-spi.md](/architecture/registration-approval-spi.md)
- [integrations/keycloak/realm-login-settings.md](/integrations/keycloak/realm-login-settings.md)
- [operations/verify-email-flows.md](/operations/verify-email-flows.md)
- [operations/troubleshoot-keycloak-email.md](/operations/troubleshoot-keycloak-email.md)

# Supersession

No prior ADR is superseded. Existing records keep their identifiers.
