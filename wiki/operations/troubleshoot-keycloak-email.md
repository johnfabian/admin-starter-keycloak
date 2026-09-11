---
type: Runbook
title: Troubleshoot Keycloak email
description: Evidence order for local SMTP failures, missing mail, wrong links, and approval-state confusion.
tags: [keycloak, mailpit, email, troubleshooting]
status: draft
generated: { by: codex/gpt-5, at: 2026-08-02T16:44:19Z }
stale_after: 2026-10-02
sources:
  - id: mailpit-compose
    resource: /local-mail-server/docker-compose.yml
    title: Mailpit ports and container
    last_modified: 2026-05-20
  - id: root-scripts
    resource: /package.json
    title: Keycloak and mail log commands
    last_modified: 2026-08-01
  - id: gateway-keycloak
    resource: /auth-server/docker-compose.gateway.yml
    title: Keycloak external URL and proxy settings
    last_modified: 2026-05-22
---

# Test connection fails

Check that Mailpit is running, SMTP uses port 1025 rather than the 8025 web UI, encryption and authentication are off for local capture, and the Keycloak Email host is `host.docker.internal` rather than container-local `localhost`.[^mailpit-compose]

# Connection succeeds but mail is missing

Confirm the `admin-starter` realm was selected, the user has an email, and the requested action is still applicable. Inspect `corepack pnpm mail:logs`, plus `corepack pnpm auth:logs` for direct mode or `corepack pnpm auth:gateway:logs` for gateway mode.[^root-scripts]

# Link points at the wrong host

Direct Keycloak uses `KEYCLOAK_HOSTNAME`; gateway Keycloak uses `KEYCLOAK_EXTERNAL_URL` with `KC_PROXY_HEADERS=xforwarded`.[^gateway-keycloak] Align the environment with the running mode and restart Keycloak.

# User cannot sign in after verification

Inspect the user's Enabled state and `awaiting_admin_approval` attribute before treating this as SMTP failure. The registration approval listener intentionally disables verified self-registered users.

# Related concepts

- [Mailpit SMTP settings](/integrations/mailpit-smtp-settings.md)
- [Environment variables](/operations/environment-variables.md)
- [Registration approval SPI](/architecture/registration-approval-spi.md)

[^mailpit-compose]: Mailpit ports and container

[^root-scripts]: Keycloak and mail log commands

[^gateway-keycloak]: Keycloak external URL and proxy settings

# Related decision records

These proposals record the decision and tradeoffs; this page retains the current behavior or operational procedure.

- [ADR-0007: Require administrator approval after self-registration verification (proposed)](/adr/ADR-0007-registration-approval.md)
