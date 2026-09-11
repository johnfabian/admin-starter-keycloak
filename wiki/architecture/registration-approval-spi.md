---
type: Architecture
title: Registration approval SPI
description: Custom Keycloak listener that disables verified self-registered users pending admin approval.
resource: /auth-server/providers/disable-after-email-verify
tags: [keycloak, registration, email, java]
status: draft
generated: { by: codex/gpt-5, at: 2026-08-02T16:44:19Z }
stale_after: 2026-11-02
sources:
  - id: listener
    resource: /auth-server/providers/disable-after-email-verify/src/main/java/com/adminstarter/keycloak/events/DisableAfterEmailVerifyEventListenerProvider.java
    title: Registration event listener
    last_modified: 2026-05-22
  - id: factory
    resource: /auth-server/providers/disable-after-email-verify/src/main/java/com/adminstarter/keycloak/events/DisableAfterEmailVerifyEventListenerProviderFactory.java
    title: Event listener factory
    last_modified: 2026-05-22
  - id: image
    resource: /auth-server/Dockerfile
    title: Custom Keycloak image build
    last_modified: 2026-05-22
---

# Implemented behavior

The provider ID is `disable-after-email-verify`. On `REGISTER`, it marks the user with `self_registered=true`. On `VERIFY_EMAIL`, it replaces that marker with `awaiting_admin_approval=true`, disables an enabled user, and removes the user's sessions.[^listener][^factory]

Admin-created users are not marked by this flow. The JAR is built into the custom Keycloak image, but the running realm must also enable the listener under Realm settings → Events and enable email verification; the repository has no realm import that enforces either console setting.[^image]

# Operational signal

A verified self-registered user is expected to be disabled until an administrator enables the account. The app treats Keycloak's disabled-user token response as a fresh-login redirect, so repeated login presentation can be an approval-state symptom.

# Related concepts

- [Realm login settings](/integrations/keycloak/realm-login-settings.md)
- [Verify email flows](/operations/verify-email-flows.md)
- [Create an admin user](/operations/create-admin-user.md)

[^listener]: Registration event listener

[^factory]: Event listener factory

[^image]: Custom Keycloak image build

# Related decision records

These proposals record the decision and tradeoffs; this page retains the current behavior or operational procedure.

- [ADR-0007: Require administrator approval after self-registration verification (proposed)](/adr/ADR-0007-registration-approval.md)
