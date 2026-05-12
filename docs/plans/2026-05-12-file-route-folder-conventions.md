# File Route Folder Conventions

Date: 2026-05-12

## Summary

Switch route configuration to React Router's file-route convention using
`@react-router/fs-routes`, and organize route modules as folders with
`route.tsx` files.

## Key Changes

- Install `@react-router/fs-routes`.
- Replace manual `route(...)` config with `flatRoutes()`.
- Move route modules into folder-style route modules.
- Rename dashboard URLs to:
  - `/users/dashboard`
  - `/admins/dashboard`
- Keep compatibility redirects:
  - `/users` redirects to `/users/dashboard`
  - `/admins` redirects to `/admins/dashboard`
- Update login defaults, links, docs, and README to use `/users/dashboard`.

## Public Interfaces / Config

- `AUTH_POST_LOGIN_REDIRECT_URI` should be `http://localhost:5173/users/dashboard`.
- Keycloak callback stays `http://localhost:5173/auth/callback`.

## Test Plan

- Run `npm run typecheck`.
- Verify `/` renders.
- Verify `/users` redirects to `/users/dashboard`.
- Verify `/admins` redirects to `/admins/dashboard`.
- Verify protected dashboard routes redirect anonymous users to login.

## Assumptions

- Use official `@react-router/fs-routes` folder route modules.
- Folder route names like `users.dashboard/route.tsx` intentionally map to
  `/users/dashboard`.

## Implementation Status

- Reverted in favor of explicit route config. See
  `2026-05-12-explicit-routes-with-route-guards.md`.
