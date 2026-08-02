---
name: stop-project
description: Stop this repository's local React Router development server and Docker development containers while preserving database volumes. Use only when the user asks to stop the project.
---

# Stop the project

1. Stop the background dev-server task created by the current session. Otherwise inspect the process listening on port `5173`; stop it only after confirming it is the repository's Node/Vite process.
2. Run `corepack pnpm stop-app` from the repository root.
3. Run `docker ps --filter name=app- --format "{{.Names}}"` and report remaining project containers.
4. State that normal shutdown preserves Postgres/Keycloak Docker volumes.

If Docker Desktop is unavailable, report that container teardown could not be verified. Never stop an unrelated process based on the port number alone.
