---
name: start-project
description: Start this repository's local development stack in dependency order, verify the containers and React Router development server, and report service URLs. Use only when the user asks to start the project.
disable-model-invocation: true
---

# Start the project

Run from the repository root.

1. Run `docker info` and confirm `.env.development` exists without displaying its contents. Stop if either precondition fails.
2. Run `corepack pnpm mail:up`, `corepack pnpm db:up`, and `corepack pnpm auth:up` in order. Allow up to ten minutes for the first Keycloak image build.
3. Start `corepack pnpm dev` as a background process; the root script supplies required environment values.
4. Poll `http://localhost:5173` and inspect server output for errors.
5. Report Web `http://localhost:5173`, Keycloak `http://localhost:8080`, Mailpit `http://localhost:8025`, and Postgres `localhost:5434`.

If a dependency fails, inspect its matching logs and stop before starting dependents. Never print secrets from environment files.
