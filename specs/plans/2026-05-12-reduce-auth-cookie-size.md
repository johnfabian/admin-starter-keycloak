# Reduce Auth Cookie Size

Date: 2026-05-12

## Summary

Fix login failure caused by the cookie session exceeding browser size limits.
Store only the minimal authenticated user session in the HttpOnly cookie for
now, instead of storing Keycloak tokens.

## Key Changes

- Remove access token, ID token, refresh token, and expiry from cookie session
  storage.
- Keep token validation during `/auth/callback`.
- Store only the normalized `CurrentUser` object in the cookie.
- Keep logout clearing the local app session and redirecting to Keycloak logout
  without `id_token_hint`.
- Document that production token storage should move to a server-side session
  table when FastAPI/resource-server calls need tokens.

## Test Plan

- Run `npm run check`.
- Retry login and confirm the session cookie stays below browser limits.
- Verify `/users/dashboard` works after login.
- Verify logout clears the app session.

## Assumptions

- For the current login proof of concept, we only need user identity and roles
  in the app session.
- Token refresh and server-to-resource-server token forwarding are later work.

## Implementation Status

- Completed
