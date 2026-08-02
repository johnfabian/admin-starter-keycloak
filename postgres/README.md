# Postgres

Shared local Postgres infrastructure for Keycloak and application services.

The Postgres boundary is separate from `auth-server/` so future services such
as `api-express/` can reuse the same local Postgres instance without making
Keycloak own application data.

## Direct Local Stack

```bash
corepack pnpm db:up
corepack pnpm db:logs
corepack pnpm db:down
```

Direct local Postgres publishes `${POSTGRES_PORT:-5434}` on the host and uses
the `admin-starter-postgres` Docker network. Inside Docker it still listens on
`5432` — the published port is what `WEB_DATABASE_URL` connects to.

## Gateway Stack

Gateway Postgres has no dedicated up/down scripts; it comes up and goes down
with the rest of the gateway stack:

```bash
corepack pnpm dev:gateway
corepack pnpm db:gateway:logs
corepack pnpm stop-gateway
```

Gateway Postgres uses the internal `admin-starter-postgres-gateway` Docker
network and publishes no host port. Traefik does not expose Postgres.

## Databases

Both init scripts are mounted into `docker-entrypoint-initdb.d` and therefore
run **only on the first boot of an empty volume** — changing them afterwards
has no effect until the volume is recreated or the SQL is applied by hand.

- `postgres/init-keycloak-db.sql` creates the `keycloak` database, which
  Keycloak owns.
- `postgres/init-app-schema.sql` creates the `web_bff_sessions` table and its
  two indexes in the app database.

The app database name comes from `POSTGRES_DB` in the active root env file.
