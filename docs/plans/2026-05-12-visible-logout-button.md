# Visible Logout Button

Date: 2026-05-12

## Summary

Add an always-visible Logout button to the signed-in header so users do not have
to open the avatar menu or clear browser history.

## Key Changes

- Keep the avatar account dropdown.
- Add a visible `Logout` button linking to `/auth/logout` when authenticated.
- Keep anonymous header buttons unchanged.

## Test Plan

- Run `npm run check`.
- Verify authenticated header includes Logout.
- Verify `/auth/logout` still clears the app session.

## Assumptions

- A simple header button is enough for this pass.

## Implementation Status

- Completed
