---
name: stop-project
description: Stop the local dev stack for this repo — shut down the web dev server, then tear down the Docker containers (Keycloak, Postgres, Mailpit). User-invoked only via /stop-project.
disable-model-invocation: true
---

# Stop the project

Tear down the local dev stack in reverse dependency order: frontend first,
then containers. Postgres data lives in a Docker volume, so stopping the
containers doesn't lose sessions or Keycloak realm config — say so in the
final report so the user isn't left wondering.

## 1. Stop the frontend dev server

If this session started the dev server as a background task, stop that task
directly. Otherwise, find whatever is listening on port 5173:

```powershell
Get-NetTCPConnection -LocalPort 5173 -State Listen -ErrorAction SilentlyContinue |
  Select-Object -ExpandProperty OwningProcess -Unique
```

Look up each PID with `Get-Process -Id <pid>` before killing anything — only
stop it if it's a `node` process (the Vite dev server). Port 5173 could in
principle be held by something else, and killing an unrelated process would
be worse than leaving the server running. If nothing is listening, the dev
server is already down; just note that and move on.

## 2. Tear down the containers

```bash
corepack pnpm stop-app
```

This runs `docker compose down` for Keycloak, Postgres, and Mailpit in turn.
It's safe if some or all containers are already stopped. If Docker Desktop
isn't running, there's nothing to tear down — report that and finish.

## 3. Verify and report

Confirm the app containers are gone:

```powershell
docker ps --filter name=app- --format "{{.Names}}"
```

Expect empty output (`app-keycloak`, `app-postgres`, `app-mailpit` all
stopped). Then report what was stopped, note anything that was already down,
and remind the user that Postgres/Keycloak data persists in Docker volumes —
`/start-project` brings everything back where they left it.
