# Security Remediation: Infrastructure Deferred Pass

## Summary

This pass handles the changes most likely to affect local setup, persisted Docker volumes, or provider compatibility. Do it after the safe and careful app passes.

Status: planned

## Changes

- Upgrade Keycloak runtime image and provider Maven dependencies to `26.6.2`.
- Rebuild and smoke test the disable-after-email-verify provider.
- Split Postgres credentials into separate Keycloak and web app users/databases with least-privilege grants.
- Provide a one-time migration or documented local reset path for existing Docker volumes.
- Add BFF session idle and absolute lifetimes.
- Enforce BFF expiry using `created_at` and `last_seen_at`.
- Add expired BFF session cleanup for encrypted token rows.
- Clear the browser session cookie when recoverable session failures delete server state.
- Bind local Postgres, Keycloak, and Mailpit ports to `127.0.0.1` by default.
- Disable Traefik insecure dashboard by default; if enabled locally, bind to localhost or protect it.
- Replace mutable image tags with fixed versions or digest pins where practical.
- Reject known placeholder/dev secret values for `WEB_SESSION_SECRET` and `WEB_TOKEN_ENCRYPTION_KEY`.

## Development Compatibility

- Existing Postgres volumes will not automatically apply new init SQL. Provide either:
  - a safe migration script for local volumes, or
  - explicit reset steps for disposable local environments.
- Update `.env.development`, `.env.example`, and `.env.traefik.example` together.
- Keep `start-app-containers` working after env changes.
- Document opt-in LAN exposure for device testing if localhost-bound ports are insufficient.

## Verification

- `corepack pnpm --dir web typecheck`
- `corepack pnpm --dir web lint`
- `corepack pnpm --dir web build`
- `corepack pnpm audit --prod`
- Rebuild Keycloak and web images.
- Manual checks:
  - Fresh local setup starts from an empty volume.
  - Existing local setup can be migrated or reset with documented steps.
  - Login/register/email verification still work on Keycloak 26.6.2.
  - disable-after-email-verify still marks and disables self-registered verified users.
  - Expired idle/absolute sessions redirect to login and clean stale state.

## Assumptions

- This pass may require a one-time local DB reset or migration.
- Full Keycloak upgrade smoke testing is required before considering this pass complete.
