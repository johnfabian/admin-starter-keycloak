# Admin Starter Keycloak

A pnpm monorepo admin starter. The current implemented app is a React Router 7
framework-mode web app that uses Keycloak for identity and a BFF-style server
layer for web authentication.

## Repository Layout

```text
postgres/      Shared Postgres Compose files
auth-server/   Keycloak Compose files
api-gateway/   Traefik Compose file
local-mail-server/  Mailpit local SMTP inbox Compose file
api-express/   Express API placeholder (next service to build)
web/           React Router web app
docs/          setup guides and runbooks
specs/plans/   implementation plans
scripts/       shared automation
```

## Architecture

This app is currently shaped as a browser app plus a small Backend For Frontend
(BFF) inside the React Router server:

```text
Browser
  -> React Router BFF
    -> Keycloak
    -> future resource server
```

The BFF is the trusted server-side layer for the web app. It handles the
browser-unfriendly auth work:

- redirects users to Keycloak for login and registration
- receives the OIDC callback
- exchanges the authorization code for tokens
- validates tokens with Keycloak JWKS
- stores an opaque session id in an HttpOnly cookie
- stores encrypted Keycloak tokens in the server-side Postgres session table
- refreshes access tokens server-side before resource server calls
- protects routes with server loaders

The browser does not read or store Keycloak tokens in `localStorage`, loader
JSON, or non-HttpOnly cookies. Logout is a POST action that clears the local BFF
session and redirects through Keycloak's end-session endpoint when an ID token
hint is available. That `id_token_hint` is an intentional OIDC logout exception:
it is sent only to Keycloak over the logout redirect and should be protected in
production with HTTPS, no-store auth responses, a strict referrer policy, and
proxy logging that avoids full query strings.

## Auth Flow

```text
1. Browser visits /auth/login
2. React Router loader redirects to Keycloak
3. User signs in with Keycloak
4. Keycloak redirects to /auth/callback
5. React Router server exchanges the code for tokens
6. React Router server stores tokens in Postgres and sets an HttpOnly session cookie
7. User lands on /users/dashboard
```

Access model:

- The splash page (`/`) is the only app page an unauthenticated visitor can
  reach. The `/auth/*` routes are necessarily public too, since login has to be
  reachable.
- Everything in the signed-in shell — `/users/*`, `/profile`, `/settings`,
  `/apps/*` — requires the `Users` role. Being signed in is not enough.
- `/admins/*` requires the `Admins` role.
- `Admins` reaches every route, because it is included in both access groups
  (`appAccess` in `app-settings.shared.ts`).
- `/users`, `/admins`, and `/apps` redirect to their `/dashboard` pages.
- `/forbidden` displays when a signed-in user lacks the required role.
- Roles are the union of realm roles and client roles under the web client id,
  compared case-sensitively — a realm role named `Admins` works exactly like the
  client role of the same name.

Route modules are kept intentionally slim. They define `meta`, `loader`, and
redirect behavior, then render page components from `web/app/pages`.
Shared page wrappers live in `web/app/layouts`. Protected loaders call
centralized guards from `web/app/lib/server/route-guards.server.ts`.

Routes and access settings are centralized for reuse:

- `web/app/lib/app-settings.shared.ts` owns app name/title, route paths, route patterns,
  route module paths, role names, and route access groups.
- `web/app/lib/server/auth-config.server.ts` owns server-only Keycloak/OIDC
  environment config and issuer URL helpers.
- `web/app/lib/auth-policy.shared.ts` owns reusable role and access checks.
- `web/app/routes.ts` wires React Router from `appRoutePatterns` and
  `appRouteModules` instead of hardcoded route strings.

Auth routes:

- `/auth/login`
- `/auth/register`
- `/auth/callback`
- `/auth/account`
- `/auth/logout`

## Future Express Resource Server

`api-express/` is the next service to build. Once it exists, it should own
business APIs and authorization enforcement:

```text
React web
  -> React Router BFF
    -> Express resource server
```

React Router stays focused on the web shell, secure-cookie session, and the
web-specific auth bridge. Express validates Keycloak access tokens, enforces
roles and ownership, and reads/writes application data. `bff-fetch.server.ts`
is the seam that will call it.

## Local Development

Copy the local environment template if needed:

```bash
cp .env.example .env.development
```

Important local values:

```env
KEYCLOAK_ISSUER=http://localhost:8080/realms/admin-starter
WEB_KEYCLOAK_CLIENT_ID=admin-starter-web
WEB_AUTH_REDIRECT_URI=http://localhost:5173/auth/callback
WEB_AUTH_POST_LOGIN_REDIRECT_URI=http://localhost:5173/users/dashboard
WEB_AUTH_POST_LOGOUT_REDIRECT_URI=http://localhost:5173
WEB_SESSION_SECRET=
WEB_DATABASE_URL=postgresql://app:app@localhost:5434/admin_starter
WEB_TOKEN_ENCRYPTION_KEY=
WEB_RESOURCE_SERVER_BASE_URL=
WEB_KEYCLOAK_API_AUDIENCE=
WEB_TOKEN_REFRESH_LEEWAY_SECONDS=60
WEB_SESSION_LAST_SEEN_UPDATE_SECONDS=300
```

`.env.example` ships `WEB_SESSION_SECRET` and `WEB_TOKEN_ENCRYPTION_KEY` empty
and you must fill both in. Each needs **at least 32 characters** or the server
throws on startup. If any required value is missing entirely the app does not
error — it silently behaves as though nobody is signed in, which is the most
confusing failure mode in local setup. Generate them with:

```bash
node -e "console.log(require('crypto').randomBytes(32).toString('base64url'))"
```

Env names are intentionally scoped for multiple clients:

- `WEB_*` values belong to the React Router web/BFF client.
- `API_*` values belong to the future Express resource server.
- `KEYCLOAK_*` values without a web or API prefix are shared Keycloak realm or
  server settings.

Install dependencies:

```bash
corepack pnpm install
```

Start the containers, then the dev server. `corepack pnpm dev` runs
`react-router dev` only — it does not start Docker, and the web app needs
Postgres and Keycloak reachable before it will work:

```bash
corepack pnpm mail:up   # Mailpit  — http://localhost:8025
corepack pnpm db:up     # Postgres — localhost:5434
corepack pnpm auth:up   # Keycloak — http://localhost:8080
corepack pnpm dev       # Web app  — http://localhost:5173
```

`auth:up` builds the custom Keycloak SPI image, so the first run takes several
minutes. `/start-project` runs this whole sequence for you.

## Keycloak Setup

See [docs/keycloak-setup.md](docs/keycloak-setup.md).

For local SMTP, email verification, and forgot-password testing, see
[docs/keycloak-email-verification.md](docs/keycloak-email-verification.md).

For production planning, deployment steps, and hardening checklist, see
[docs/production-deployment.md](docs/production-deployment.md).

For dependency install hardening and pnpm supply-chain settings, see
[docs/supply-chain-security.md](docs/supply-chain-security.md).

API-specific Keycloak and Traefik setup instructions live in each API folder:

- [api-express/README.md](api-express/README.md)
- [api-gateway/README.md](api-gateway/README.md)

Minimum local client requirements:

- Realm: `admin-starter`
- Client: `admin-starter-web`
- Valid redirect URI: `http://localhost:5173/auth/callback`
- Valid post logout redirect URI: `http://localhost:5173/*`
- Client roles:
  - `Admins`
  - `Users`

## Plans

Implementation plans are stored in `specs/plans/` before feature work starts.

Create a new plan:

```bash
corepack pnpm plan:new -- "keycloak auth splash users dashboard"
```

## Scripts

```bash
corepack pnpm dev               # web dev server only (containers must already be up)
corepack pnpm check             # format:check + lint + typecheck — the verification gate
corepack pnpm format            # prettier --write
corepack pnpm dev:gateway       # start Mailpit, Traefik, gateway Postgres, auth, and web
corepack pnpm stop-gateway      # tear the gateway stack down
corepack pnpm web:typecheck     # generate route types and run TypeScript
corepack pnpm web:build         # production web build
corepack pnpm web:start         # serve the production web build
corepack pnpm mail:up           # start local Mailpit SMTP inbox
corepack pnpm mail:down         # stop local Mailpit SMTP inbox
corepack pnpm mail:logs         # follow local Mailpit logs
corepack pnpm db:up             # start local shared Postgres
corepack pnpm db:down           # stop local shared Postgres
corepack pnpm db:logs           # follow local Postgres logs
corepack pnpm auth:up           # start local Keycloak
corepack pnpm auth:down         # stop local Keycloak
corepack pnpm auth:logs         # follow local auth service logs
corepack pnpm gateway:up        # start Traefik only
corepack pnpm stop-app          # stop auth, Postgres, and Mailpit
corepack pnpm plan:new -- "name" # scaffold a plan in specs/plans/
./backup-all                    # run local backup scripts
```
