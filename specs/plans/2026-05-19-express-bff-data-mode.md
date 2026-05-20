# Move React Router Framework Auth To A Same-Origin Express BFF

## Summary

Convert `web` from React Router framework mode to React Router data mode plus an Express/TypeScript BFF in the same `web` package. Express will serve the built React SPA and own all security-sensitive auth/session behavior under `/auth/*` and `/api/*`.

Target shape:

```text
Browser
  -> Express BFF on app origin
    -> serves React SPA
    -> owns HttpOnly session cookie
    -> talks to Keycloak
    -> later calls resource APIs with server-held tokens
```

The browser never stores Keycloak tokens, never calls Keycloak token endpoints, and never sends bearer tokens to APIs.

## Key Changes

- Replace React Router framework mode:
  - Remove server route loaders/actions from `web/app/routes/*.tsx`.
  - Replace `react-router.config.ts` and `@react-router/dev` build flow with Vite SPA build.
  - Use React Router data mode via `createBrowserRouter` / `RouterProvider`.
  - Keep current page components, layout, role helpers, route constants, and `CurrentUser` model where possible.

- Add Express BFF inside `web/server`:
  - `GET /auth/login?returnTo=&prompt=login` starts OIDC Authorization Code + PKCE.
  - `GET /auth/register` starts the same flow with `kc_action=register`.
  - `GET /auth/callback` validates state, exchanges code for tokens, verifies tokens with Keycloak JWKS, builds `CurrentUser`, stores session server-side, and redirects.
  - `POST /auth/logout` or `GET /auth/logout` clears the local BFF session; full Keycloak SSO logout is added only after storing `id_token`.
  - `GET /api/session` returns `{ user: CurrentUser | null }`.
  - `GET /api/session/required` returns `401` when unauthenticated.
  - `GET /api/access/users` and `GET /api/access/admins` return `200` or `403` for route guard checks.

- Store sessions securely:
  - Use an opaque HttpOnly cookie such as `__admin_starter_sid`.
  - Store Keycloak tokens and compact user data server-side, initially in Postgres because the repo already has Postgres.
  - Cookie settings: `httpOnly`, `sameSite=lax`, `secure` in HTTPS production, short idle/max lifetime aligned with Keycloak session policy.
  - Keep PKCE verifier, state, return URL, user, access token, refresh token, and optional ID token out of browser-readable storage.

- Update React route protection:
  - Root/home route fetches `/api/session`.
  - Protected dashboard routes use client-side loaders that call BFF guard endpoints.
  - `401` redirects browser to `/auth/login?returnTo=<current path>`.
  - `403` redirects to `/forbidden`.
  - Header login/register/logout links point to BFF auth routes; logout should prefer a form/button POST if CSRF protection is added immediately.

- Add BFF hardening:
  - Validate `returnTo` as same-origin relative paths only.
  - Add `helmet`.
  - Add CSRF protection for mutating `/api/*` and logout routes.
  - Rate-limit auth start/callback/logout endpoints lightly.
  - Disable caching on `/api/session` and auth responses.
  - Centralize role checks using the existing `Users` and `Admins` policy.

## Keycloak Changes

- Keep the same realm: `admin-starter`.
- Keep or convert `admin-starter-web` into a confidential web/BFF client:
  - Client authentication: `On`.
  - Standard flow: `On`.
  - PKCE: `S256`.
  - Implicit flow: `Off`.
  - Direct access grants: `Off`.
  - Valid redirect URI: `http://localhost:5173/auth/callback` for direct dev, or `http://app.localhost/auth/callback` for Traefik.
  - Valid post logout redirect URI: app origin only.
  - Web origins can be the app origin, but the SPA should not need Keycloak CORS for token calls.
- Keep web client roles:
  - `admin-starter-web:Users`
  - `admin-starter-web:Admins`
- Add API audience scopes only when the BFF needs to call downstream resource APIs with the user's access token.
- Keep groups assigning roles; do not hard-code Keycloak group names in React or Express.

## Build And Dev

- `web` package scripts become roughly:
  - `dev`: run Vite client dev server plus Express BFF dev server, with Vite proxying app traffic or Express proxying Vite assets.
  - `build`: `vite build` for SPA plus `tsc`/bundler build for Express server.
  - `start`: run compiled Express server, serving `web/dist`.
  - `typecheck`: TypeScript check for both client and server.
- Update Dockerfile so the production container runs Express, not `react-router-serve`.
- Update Traefik labels to route `app.localhost` to the Express server port.
- Leave `api-express` as the future standalone Express resource server placeholder; the BFF belongs to the web app because it owns browser sessions.

## Test Plan

- Auth flow:
  - Anonymous user can open `/`.
  - Login redirects to Keycloak and returns to `/users/dashboard`.
  - `returnTo` preserves safe in-app paths and rejects external URLs.
  - Register link sends `kc_action=register`.
  - Logout clears the local BFF session.

- Route protection:
  - Anonymous user visiting `/users/dashboard` is redirected to login.
  - User with `Users` can access `/users/dashboard`.
  - User without `Admins` gets `/forbidden` for `/admins/dashboard`.
  - User with `Admins` can access admin dashboard.

- Security checks:
  - Browser storage contains no Keycloak tokens.
  - Session cookie is HttpOnly and SameSite.
  - `/api/session` returns only compact user data, not tokens.
  - Callback rejects missing/invalid state and missing PKCE verifier.
  - Token verification validates issuer, signature, expiration, and expected client/audience where applicable.

## Assumptions

- Use same-origin Express as selected.
- Use Postgres-backed server sessions instead of cookie-only sessions.
- Keep Keycloak as the only login/register/password UI.
- Keep authorization based on Keycloak client roles, not groups.
- Keep full Keycloak SSO logout as a follow-up unless the BFF stores `id_token` from day one.
