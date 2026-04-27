# Infrastructure

Local dev services for the POC: Postgres (app + Keycloak data) and Keycloak.

## Configure

Env vars live at the project root. Copy the template and fill it in:

```bash
cp .env.example .env.development   # local dev
cp .env.example .env                # prod
```

`.env.development` is auto-loaded by Vite during `react-router dev`. Docker compose needs an explicit `--env-file` flag (below).

## Bring it up

Run from the project root:

```bash
# local dev
docker compose -f docker/docker-compose.yml --env-file .env.development up -d

# prod
docker compose -f docker/docker-compose.yml --env-file .env up -d
```

First boot takes ~30–60s while Keycloak initializes its schema.

## Verify

- **Postgres** — `docker exec -it app-postgres psql -U $POSTGRES_USER -d $POSTGRES_DB -c '\l'` should list both the app and `keycloak` databases.
- **Keycloak admin console** — http://localhost:8080 → sign in with the `KEYCLOAK_ADMIN_*` values from your env file.

## Tear down

```bash
docker compose -f docker/docker-compose.yml down       # keeps the volume
docker compose -f docker/docker-compose.yml down -v    # nukes the volume (fresh start)
```

## Notes

- `start-dev` is local-only — no TLS, relaxed hostname handling. Swap to `start` with proper `KEYCLOAK_HOSTNAME` and a reverse proxy before any non-local deployment.
- `KEYCLOAK_ADMIN_*` only applies on first boot. After that, manage the admin user through the console.
- Postgres and Keycloak share the same DB user (`POSTGRES_USER`); they just use separate databases on the same instance.
