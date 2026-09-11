---
name: keycloak-admin
description: Inspect and administer a configured Keycloak realm through its Admin CLI, and provision owned accounts for browser tests. Use for Keycloak configuration, users, roles, sessions, and test fixtures.
---

# Keycloak administration

Use `scripts/keycloak.py` for realm-scoped Admin CLI requests and fixture lifecycle operations. Select the environment file by explicit absolute path. The helper may consume the required secret values; never display the file, credentials, raw CLI output, temporary CLI config, or fixture manifest.

The skill is available for automatic discovery. Discovery does not authorize changing a realm: apply only the administration action or test-fixture work already requested by the user. Read operations and prerequisite inspection can proceed within that scope. Test setup must not repair realm/client policy or reset existing administrator credentials.

1. Read [the interface reference](references/interface.md) for configuration and JSON examples. Use `uv run scripts/keycloak.py --env-file <absolute-path> doctor` before fixtures.
2. Prefer the configured container's bundled `/opt/keycloak/bin/kcadm.sh`; it matches the server distribution. For local executable mode, configure its exact version and let the helper compare it with authenticated server information. Windows batch CLI launchers are intentionally excluded; use container mode on Windows.
3. Review the selected realm/client and doctor repair suggestions. The administrator authentication realm is independent of the target realm derived from the issuer. The helper rejects a contradictory realm override and arbitrary flags or cross-realm endpoints.
4. Pass request JSON through subprocess stdin, using argument arrays and no shell. Administrator passwords cross into Docker over stdin and are exported only inside the CLI process by a fixed shell bridge. Local executable mode uses a child-only environment variable. Mutation payloads use stdin; no secret belongs in command arguments. For normal inspection, CLI output has a small allowlist of non-secret fields. Trusted Python callers can inspect full returned JSON in memory and must redact before any output.
5. For browser testing, create a fresh protected manifest, retain it across failure, and use only its generated synthetic accounts. Serialize the shared stack outside this helper. Register the reserved browser account, immediately adopt its exact username/email, and keep its recorded ID for cleanup. Approval is restricted to the owned, email-verified disabled account awaiting approval.
6. Cleanup verifies all ownership records before deleting, rechecks each immediately before deletion, and journals each success. It removes only those Keycloak accounts; the runner separately removes their BFF sessions and exact test-email IDs. Keep the manifest until all services report cleanup complete. Missing or changed ownership stops cleanup; never broaden deletion to a prefix search.

Do not attach secret manifests or raw traces to issues. Record sanitized outcomes and tool/version applicability. Credentials in this development workflow remain available to the same OS user and Docker administrators; filesystem permissions are not isolation from those principals.

Authoritative behavior: [Keycloak Admin CLI](https://www.keycloak.org/docs/latest/server_admin/#admin-cli). The password environment variable and advertised stdin interface are documented in the [Keycloak 26.0 CLI implementation](https://github.com/keycloak/keycloak/blob/26.0.0/integration/client-cli/admin-cli/src/main/java/org/keycloak/client/cli/common/BaseConfigCredentialsCmd.java). The container image requires a console for its advertised interactive password prompt, so the helper uses the supported `KC_CLI_PASSWORD` environment variable through the protected bridge. The repository currently builds its bundled CLI/server from the Keycloak 26.0 image.
