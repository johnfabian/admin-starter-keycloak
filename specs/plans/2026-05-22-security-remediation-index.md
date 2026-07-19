# Security Remediation Implementation Index

## Summary

Use this index to implement remediation work in small batches without committing the full audit report. Each batch has its own plan and status. Keep the Keycloak `id_token_hint` logout behavior as a documented exception for now, with header/logging mitigations, because preserving full Keycloak SSO logout is preferable for this MVP.

## Implementation Order

1. `2026-05-22-security-safe-first-pass.md`
   - Status: completed
   - Low-risk code/config/docs hardening that should not reset Keycloak or Postgres.
   - Completed 2026-05-22 with frozen install, prod/dev audits, typecheck, lint, and build.

2. `2026-05-22-security-app-auth-careful-pass.md`
   - Status: planned
   - App authorization and browser data changes that may require assigning local Keycloak roles.

3. `2026-05-22-security-infra-deferred-pass.md`
   - Status: planned
   - Runtime, Keycloak upgrade, Postgres credential split, and session lifecycle work that can affect local setup.

## Documented Exception

- Keep RP-initiated Keycloak logout with `id_token_hint` for now.
- Mitigate with HTTPS-only production, `Referrer-Policy`, auth-response `Cache-Control: no-store`, minimized ID token claims, and docs instructing operators not to log full query strings.
- Revisit local-only or back-channel logout after MVP.

## Completion Rule

After each pass is implemented and verified, update its status from `planned` to `completed` and add a short dated note with checks run. After all three passes are complete, run a fresh audit and create a new sanitized result summary.
