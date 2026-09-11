---
type: Test Strategy
title: Automated local verification
description: Run reproducible Chromium characterization against the existing local realm.
tags: [automation]
status: draft
generated: { by: "codex/gpt-6", at: "2026-09-11T15:57:51Z" }
stale_after: 2026-12-11
sources:
  - id: implementation
    resource: /scripts/e2e.py
    title: Implemented automation
    last_modified: 2026-09-11
---

# Commands and prerequisites

Run corepack pnpm agent:setup with an absolute environment path once per worktree.
test:fast runs formatting, web lint/type checking, Python tooling tests, and browser-test type checking.
test:e2e runs Chromium; test:e2e:ui opens the same suite interactively. verify:story adds the production
build, graph checks, and two consecutive browser runs. Hosted CI is not configured.

The direct local Keycloak, Postgres and Mailpit services must be available. The runner checks realm
configuration without repairing it, then provisions no-role, Users, Admins, logout, reset and registration
fixtures. The selected application port must be free. Tests run serially with fresh browser contexts.
No human browser baseline is required before automated characterization.
When administrator access is unavailable, test:e2e -- --public-only runs only anonymous
checks without authenticating an administrator or creating users. Its result is explicitly partial.

# Baseline mapping

The source checklist is the preserved local `APP-STABILITY-PILOT` manual baseline at
revision `dcd23a16a3a3365ce37320f515a240881af5648f` (2026-08-13). The rows below map each
observation; mapping indicates implemented coverage, not a claim that signed-in checks passed.
Test paths are relative to `tests/browser/specs/`.

| Original checklist row             | Assertion or explicit limitation                                                                                                                                                                                                        |
| ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Docker engine                      | CLI/container access is exercised by Keycloak preflight; Docker version is not asserted.                                                                                                                                                |
| Direct dependency startup          | Runner requires existing services and checks realm configuration; startup ordering and container health metadata are not tested.                                                                                                        |
| Web startup                        | Runner starts its own strict-port server and polls its ownership nonce before Chromium starts.                                                                                                                                          |
| Static/build baseline              | test:fast checks formatting, lint and types; verify:story adds production build.                                                                                                                                                        |
| Anonymous public response          | auth.spec.ts public splash checks visible sign-in content; CSP and nosniff headers are not asserted by this suite.                                                                                                                      |
| Protected-route initiation         | auth.spec.ts anonymous route loop reaches the Keycloak username field for every protected route.                                                                                                                                        |
| Explicit login initiation          | auth.spec.ts checks prompt=login and the visible password field; no-store header is not asserted.                                                                                                                                       |
| Registration initiation            | registration.spec.ts follows the Register entry through real self-registration; no-store header is not asserted.                                                                                                                        |
| Anonymous logout boundary          | auth.spec.ts rejects cross-origin POST; anonymous GET/same-origin POST redirect and cache headers remain an automation limitation.                                                                                                      |
| Public error responses             | auth.spec.ts asserts 404 status, not-found text, forbidden explanation and absence of diagnostic patterns.                                                                                                                              |
| Browser automation availability    | Locked Playwright Chromium is installed by agent:setup and exercised by test:e2e.                                                                                                                                                       |
| Anonymous home                     | auth.spec.ts public splash visibility; subjective visual appearance remains unverified.                                                                                                                                                 |
| Explicit login                     | auth.spec.ts prompt=login and password field; existing-SSO reuse itself is not independently characterized.                                                                                                                             |
| Registration                       | registration.spec.ts real registration, Mailpit verification, pending approval and subsequent login.                                                                                                                                    |
| Callback                           | auth.spec.ts callback preserves the requested profile URL after real login.                                                                                                                                                             |
| No-role account                    | auth.spec.ts noRole authorization matrix denies every protected route.                                                                                                                                                                  |
| Users account                      | auth.spec.ts users matrix allows user routes and denies admin routes.                                                                                                                                                                   |
| Admins account                     | auth.spec.ts admins matrix allows both sets of routes.                                                                                                                                                                                  |
| Protected-route redirect           | Anonymous route loop plus successful profile return assertion; unsafe external initiation stays on the configured identity origin.                                                                                                      |
| Logout                             | Dedicated logout account: real menu action, Keycloak return, removed BFF cookie.                                                                                                                                                        |
| Post-logout protection             | The same logout test requires the Keycloak username field on the next protected navigation.                                                                                                                                             |
| Session continuity                 | auth.spec.ts reload/navigation retains visible account controls.                                                                                                                                                                        |
| Browser token boundary             | auth.spec.ts scans browser storage, readable cookies, DOM and app response bodies for JWT/token fields, and asserts HttpOnly/SameSite on the session cookie. This is bounded leak detection, not proof against every possible encoding. |
| /users — Users or Admins           | Authorization matrices assert redirect to /users/dashboard.                                                                                                                                                                             |
| /users/dashboard — Users or Admins | Authorization matrices assert final URL and visible main content.                                                                                                                                                                       |
| /profile — Users or Admins         | Authorization matrices assert final URL and visible main content.                                                                                                                                                                       |
| /settings — Users or Admins        | Authorization matrices assert final URL and visible main content.                                                                                                                                                                       |
| /apps — Users or Admins            | Authorization matrices assert redirect to /apps/dashboard.                                                                                                                                                                              |
| /apps/dashboard — Users or Admins  | Authorization matrices assert final URL and visible main content.                                                                                                                                                                       |
| /apps/todos — Users or Admins      | Authorization matrices assert final URL and visible main content.                                                                                                                                                                       |
| /admins — Admins                   | Admins matrix asserts redirect to /admins/dashboard.                                                                                                                                                                                    |
| /admins/dashboard — Users          | Users matrix asserts forbidden redirect.                                                                                                                                                                                                |
| /admins/dashboard — Admins         | Admins matrix asserts final URL and visible main content.                                                                                                                                                                               |
| Desktop navigation                 | ui.spec.ts sidebar toggle, account menu and theme controls; logout exercised separately.                                                                                                                                                |
| Mobile navigation                  | ui.spec.ts drawer viewport, Profile navigation and no horizontal overflow; subjective readability remains unverified.                                                                                                                   |
| Theme controls                     | ui.spec.ts light/dark toggle persists on reload, Purple accent survives navigation/reload, system mode responds to device preference.                                                                                                   |
| Keyboard operation                 | ui.spec.ts Enter opens account menu, Escape restores focus, Tab moves focus; exhaustive keyboard traversal remains a limitation.                                                                                                        |
| Focus visibility                   | ui.spec.ts focused control has geometry and outline/shadow; subjective contrast and every focus state are not proven.                                                                                                                   |
| Error pages                        | auth.spec.ts public errors and authenticated development 500 preview check sanitized content; subjective actionable design remains unverified.                                                                                          |

# Evidence and limitations

Reports contain test titles, outcomes and durations; raw network traces, cookies, passwords, email links
and CLI diagnostics are suppressed. App-only failure screenshots use synthetic accounts and remain ignored.
Subjective design quality and complete accessibility are not proven by browser assertions or axe.
Existing application defects must be reported separately rather than silently changing expected behavior.

Cleanup verifies fixture ownership, removes only their BFF sessions and exact-recipient email messages,
and removes only run-owned Keycloak users. An interrupted/failed cleanup retains the recovery manifest.
Use test:e2e -- --cleanup <absolute-manifest> to retry under the shared stack lock.

[Playwright authentication](https://playwright.dev/docs/auth) explains browser-state isolation.
