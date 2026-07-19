# Security Remediation: App Auth Careful Pass

## Summary

This pass tightens application authorization and browser user data. It can affect local users unless Keycloak client roles are assigned correctly.

Status: planned

## Changes

- Stop merging realm roles and app client roles into one authorization list.
- Authorize admin/user routes only from `resource_access[WEB_KEYCLOAK_CLIENT_ID].roles`.
- Enforce `requireUserRoute` on user-area routes:
  - users dashboard
  - profile
  - settings
  - apps dashboard
  - todos
- Keep `requireAuthenticatedRoute` only for routes intentionally available to every signed-in account.
- Introduce a narrower browser-safe user projection for loader data.
- Avoid returning raw role provenance and stable subject identifiers unless a route explicitly needs them.
- Harden logout method/origin validation while preserving current Keycloak SSO logout behavior.
- Normalize callback token/JWKS verification failures and clear stale auth-attempt state.

## Development Compatibility

- Before enabling stricter route guards, assign the local test user the `Users` client role.
- Assign admin test users the `Admins` client role on the web client, not just a realm role.
- A realm role named `Admins` should no longer grant admin dashboard access.

## Verification

- `corepack pnpm --dir web typecheck`
- `corepack pnpm --dir web lint`
- `corepack pnpm --dir web build`
- Manual checks:
  - No-role user is denied from user-area routes.
  - `Users` client-role user can access user dashboard/profile/settings/apps/todos.
  - `Admins` client-role user can access admin dashboard and user routes.
  - Realm-only `Admins` does not grant admin dashboard access.
  - Logout rejects non-POST and cross-origin requests.
  - Callback failures route through sanitized recovery behavior.

## Assumptions

- Keycloak roles will be configured manually for local users before this pass is considered complete.
- Automated tests remain deferred.
