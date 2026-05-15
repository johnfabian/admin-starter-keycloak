# Monorepo Reorganization With API Gateway Boundary

Date: 2026-05-15

## Summary

Reorganize the repo into a pnpm monorepo with clear service boundaries:

```text
postgres/      shared Postgres
auth-server/   Keycloak
api-gateway/   Traefik only
web/           React Router app
api-python/    placeholder for FastAPI
mobile/        placeholder for Expo
docs/          user-facing docs and runbooks
specs/plans/   implementation plans
scripts/       shared repo automation
```

Root scripts should orchestrate auth, gateway, and web. Real env files stay at
the repo root.

## Key Changes

- Convert to pnpm workspaces:
  - Add `pnpm-workspace.yaml` with `web`, `api-python`, and `mobile`.
  - Make root `package.json` orchestration-only.
  - Move current app dependencies and app scripts into `web/package.json`.
  - Replace `bun.lock` with `pnpm-lock.yaml`.

- Move the React Router app into `web/`:
  - Move `app/`, `public/`, `Dockerfile`, `vite.config.ts`,
    `react-router.config.ts`, `tsconfig.json`, and web-specific lint/format
    config into `web/`.
  - Preserve `~/* -> ./app/*` relative to `web/`.
  - Update the web Dockerfile so it builds from the `web/` package context.

- Split infrastructure by ownership:
  - `postgres/docker-compose.yml`: direct local shared Postgres stack.
  - `postgres/docker-compose.gateway.yml`: shared Postgres for Traefik mode.
  - `auth-server/docker-compose.yml`: direct local Keycloak stack.
  - `auth-server/docker-compose.gateway.yml`: Keycloak for Traefik mode, with
    Traefik labels and no direct Keycloak host port.
  - `api-gateway/docker-compose.yml`: Traefik only, with Docker provider,
    ports `80` and `8081`, and shared public network.
  - `web/docker-compose.gateway.yml`: web container behind Traefik with labels
    for `app.localhost`.

- Use a shared gateway network:
  - Network name: `admin-starter-public`.
  - `api-gateway` creates/owns the network.
  - `auth-server` and `web` gateway Compose files attach to it as external.
  - `Postgres` owns a separate internal Postgres network for Keycloak and API
    services.
  - Traefik labels use `traefik.docker.network=admin-starter-public`.

- Keep root env files:
  - `.env.development`
  - `.env.traefik`
  - `.env.example`
  - `.env.traefik.example`

- Add root orchestration scripts:
  - `dev`: start default auth stack, then run `web` dev server.
  - `web:dev`, `web:build`, `web:start`, `web:typecheck`, `web:lint`.
  - `db:up`, `db:down`, `db:logs`.
  - `auth:up`, `auth:down`, `auth:logs`.
  - `gateway:up`, `gateway:down`, `gateway:logs`.
  - `dev:gateway`: start Traefik, gateway-mode auth, and gateway-mode web.

- Preserve automation and planning structure:
  - Keep `./backup-all` at repo root.
  - Update backup/restore scripts to use `postgres/docker-compose*.yml`.
  - Keep implementation plans in `specs/plans/`.
  - Keep setup docs, runbooks, and architecture docs in `docs/`.

## Public Interfaces / Config

- Root command names become the stable developer interface:
  - `pnpm dev`
  - `pnpm web:build`
  - `pnpm auth:up`
  - `pnpm db:up`
  - `pnpm dev:gateway`
  - `./backup-all`
- Local URLs remain unchanged:
  - direct dev web: `http://localhost:5173`
  - direct Keycloak: `http://localhost:8080`
  - gateway web: `http://app.localhost`
  - gateway Keycloak: `http://auth.localhost`
  - Traefik dashboard: `http://localhost:8081`

## Test Plan

- Install dependencies with `pnpm install`.
- Run web checks:
  - `pnpm web:typecheck`
  - `pnpm web:build`
  - `pnpm web:lint`
- Run default local dev:
  - `pnpm dev`
  - confirm Keycloak opens at `http://localhost:8080`.
  - confirm web opens at `http://localhost:5173`.
  - confirm login/callback still works.
- Run gateway dev:
  - `pnpm dev:gateway`
  - confirm `http://app.localhost`, `http://auth.localhost`, and
    `http://localhost:8081`.
- Run backup smoke test:
  - `./backup-all`
  - confirm timestamped backup files are created.
- Search for stale paths:
  - no remaining `docker/docker-compose.yml`.
  - no remaining `docker/docker-compose.traefik.yml`.
  - no root-level React Router config assumptions.

## Assumptions

- Use pnpm workspaces.
- Use `api-gateway/` for Traefik only.
- Use `postgres/` for shared Postgres only.
- Use `auth-server/` for Keycloak only.
- Keep env files at repo root.
- Add only placeholder `api-python/` and `mobile/` directories for now.
- Do not add a VS Code workspace file as part of this implementation.

## Implementation Status

- Implemented on 2026-05-15.
