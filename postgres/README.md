# Postgres

Shared local Postgres infrastructure for Keycloak and application services.

The Postgres boundary is separate from `auth-server/` so future services such
as `api-python/`, `api-express/`, and `api-dotnet/` can reuse the same local
Postgres instance without making Keycloak own application data.

## Direct Local Stack

```bash
corepack pnpm db:up
corepack pnpm db:logs
corepack pnpm db:down
```

Direct local Postgres listens on `localhost:5432` and uses the
`admin-starter-postgres` Docker network.

## Gateway Stack

```bash
corepack pnpm db:gateway:up
corepack pnpm db:gateway:logs
corepack pnpm db:gateway:down
```

Gateway Postgres uses the internal `admin-starter-postgres-gateway` Docker
network. Traefik does not expose Postgres.

## Databases

`postgres/init-keycloak-db.sql` creates the `keycloak` database on the first
Postgres boot. The default app database still comes from `POSTGRES_DB` in the
active root env file.
