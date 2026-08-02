---
type: Integration
title: Mailpit SMTP settings
description: Draft Keycloak SMTP values for the implemented local Mailpit service.
tags: [mailpit, keycloak, smtp, email]
status: draft
generated: { by: codex/gpt-5, at: 2026-08-02T16:44:19Z }
stale_after: 2026-10-02
sources:
  - id: mailpit-compose
    resource: /local-mail-server/docker-compose.yml
    title: Mailpit Compose service
    last_modified: 2026-05-20
  - id: keycloak-compose
    resource: /auth-server/docker-compose.yml
    title: Containerized Keycloak service
    last_modified: 2026-05-22
---

# Local settings

Mailpit publishes SMTP on host port 1025 and its web inbox on `http://localhost:8025`; messages persist in the `admin-starter-mailpit_data` volume.[^mailpit-compose]

The migrated local setup used these values under Realm settings → Email:

```text
From: no-reply@admin-starter.local
From display name: Admin Starter
Reply to: no-reply@admin-starter.local
Host: host.docker.internal
Port: 1025
Encryption: None
Authentication: Off
```

Keycloak runs in a container, so `localhost` would mean the Keycloak container rather than the host-published SMTP service.[^keycloak-compose] Save the settings and use Test connection; the repository does not automate or verify the live realm's Email tab.

# Boundary

These are local capture settings only. No hosted SMTP provider, credential storage, delivery monitoring, or production mail policy is implemented.

# Related concepts

- [Verify email flows](/operations/verify-email-flows.md)
- [Troubleshoot Keycloak email](/operations/troubleshoot-keycloak-email.md)

[^mailpit-compose]: Mailpit Compose service

[^keycloak-compose]: Containerized Keycloak service
