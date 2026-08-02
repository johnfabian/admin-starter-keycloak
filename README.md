# Admin Starter Keycloak

A pnpm workspace with an implemented React Router 7 server-rendered web/BFF, local Keycloak identity, shared Postgres state, Mailpit email capture, and an optional local Traefik gateway.

## What exists

| Area                   | State                      | Evidence and limits                                                                                                                                                     |
| ---------------------- | -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| React Router web/BFF   | Implemented                | Authorization code + PKCE, server-side token validation/refresh, opaque HttpOnly cookie, encrypted Postgres session records, and loader-based role guards under `web/`. |
| Keycloak               | Implemented local service  | Direct and gateway Compose files build a Keycloak 26.0 image with the registration-approval SPI. The realm and client are configured manually; no realm import exists.  |
| Postgres               | Implemented local service  | One instance per mode stores both Keycloak and `web_bff_sessions`. Init SQL runs only for an empty volume; no migration framework exists.                               |
| Mailpit                | Implemented local service  | SMTP capture on port 1025 with the inbox at `http://localhost:8025`.                                                                                                    |
| Traefik                | Implemented for local HTTP | Routes `app.localhost` and `auth.localhost`; the dashboard is intentionally insecure at `http://localhost:8081`. No production TLS edge exists.                         |
| Express resource API   | Placeholder                | `api-express/` contains a README only: no manifest, source, runtime, Compose service, or tests.                                                                         |
| Automated tests and CI | Gap                        | No test runner, test files, or CI workflow is configured. The current gate is static only.                                                                              |
| Production deployment  | Gap                        | TLS, secret management, migrations, observability, health checks, scheduled/offsite backups, and a provider design are not implemented.                                 |

## Architecture

```text
Browser
  -> React Router BFF (web/)
       -> Keycloak (identity and OIDC)
       -> Postgres (opaque BFF sessions)

Keycloak
  -> Postgres (realm, clients, roles, and users)
```

The browser never receives Keycloak access or refresh tokens. The BFF performs the OIDC exchange, verifies tokens with the realm JWKS, stores encrypted token state in Postgres, refreshes server-side, and applies exact-case `Users`/`Admins` role guards. The future Express seam is not part of the running architecture.

## Repository map

```text
.agents/            canonical shared skills and scoped rule cards
.claude/            thin Claude discovery adapters
api-express/        documentation-only resource API placeholder
api-gateway/        local Traefik Compose configuration
auth-server/        Keycloak image, Compose files, and custom provider
local-mail-server/  Mailpit Compose configuration
postgres/           direct/gateway Postgres and first-boot SQL
scripts/            backup, restore, and repository automation
specs/plans/        dated implementation records
web/                React Router application and BFF
wiki/               draft, evidence-backed durable repository knowledge
```

## Quick start

Install from the repository root:

```bash
corepack pnpm install
```

For direct mode, copy `.env.example` to `.env.development`, replace the placeholder secrets, then run the package scripts in dependency order:

```bash
corepack pnpm mail:up
corepack pnpm db:up
corepack pnpm auth:up
corepack pnpm dev
```

Open the app at `http://localhost:5173` and Keycloak at `http://localhost:8080`. `dev` starts only the web development server. Stop Keycloak and Postgres with `corepack pnpm stop-app`; stop Mailpit separately with `corepack pnpm mail:down`.

For gateway mode, copy `.env.traefik.example` to `.env.traefik`, replace placeholders, then run:

```bash
corepack pnpm dev:gateway
corepack pnpm dev:gateway:down
```

Open `http://app.localhost`, `http://auth.localhost`, and the local Traefik dashboard at `http://localhost:8081`.

## Verification

```bash
corepack pnpm check
```

The gate runs repository-wide Prettier checking, web ESLint, React Router type generation, and TypeScript. It does not run unit, integration, browser, identity-flow, Compose, or CI checks because none are configured. Use `corepack pnpm web:build` when changing a build or server/client boundary, then exercise relevant runtime flows manually.

## Project knowledge and agent workflow

- [Wiki index](wiki/index.md) — retrieve only concepts relevant to the current task.
- [Shared skills](.agents.config/skills/) — typed procedural capabilities shared by Codex and Claude through discovery symlinks.
- [Scoped rule catalog](.agents.config/rules/index.md) — shared imperative rules selected by changed paths.
- [Local stack runbook](wiki/operations/local-stack.md) and [environment variables](wiki/operations/environment-variables.md).
- [Keycloak realm/client facts](wiki/integrations/keycloak/realm-and-client-facts.md), [email verification](wiki/operations/verify-email-flows.md), and [admin-user workflow](wiki/operations/create-admin-user.md).
- [Local backup](wiki/operations/local-backup.md), [restore drill](wiki/operations/backup-restore-drill.md), and [known production gaps](wiki/architecture/known-production-gaps.md).

All newly migrated wiki knowledge is draft and unverified until a human checks it against the running realm and intended operating model.

Agent-framework automation under skill-local `scripts/` is portable Python invoked through `uv`. Existing operational backup/restore runbooks remain POSIX shell scripts; JavaScript `.mjs` files are tool configuration only.
