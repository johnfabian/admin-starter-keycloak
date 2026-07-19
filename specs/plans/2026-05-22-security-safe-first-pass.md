# Security Remediation: Safe First Pass

## Summary

This pass handles low-risk hardening that should not break existing Keycloak realm data, existing Postgres volumes, or local login flows.

Status: completed

Completed: 2026-05-22

Automated verification run:

- `corepack pnpm install --frozen-lockfile`
- `corepack pnpm audit --prod`
- `corepack pnpm audit --dev`
- `corepack pnpm --dir web typecheck`
- `corepack pnpm --dir web lint`
- `corepack pnpm --dir web build`

Manual local-stack login/logout smoke checks were not run during this pass.

## Changes

- Add `.env*` to `.dockerignore`, while preserving explicitly safe example files if needed.
- Fix the dev-only error preview route so production returns 404 before any authentication check.
- Add app-level security headers without inline scripts:
  - `Content-Security-Policy`
  - `Referrer-Policy`
  - `X-Content-Type-Options`
  - `Permissions-Policy`
  - production-only `Strict-Transport-Security`
- Add `Cache-Control: no-store` to auth callback/logout responses.
- Keep current Keycloak RP-initiated logout behavior and document `id_token_hint` as an intentional exception.
- Resolve the `qs` advisory by upgrading the dependency chain or using a verified pnpm override to `qs >= 6.15.2`.
- Remove or reduce direct remote avatar loading from the `picture` claim.
- Update stale docs/scripts references so command names match current `package.json`.

## Verification

- `corepack pnpm --dir web typecheck`
- `corepack pnpm --dir web lint`
- `corepack pnpm --dir web build`
- `corepack pnpm audit --prod`
- Manual checks:
  - Login still works.
  - Logout still reaches Keycloak logout and returns to the app.
  - Missing route and dev error previews still render clean error UI.
  - Production build does not expose dev-only error preview behavior.
  - Security headers are present on HTML and auth-sensitive responses.

## Assumptions

- No Keycloak version, realm, provider, or Postgres credential changes in this pass.
- No database reset or migration required.
