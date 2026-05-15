# Force Keycloak Login Prompt

Date: 2026-05-12

## Summary

After local app logout, Keycloak SSO can still silently authenticate the user.
Add support for `prompt=login` so the app can force Keycloak to show the login
screen when the user clicks Login.

## Key Changes

- Allow `/auth/login?prompt=login` to forward `prompt=login` to Keycloak.
- Update anonymous Login links to use `/auth/login?prompt=login`.
- Keep protected-route redirects using normal `/auth/login` behavior so active
  SSO sessions remain convenient.
- Document the difference between local app logout and Keycloak SSO logout.

## Test Plan

- Run `npm run check`.
- Logout locally.
- Click Login and confirm Keycloak shows the login screen.
- Visit a protected route while Keycloak SSO is active and confirm it can still
  silently return to the app.

## Assumptions

- Full Keycloak SSO logout remains later work once server-side session storage
  can keep the ID token.

## Implementation Status

- Completed
