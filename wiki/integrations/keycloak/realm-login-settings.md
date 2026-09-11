---
type: Integration
title: Realm login settings
description: Draft screen-level baseline for Keycloak login, email, password, and event settings.
tags: [keycloak, realm, login, email, security]
status: draft
generated: { by: codex/gpt-5, at: 2026-08-02T16:44:19Z }
stale_after: 2026-10-02
sources:
  - id: registration-route
    resource: /web/app/routes/auth-register.tsx
    title: Application registration redirect
    last_modified: 2026-05-12
  - id: listener
    resource: /auth-server/providers/disable-after-email-verify/src/main/java/com/adminstarter/keycloak/events/DisableAfterEmailVerifyEventListenerProvider.java
    title: Registration approval listener
    last_modified: 2026-05-22
  - id: mailpit
    resource: /local-mail-server/docker-compose.yml
    title: Local Mailpit service
    last_modified: 2026-05-20
---

# Draft baseline

For realm `admin-starter`, review these screens rather than assuming the live realm matches:

| Console area                              | Draft value                                | Repository coupling                                                |
| ----------------------------------------- | ------------------------------------------ | ------------------------------------------------------------------ |
| Login → User registration                 | On only when self-registration is intended | `/auth/register` redirects to Keycloak; there is no app-side form. |
| Login → Login with email                  | On                                         | Preserved setup convention; not enforced by code.                  |
| Login → Duplicate emails                  | Off                                        | Preserved setup convention; not enforced by code.                  |
| Login → Verify email                      | On when using approval flow                | The SPI reacts to `VERIFY_EMAIL`.                                  |
| Login → Forgot password                   | On after SMTP works                        | Requires outbound email.                                           |
| Login → Remember me                       | Off unless deliberately approved           | Changes session expectations.                                      |
| Security defenses → Brute force detection | On before exposure                         | Thresholds require an environment-specific decision.               |
| Events → Event listeners                  | Include `disable-after-email-verify`       | The JAR is inert until the realm enables it.                       |

The migrated documentation also proposed a minimum password length of 12, username/email exclusions, and password history of at least 3. These remain draft recommendations: no realm export or automated check verifies them.

# Verification

Inspect the actual realm, test SMTP, register a disposable user, verify the email, and confirm the approval listener transitions the account as documented.

# Related concepts

- [Registration approval SPI](/architecture/registration-approval-spi.md)
- [Mailpit SMTP settings](/integrations/mailpit-smtp-settings.md)
- [Verify email flows](/operations/verify-email-flows.md)

[^registration-route]: Application registration redirect

[^listener]: Registration approval listener

[^mailpit]: Local Mailpit service

# Related decision records

These proposals record the decision and tradeoffs; this page retains the current behavior or operational procedure.

- [ADR-0007: Require administrator approval after self-registration verification (proposed)](/adr/ADR-0007-registration-approval.md)
