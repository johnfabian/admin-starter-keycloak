# Auth Server

Local Keycloak infrastructure for the admin starter.

Postgres is owned by `postgres/` because it is shared by Keycloak and the app
services.

## Configure

Env vars live at the project root:

```bash
cp .env.example .env.development
cp .env.traefik.example .env.traefik
```

## Direct Local Stack

Start the shared Postgres first, then Keycloak with direct host ports:

```bash
corepack pnpm db:up
corepack pnpm auth:up
```

Open:

```text
http://localhost:8080
```

Stop:

```bash
corepack pnpm auth:down
```

## Gateway Stack

Use this stack with `api-gateway/` and `web/docker-compose.gateway.yml` when
testing host-based routing through Traefik.

Start the full gateway mode from the repo root:

```bash
corepack pnpm dev:gateway
```

Open:

```text
http://app.localhost
http://auth.localhost
http://localhost:8081
```

Stop:

```bash
corepack pnpm dev:gateway:down
```

## Notes

- `docker-compose.yml` uses Keycloak `start-dev` for direct local development.
- `docker-compose.gateway.yml` uses Keycloak `start` with proxy headers for
  Traefik-style routing.
- `KEYCLOAK_ADMIN_*` only applies on first boot. After that, manage the admin
  user through the console.
- Keycloak connects to the shared Postgres container over the
  `admin-starter-postgres` or `admin-starter-postgres-gateway` Docker network.
