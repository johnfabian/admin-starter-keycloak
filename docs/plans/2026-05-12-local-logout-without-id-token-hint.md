# Local Logout Without Id Token Hint

Date: 2026-05-12

## Summary

Fix logout when Keycloak requires `id_token_hint` but the app no longer stores
tokens in the cookie. For the current proof of concept, logout should clear the
local app session and return to the splash page without redirecting through
Keycloak.

## Key Changes

- Update `/auth/logout` to destroy the local app session cookie.
- Redirect to `AUTH_POST_LOGOUT_REDIRECT_URI`.
- Do not call Keycloak's end-session endpoint until server-side token/session
  storage is added.
- Document that full SSO logout needs the ID token stored server-side.

## Test Plan

- Run `npm run check`.
- Sign in, click Logout, and confirm the app returns to `/`.
- Confirm `/users/dashboard` redirects to login after logout.

## Assumptions

- Local app logout is acceptable for this proof of concept.
- Full Keycloak SSO logout will be revisited with server-side session storage.

## Implementation Status

- Completed
