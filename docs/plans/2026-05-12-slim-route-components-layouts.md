# Slim Route Components And Layouts

Date: 2026-05-12

## Summary

Refactor route modules so they stay slim and delegate UI to reusable components.
Place reusable page components under `app/components/` and layout wrappers under
`app/layouts/`.

## Key Changes

- Add `app/layouts/app-layout.tsx` for pages that share the app header and base
  screen styling.
- Add page-level components under `app/components/pages/`.
- Keep route modules focused on `meta`, `loader`, redirects, and rendering the
  page component.
- Leave auth resource routes as slim server route modules.

## Test Plan

- Run `npm run typecheck`.
- Verify `/` still renders the splash page.
- Verify `/users/dashboard` and `/admins/dashboard` still protect anonymous
  users.
- Verify `/users` and `/admins` redirects still work.

## Assumptions

- `app/components/pages/` is acceptable for route-owned page components.
- `app/layouts/` is the shared home for layout wrappers.

## Implementation Status

- Completed
