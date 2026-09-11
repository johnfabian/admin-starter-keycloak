---
type: Decision
title: "ADR-0008: Use realm-local credentials for routine application administration"
description: Proposed decision record extracted from current wiki and source evidence.
tags: [adr, architecture]
adr_id: ADR-0008
decision_status: proposed
status: draft
generated: { by: "codex/gpt-6", at: "2026-09-11T20:32:36Z" }
stale_after: 2026-12-11
sources:
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

# Decision proposal

Use a separately configured realm-local administrator for this application's routine automation, with the authentication realm configured independently from the target realm. Load the target from the explicitly selected environment configuration, keep credentials out of logs and Git, and preserve master configuration. Treat persistent administrators separately from run-owned test accounts.

# Alternatives for review

Master credentials for routine work or a narrower delegated role/service-account design are alternatives. The current realm-admin grant is realm-scoped but broad within that realm; this proposal does not claim least privilege within the realm.

# Consequences and limits

The reusable helper still supports other explicitly configured administrative realms and defaults to master when the admin realm is omitted. Isolation therefore depends on the selected credentials and permissions, not a universal helper prohibition. Initial bootstrap and later role changes are separate operations. No live credentials or privileges were inspected or changed in this audit.

# Approval provenance

The user requested realm-local administration in this conversation. The proposal captures that boundary without fabricating a durable approval URL; live realm state was not reverified during this documentation audit.
Acceptance requires an attributable record of the exact outcome and approver. This audit creates no accepted ADR and makes no application, realm, network, or tooling-policy change.

# Evidence and related guidance

Source revision inspected: 342ec668b7848fe0200a9c317812831ca546b885. Draft documents are evidence of design intent, not implemented behavior.

- [operations/keycloak-cli.md](/operations/keycloak-cli.md)

# Supersession

No prior ADR is superseded. Existing records keep their identifiers.
