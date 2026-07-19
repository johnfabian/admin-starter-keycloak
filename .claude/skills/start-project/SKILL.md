---
name: start-project
description: Start the full local dev stack for this repo — Docker containers (Mailpit, Postgres, Keycloak) followed by the web dev server. User-invoked only via /start-project.
disable-model-invocation: true
---

# Start the project

Bring up the local dev stack in dependency order: containers first, then the
frontend (the web app needs Postgres and Keycloak to be reachable). All
commands run from the repo root — the root scripts inject `.env.development`
via dotenv, which the web app requires.

## 1. Preflight

- Run `docker info`. If it fails, Docker Desktop isn't running — tell the user
  to start it, then stop here. Nothing else can proceed without it.
- Confirm `.env.development` exists at the repo root. If it's missing, point
  the user at `.env.example` as the template and stop.

## 2. Start the containers

Run these in order. Each is idempotent (safe if already running) and uses
`--wait`, so it returns only once the container is healthy:

```bash
corepack pnpm mail:up    # Mailpit SMTP inbox
corepack pnpm db:up      # Postgres on localhost:5434
corepack pnpm auth:up    # Keycloak on localhost:8080
```

`auth:up` builds the custom Keycloak SPI provider image, so the first run can
take several minutes — use a generous timeout (10 minutes) and don't assume
it's hung. If any of these fail, show the error and check logs with the
matching script (`corepack pnpm auth:logs`, `mail:logs`, or
`docker compose -f postgres/docker-compose.yml logs`), then stop — starting
the frontend without its containers just produces confusing runtime errors.

## 3. Start the frontend

Run `corepack pnpm dev` from the repo root **in the background** (it's a
long-running dev server; running it in the foreground would block the
session). Don't run it inside `web/` directly — that skips the dotenv wrapper
and the app starts without its env vars.

## 4. Verify and report

Poll `http://localhost:5173` until it responds (a few retries over ~15
seconds), and check the dev-server output for startup errors. Then report the
running stack to the user:

| Service  | URL                    |
| -------- | ---------------------- |
| Web app  | http://localhost:5173  |
| Keycloak | http://localhost:8080  |
| Mailpit  | http://localhost:8025  |
| Postgres | localhost:5434         |

If the web app doesn't come up, report what the dev-server output shows — the
most common causes are a port already in use (an earlier `pnpm dev` still
running) or missing values in `.env.development`.
