---
type: Runbook
title: Verify email flows
description: Manual verification order for local SMTP, email verification, registration, and password reset.
tags: [keycloak, mailpit, email, verification]
status: draft
generated: { by: codex/gpt-5, at: 2026-08-02T16:44:19Z }
stale_after: 2026-10-02
sources:
  - id: mailpit-compose
    resource: /local-mail-server/docker-compose.yml
    title: Local Mailpit service
    last_modified: 2026-05-20
  - id: registration-listener
    resource: /auth-server/providers/disable-after-email-verify/src/main/java/com/adminstarter/keycloak/events/DisableAfterEmailVerifyEventListenerProvider.java
    title: Registration approval listener
    last_modified: 2026-05-22
  - id: auth-routes
    resource: /web/app/lib/server/auth.server.ts
    title: Login and registration redirects
    last_modified: 2026-07-19
---

# Prerequisites

Start Mailpit with `corepack pnpm mail:up`, open `http://localhost:8025`, configure the realm's SMTP values, and pass Keycloak's Test connection. Confirm Verify email and Forgot password are enabled only as intended.

# Verification order

1. Create a disposable user with an email, Email verified off, and a known local password.
2. Use the user action Send verify email; open the Mailpit message and confirm the user becomes verified.
3. Reset the user and exercise login-driven verification. Use `/auth/login?prompt=login` to avoid reusing an existing SSO session.[^auth-routes]
4. If self-registration is enabled, register through `/auth/register`, follow the message, and confirm the user becomes disabled with `awaiting_admin_approval=true` when the custom listener is enabled.[^registration-listener]
5. Exercise Forgot password and confirm the new password completes login.

In gateway mode use `http://app.localhost`; Mailpit remains on host port 8025.[^mailpit-compose]

# Evidence

Record which mode, realm, disposable user, message type, final account state, and guarded route were verified. Do not record credentials, tokens, or message links.

# Related concepts

- [Mailpit SMTP settings](/integrations/mailpit-smtp-settings.md)
- [Troubleshoot Keycloak email](/operations/troubleshoot-keycloak-email.md)
- [Registration approval SPI](/architecture/registration-approval-spi.md)

[^mailpit-compose]: Local Mailpit service

[^registration-listener]: Registration approval listener

[^auth-routes]: Login and registration redirects
