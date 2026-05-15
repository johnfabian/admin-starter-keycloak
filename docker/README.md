# Infrastructure

Local dev services for the POC: Postgres (app + Keycloak data), Keycloak, and
an optional Traefik stack for testing host-based routing locally.

## Configure

Env vars live at the project root. Copy the template and fill it in:

```bash
cp .env.example .env.development   # local dev
cp .env.traefik.example .env.traefik # local Traefik
cp .env.example .env                # prod or platform env
```

`.env.development` is auto-loaded by Vite during `react-router dev`. Docker compose needs an explicit `--env-file` flag (below).

## Bring it up

Run from the project root:

```bash
# local dev
docker compose -f docker/docker-compose.yml --env-file .env.development up -d

# local Traefik test stack
docker compose -f docker/docker-compose.traefik.yml --env-file .env.traefik up -d --build --wait
```

First boot takes ~30–60s while Keycloak initializes its schema.

The Traefik stack routes through port 80:

- App: http://app.localhost
- Keycloak: http://auth.localhost
- Traefik dashboard: http://localhost:8081

Use the Traefik stack when you want local behavior to look like production:
browser requests enter through a reverse proxy, services are routed by host
name, Postgres is private, and Keycloak is not published directly on port 8080.

## Verify

- **Postgres** — `docker exec -it app-postgres psql -U $POSTGRES_USER -d $POSTGRES_DB -c '\l'` should list both the app and `keycloak` databases.
- **Keycloak admin console** — http://localhost:8080 → sign in with the `KEYCLOAK_ADMIN_*` values from your env file.
- **Traefik Keycloak admin console** — http://auth.localhost → sign in with
  the `KEYCLOAK_ADMIN_*` values from `.env.traefik`.

## Tear down

```bash
docker compose -f docker/docker-compose.yml down       # keeps the volume
docker compose -f docker/docker-compose.yml down -v    # nukes the volume (fresh start)

docker compose -f docker/docker-compose.traefik.yml --env-file .env.traefik down
docker compose -f docker/docker-compose.traefik.yml --env-file .env.traefik down -v
```

## Notes

- `start-dev` is local-only — no TLS, relaxed hostname handling. Swap to `start` with proper `KEYCLOAK_HOSTNAME` and a reverse proxy before any non-local deployment.
- `docker-compose.traefik.yml` uses Keycloak `start`, but keeps app
  `APP_NODE_ENV=development` by default so local HTTP auth cookies work.
  Set `APP_NODE_ENV=production` only when routing over HTTPS.
- `KEYCLOAK_ADMIN_*` only applies on first boot. After that, manage the admin user through the console.
- Postgres and Keycloak share the same DB user (`POSTGRES_USER`); they just use separate databases on the same instance.
