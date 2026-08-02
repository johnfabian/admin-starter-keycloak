---
type: Runbook
title: Create an admin user
description: Manual local workflow for creating a realm user and assigning implemented application access.
tags: [keycloak, users, roles, administration]
status: draft
generated: { by: codex/gpt-5, at: 2026-08-02T16:44:19Z }
stale_after: 2026-10-02
sources:
  - id: access-settings
    resource: /web/app/lib/app-settings.shared.ts
    title: Implemented application roles
    last_modified: 2026-05-22
  - id: keycloak-compose
    resource: /auth-server/docker-compose.yml
    title: Keycloak bootstrap admin configuration
    last_modified: 2026-05-22
---

# Procedure

In the `admin-starter` realm:

1. Open Users → Create new user and provide the local user's identity fields.
2. For an administrator-created local account, set Email verified deliberately and create a non-temporary password when a forced change is not being tested.
3. Open Role mapping → Assign role.
4. Assign exact-case `Admins` for admin and user areas, or `Users` for user areas only.[^access-settings]
5. Sign in through the app and verify `/users/dashboard`; verify `/admins/dashboard` only for `Admins`.

Groups may carry these roles, but the app consumes role claims rather than group names. If the user reaches `/forbidden`, inspect the emitted realm and `admin-starter-web` client roles and confirm exact spelling.

# Bootstrap boundary

`KEYCLOAK_ADMIN_USER` and `KEYCLOAK_ADMIN_PASSWORD` bootstrap Keycloak itself when the database is initialized; they are not the application user's role mapping workflow.[^keycloak-compose] Changing the environment values later does not document or verify the live realm administrator state.

# Related concepts

- [Access control model](/architecture/access-control-model.md)
- [Registration approval SPI](/architecture/registration-approval-spi.md)

[^access-settings]: Implemented application roles

[^keycloak-compose]: Keycloak bootstrap admin configuration
