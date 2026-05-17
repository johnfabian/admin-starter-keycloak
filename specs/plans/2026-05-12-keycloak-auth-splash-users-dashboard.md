# Keycloak Auth, Splash, Admins Route, And Users Dashboard

Date: 2026-05-12

## Summary

Implement server-side Keycloak login with an HttpOnly session cookie, a polished
splash page, protected `/admins`, and a default authenticated `/users` dashboard
that displays the logged-in user's first and last name.

## Key Changes

- Add plan archiving with `specs/plans/`, `scripts/create-plan.mjs`, and
  `npm run plan:new -- "plan title"`.
- Add React Router framework-mode auth routes for login, registration,
  callback, and logout.
- Store auth state in an HttpOnly cookie and keep tokens out of browser
  JavaScript storage.
- Add auth helpers for current user loading, authenticated route protection, and
  `Admins` role checks.
- Replace the starter welcome screen with a splash page and auth-aware header.
- Add `/users` as the post-login dashboard and `/admins` as an admin-only
  dashboard placeholder.

## Public Interfaces / Config

- Add env vars for Keycloak issuer/client settings, auth callback URLs, and
  `SESSION_SECRET`.
- Update Keycloak documentation with `/auth/callback`, `/users` post-login
  behavior, and the `Admins` / `Users` role model.
- Read client roles from `resource_access["admin-starter-web"].roles`.

## Test Plan

- Confirm this plan exists before implementation.
- Run `npm run typecheck`.
- Verify logged-out `/` shows the splash page with Login and Register.
- Verify login redirects through Keycloak and lands on `/users`.
- Verify `/users` displays first and last name.
- Verify `/admins` redirects anonymous users to login.
- Verify `/admins` shows forbidden for non-admin users and dashboard for
  `Admins`.
- Verify logout clears the app session and returns to `/`.

## Assumptions

- Use `/users` as the default authenticated dashboard route.
- Use `/admins` as the protected Admin dashboard route.
- Register uses Keycloak registration.
- Navigation/sidebar comes later.
- Use server-side OIDC with secure cookie-based session, not SPA token storage.

## Implementation Status

- Completed
