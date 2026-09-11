---
type: Decision
title: "ADR-0007: Require administrator approval after self-registration verification"
description: Proposed decision record extracted from current wiki and source evidence.
tags: [adr, architecture]
adr_id: ADR-0007
decision_status: proposed
status: draft
generated: { by: "codex/gpt-6", at: "2026-09-11T20:32:36Z" }
stale_after: 2026-12-11
sources:
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

# Decision proposal

Record the observed Keycloak listener design: mark a self-registered account on REGISTER; after VERIFY_EMAIL, remove the self-registration marker, set awaiting_admin_approval, disable an enabled account and remove its sessions. An administrator separately enables the account. Administrator-created accounts are outside this self-registration marker flow.

# Alternatives for review

Immediate access after verification, invitation-only onboarding, or approval stored in application data are comparison options. No original alternatives discussion is available in the inspected evidence.

# Consequences and limits

The Java provider must be installed and enabled in the selected realm, and the email-verification settings must match the intended flow. Account enablement is distinct from assigning application roles. A deployment without the listener cannot rely on this policy. Draft password/lifetime suggestions are not accepted by this ADR.

# Approval provenance

This is a proposed record of architecture observed in the cited source. The original approver, decision date and historical rationale were not established. Do not treat implemented behavior as approval or infer that the alternatives below were historically considered.
Acceptance requires an attributable record of the exact outcome and approver. This audit creates no accepted ADR and makes no application, realm, network, or tooling-policy change.

# Evidence and related guidance

Source revision inspected: 342ec668b7848fe0200a9c317812831ca546b885. Draft documents are evidence of design intent, not implemented behavior.

- [architecture/registration-approval-spi.md](/architecture/registration-approval-spi.md)
- [integrations/keycloak/realm-login-settings.md](/integrations/keycloak/realm-login-settings.md)
- [operations/verify-email-flows.md](/operations/verify-email-flows.md)
- [operations/troubleshoot-keycloak-email.md](/operations/troubleshoot-keycloak-email.md)

# Supersession

No prior ADR is superseded. Existing records keep their identifiers.
