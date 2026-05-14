# Admin Starter Keycloak

A React Router 7 framework-mode admin starter that uses Keycloak for identity
and a BFF-style server layer for web authentication.

## Architecture

This app is currently shaped as a browser app plus a small Backend For Frontend
(BFF) inside the React Router server:

```text
Browser
  -> React Router BFF
    -> Keycloak
```

The BFF is the trusted server-side layer for the web app. It handles the
browser-unfriendly auth work:

- redirects users to Keycloak for login and registration
- receives the OIDC callback
- exchanges the authorization code for tokens
- validates tokens with Keycloak JWKS
- stores a compact app user session in an HttpOnly cookie
- protects routes with server loaders

The browser does not read or store Keycloak tokens in `localStorage`.
The current proof of concept does not persist Keycloak tokens in the cookie
because browser cookies have small size limits. When the app needs to call a
FastAPI/resource server with Keycloak tokens, move token storage to a server-side
session table and keep only an opaque session id in the cookie.

Logout currently clears the local app session and returns to the splash page.
Full Keycloak SSO logout requires an `id_token_hint`; add server-side session
storage for the ID token before redirecting through Keycloak's end-session
endpoint.

Because local logout does not end the Keycloak SSO session, protected-route
redirects may silently sign the same Keycloak user back in. The visible Login
button uses `/auth/login?prompt=login` to force Keycloak to show the login
screen when you want to test credentials or switch users.

## Auth Flow

```text
1. Browser visits /auth/login
2. React Router loader redirects to Keycloak
3. User signs in with Keycloak
4. Keycloak redirects to /auth/callback
5. React Router server exchanges the code for tokens
6. React Router server sets an HttpOnly session cookie
7. User lands on /users/dashboard
```

Protected routes:

- `/users/dashboard` requires the `Users` or `Admins` Keycloak client role.
- `/users` redirects to `/users/dashboard`.
- `/admins/dashboard` requires the `Admins` Keycloak client role.
- `/admins` redirects to `/admins/dashboard`.
- `/forbidden` displays when a signed-in user lacks the required role.

Route modules are kept intentionally slim. They define `meta`, `loader`, and
redirect behavior, then render page components from `app/components/pages`.
Shared page wrappers live in `app/layouts`. Protected loaders call centralized
guards from `app/lib/route-guards.server.ts`.

Routes and access settings are centralized for reuse:

- `app/lib/app-settings.ts` owns app name/title, route paths, route patterns,
  route module paths, role names, and route access groups.
- `app/lib/auth-config.server.ts` owns server-only Keycloak/OIDC environment
  config and issuer URL helpers.
- `app/lib/auth-policy.ts` owns reusable role and access checks.
- `app/routes.ts` wires React Router from `appRoutePatterns` and
  `appRouteModules` instead of hardcoded route strings.

Auth routes:

- `/auth/login`
- `/auth/register`
- `/auth/callback`
- `/auth/logout`

## Future FastAPI Resource Server

If this proof of concept grows into a web + Expo mobile architecture, FastAPI
should own business APIs and authorization enforcement:

```text
React web
  -> React Router BFF
    -> FastAPI resource server

Expo mobile
  -> FastAPI resource server
```

React Router should stay focused on the web shell, secure-cookie session, and
web-specific auth bridge. FastAPI should validate Keycloak access tokens,
enforce roles and ownership, and read/write application data.

## Local Development

Copy the local environment template if needed:

```bash
cp .env.example .env.development
```

Important local values:

```env
KEYCLOAK_ISSUER=http://localhost:8080/realms/admin-starter
KEYCLOAK_CLIENT_ID=admin-starter-web
AUTH_REDIRECT_URI=http://localhost:5173/auth/callback
AUTH_POST_LOGIN_REDIRECT_URI=http://localhost:5173/users/dashboard
AUTH_POST_LOGOUT_REDIRECT_URI=http://localhost:5173
SESSION_SECRET=dev-admin-starter-keycloak-session-secret-change-me
```

Start Postgres, Keycloak, and the React Router dev server:

```bash
npm run dev
```

The dev script prints both local URLs:

```text
Frontend: http://localhost:5173
Keycloak: http://localhost:8080
```

## Keycloak Setup

See [docs/keycloak-setup.md](docs/keycloak-setup.md).

For production planning, deployment steps, and hardening checklist, see
[docs/production-deployment.md](docs/production-deployment.md).

Minimum local client requirements:

- Realm: `admin-starter`
- Client: `admin-starter-web`
- Valid redirect URI: `http://localhost:5173/auth/callback`
- Valid post logout redirect URI: `http://localhost:5173/*`
- Client roles:
  - `Admins`
  - `Users`

## Plans

Implementation plans are stored in `docs/plans/` before feature work starts.

Create a new plan:

```bash
npm run plan:new -- "keycloak auth splash users dashboard"
```

## Scripts

```bash
npm run dev          # start Docker services and React Router dev server
npm run typecheck    # generate route types and run TypeScript
npm run build        # production build
npm run start        # serve the production build
npm run docker:up    # start local Postgres and Keycloak
npm run docker:down  # stop local Docker services
npm run docker:logs  # follow Docker service logs
```
