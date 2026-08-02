# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

A pnpm monorepo admin starter. The only implemented app is `web/`, a React Router 7 framework-mode app that acts as its own Backend For Frontend (BFF) for Keycloak authentication. Other workspace folders (`api-express/`) are placeholders. Infrastructure (Postgres, Keycloak, Traefik, Mailpit) runs via Docker Compose files in `postgres/`, `auth-server/`, `api-gateway/`, and `local-mail-server/`.

- Never make code changes directly on `master`; use a feature branch.
- File naming: `.server.ts` (server-only), `.client.ts` (browser-only), `.shared.ts` (safe on both).
- SQL lives only in repository/data-access modules (`web/app/lib/server/data/`).
- Browser code must never see Keycloak access/refresh tokens; the React Router server is the BFF boundary.
- No inline executable scripts or `dangerouslySetInnerHTML`.
- Promote repeated, security-sensitive, protocol, header, storage-key, and config values to named constants or shared config.

## Commands

Run everything from the repo root with `corepack pnpm`. Root scripts wrap web commands with `dotenv -e .env.development`, which the web app requires — running `pnpm dev`/`typecheck` directly inside `web/` will miss env vars.

```bash
corepack pnpm install            # install workspace deps
corepack pnpm dev                # web dev server at http://localhost:5173 (containers must already be up)
corepack pnpm mail:up            # Mailpit SMTP inbox (http://localhost:8025)
corepack pnpm db:up              # shared Postgres (localhost:5434)
corepack pnpm auth:up            # Keycloak (http://localhost:8080; builds custom SPI provider)
corepack pnpm web:typecheck      # react-router typegen + tsc
corepack pnpm --dir web lint     # eslint
corepack pnpm format             # prettier --write
corepack pnpm check              # format:check + lint + typecheck (the full verification gate)
corepack pnpm web:build          # production build
corepack pnpm dev:gateway        # full Traefik gateway stack (uses .env.traefik); stop-gateway to tear down
corepack pnpm plan:new -- "name" # scaffold an implementation plan in specs/plans/
```

There is no test suite; `corepack pnpm check` is the verification command.

Local env lives in `.env.development` (template: `.env.example`; gateway mode: `.env.traefik.example`). Keycloak expects realm `admin-starter`, client `admin-starter-web`, and client roles `Admins` and `Users` — setup guides are in `docs/`.

`pnpm-workspace.yaml` enforces supply-chain hardening (`minimumReleaseAge` of 7 days, strict dep builds, blocked exotic subdeps). Installing a just-published package version will fail by design; see `docs/supply-chain-security.md` before relaxing anything.

## Architecture

### BFF auth flow (the core of the app)

Browser → React Router server (BFF) → Keycloak. The browser only ever holds an opaque HttpOnly session cookie. The BFF redirects to Keycloak for login/registration (PKCE), handles `/auth/callback`, exchanges the code for tokens, validates them against Keycloak JWKS, encrypts them, and stores them in the `web_bff_sessions` Postgres table. Access tokens are refreshed server-side before resource-server calls. Logout is a POST that clears the local session cookie even if downstream cleanup fails, then redirects through Keycloak end-session.

The server-side auth stack in `web/app/lib/server/`:

- `auth-config.server.ts` — server-only Keycloak/OIDC env config and issuer URL helpers
- `auth.server.ts` / `auth-request.server.ts` — core auth operations and request-level helpers (`requireUser`, `requireAnyRole`)
- `route-guards.server.ts` — centralized loader guards (`requireAuthenticatedRoute`, `requireAccessRoute`, `requireUserRoute`, `requireAdminRoute`); all protected loaders call these
- `oauth-pkce.server.ts` / `oauth-token.service.server.ts` — PKCE and token exchange/refresh
- `token-crypto.server.ts` — token encryption at rest
- `bff-session.service.server.ts` → `data/bff-session.repository.server.ts` → `data/database.server.ts` — session service, SQL repository, and the `postgres` client singleton
- `bff-fetch.server.ts` — authenticated fetch toward the (future) resource server

The `web_bff_sessions` schema is created by `postgres/init-app-schema.sql`, which only runs on first container boot (`docker-entrypoint-initdb.d`) — schema changes require recreating the Postgres volume or applying SQL manually.

### Route/config centralization

Route strings, role names, and page titles are never hardcoded. `web/app/lib/app-settings.shared.ts` is the single source of truth for app metadata, route paths/patterns/module paths, role names (`Admins`, `Users`), access groups (`appAccess`), and theme settings. `web/app/routes.ts` wires React Router entirely from `appRoutePatterns`/`appRouteModules`. `auth-policy.shared.ts` owns reusable role/access checks. When adding a route: add its path, pattern, and module to `app-settings.shared.ts`, then register it in `routes.ts`.

### Layered UI structure

Route modules in `web/app/routes/` are intentionally slim: `meta`, `loader` (calling a route guard), and a render of a page component. Pages live in `web/app/pages/`, shared layout wrappers in `web/app/layouts/`, reusable components in `web/app/components/` (with shadcn-style primitives under `components/ui/`). Route errors render the reusable error UI (`components/error-page.tsx`) — never raw text responses — and Keycloak/token/network failures are normalized before reaching the UI.

### Access model

- Every page in the signed-in shell — `/users/*`, `/profile`, `/settings`, `/apps/*` — requires the `Users` or `Admins` role (`requireUserRoute`); `/admins/*` requires `Admins` (`requireAdminRoute`). Authentication alone is never enough.
- Signed-in users lacking a role land on `/forbidden`.
- Roles are read from the access token as the union of realm roles and client roles under the web client id, and matched case-sensitively against `appRoles` — so a realm role named `Admins` grants admin access just as a client role does.
- Bare section paths (`/users`, `/admins`, `/apps`) redirect to their `/dashboard` pages.

### Keycloak customization

`auth-server/providers/disable-after-email-verify/` is a Java Keycloak SPI (event listener) built into the Keycloak image by `auth-server/Dockerfile` — `corepack pnpm auth:up` rebuilds it.
