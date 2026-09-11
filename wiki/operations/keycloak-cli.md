---
type: Runbook
title: Keycloak administration CLI
description: Use the reusable helper to inspect and administer an explicitly selected local realm.
tags: [automation]
status: draft
generated: { by: "codex/gpt-6", at: "2026-09-11T15:57:51Z" }
stale_after: 2026-12-11
sources:
  - id: implementation
    resource: /.agents-config/skills/ops/keycloak-admin/scripts/keycloak.py
    title: Implemented automation
    last_modified: 2026-09-11
---

# Configuration and transport

The keycloak-admin skill uses the bundled kcadm CLI in the selected container. The target realm comes
from KEYCLOAK_ISSUER; KEYCLOAK_REALM must agree if present. KEYCLOAK_ADMIN_REALM selects where the
administrator authenticates and defaults to master. KEYCLOAK_ADMIN_CONTAINER selects the local container.
KEYCLOAK_ADMIN_URL is the administration endpoint visible inside that container, independent of the browser issuer.

Prefer a dedicated administrator inside the application realm, with only the needed realm-management
permissions. Set KEYCLOAK_AUTOMATION_USER and KEYCLOAK_AUTOMATION_PASSWORD together and set
KEYCLOAK_ADMIN_REALM to that realm. Partial dedicated credentials fail without bootstrap fallback.
The original KEYCLOAK_ADMIN_USER/PASSWORD remain reserved for Docker bootstrap or explicitly selected
initial administration. Realm-local realm-management/realm-admin grants management of its own realm,
not master. Persistent administrators are not test fixtures and must never enter fixture cleanup journals.
See [dedicated realm administration](https://www.keycloak.org/docs/latest/server_admin/#_per_realm_admin_permissions).

Use an absolute --env-file path. The helper consumes values in-process and suppresses raw CLI output.
Admin passwords travel through standard input into a child-only environment variable in container mode;
temporary authentication state is isolated and removed. Local executable mode requires an absolute CLI
path and KEYCLOAK_CLI_VERSION; Windows batch distributions should use container mode.

# Inspect and repair

Run the skill helper's doctor command before test provisioning. It checks client settings, exact-case
Users/Admins role availability, role mappers, registration/email/reset configuration and the custom listener.
A missing prerequisite produces a proposed repair; no existing configuration is reconciled automatically.
The profile must explicitly declare automation_run_id, self_registered and awaiting_admin_approval
with view/edit permissions restricted to admin. This preserves fixture ownership and lets the existing
approval provider expose its state to administration without letting users forge those attributes.
Keep existing profile fields and unmanaged-attribute policy unchanged when adding these declarations.
The approval listener must be present in eventsListeners alongside any existing listeners.
Bootstrap environment variables may no longer match an existing administrator. Rejected credentials
require correcting the selected file; never reset an administrator as a troubleshooting shortcut.

# Fixtures

Provisioning clears direct role assignments only on verified run-owned fixture accounts before assigning
the requested application role. This isolates the no-role matrix even when realm defaults grant Users.
Self-registration retains those defaults; approval only enables the account.

The fixture workflow journals random run-specific account names and IDs in an access-restricted local
manifest. Creation, role verification, registration adoption, approval and cleanup all use that ownership.
New fixtures use their unique synthetic email as username, including in email-as-username realms. Legacy exact-name recovery journals remain supported. Passwords never appear in stdout. Retain the exact manifest after interruption and invoke the root
browser runner's --cleanup path to coordinate Keycloak, BFF and Mailpit cleanup.

[Keycloak Admin CLI reference](https://www.keycloak.org/docs/latest/server_admin/#admin-cli).
The repository image currently uses Keycloak 26.0; verify version applicability before changing commands.

# Related decision records

These accepted ADRs record the decisions and tradeoffs; this page retains the current behavior or operational procedure.

- [ADR-0008: Use realm-local credentials for routine application administration (accepted)](/adr/ADR-0008-realm-scoped-automation-administration.md)
