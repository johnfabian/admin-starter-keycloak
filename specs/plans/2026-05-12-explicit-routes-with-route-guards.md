# Explicit Routes With Route Guards

Date: 2026-05-12

## Summary

Revert from folder route modules to explicit route configuration while keeping
the extracted page components. Add a centralized route guard helper so route
permissions are checked consistently from loaders.

## Key Changes

- Replace `flatRoutes()` with explicit `index(...)` and `route(...)` entries.
- Remove `@react-router/fs-routes`.
- Move route modules back to regular files under `app/routes/`.
- Keep page UI under `app/components/pages/` and layout wrappers under
  `app/layouts/`.
- Add a centralized route guard helper for authenticated and role-protected
  routes.
- Preserve URLs:
  - `/`
  - `/users`
  - `/users/dashboard`
  - `/admins`
  - `/admins/dashboard`
  - `/auth/login`
  - `/auth/register`
  - `/auth/callback`
  - `/auth/logout`
  - `/forbidden`

## Test Plan

- Run `npm run typecheck`.
- Verify `/` returns 200.
- Verify `/users` redirects to `/users/dashboard`.
- Verify `/admins` redirects to `/admins/dashboard`.
- Verify `/users/dashboard` redirects anonymous users to login.
- Verify `/admins/dashboard` redirects anonymous users to login.

## Assumptions

- “Middleware” means a centralized guard function used by route loaders for now.
- True framework-level middleware can be added later if React Router middleware
  is enabled for this app.

## Implementation Status

- Completed
