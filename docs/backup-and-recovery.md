# Backup And Recovery

This guide explains how to back up and recover the local and production
infrastructure for this project, with special attention to Keycloak.

## What Must Be Backed Up

Back up these things:

- Keycloak Postgres database
- application Postgres database
- Keycloak realm export snapshots
- production `.env` or platform secret values
- Traefik ACME certificate storage in production
- Terraform state if Terraform is used
- deployed image tags and release notes

Do not rely on the Keycloak container itself as a backup. Containers are
replaceable. The important state lives in Postgres and in secret/configuration
systems.

## Current Local Storage

The default local Docker stack uses:

```text
Compose file: docker/docker-compose.yml
Postgres container: app-postgres
Keycloak container: app-keycloak
Docker volume: admin-starter-keycloak_postgres_data
App database: admin_starter
Keycloak database: keycloak
```

The local Traefik stack uses:

```text
Compose file: docker/docker-compose.traefik.yml
Postgres container: app-traefik-postgres
Keycloak container: app-traefik-keycloak
Docker volume: admin-starter-keycloak-traefik_postgres_traefik_data
App database: admin_starter
Keycloak database: keycloak
```

Manual Keycloak admin-console changes are stored in the `keycloak` database
inside the relevant Postgres volume. They are not stored in Git.

`docker compose down` keeps named volumes. `docker compose down -v` removes
named volumes and can delete local Keycloak settings and users.

## Local Backup Directory

Create a local backup directory:

```bash
mkdir -p ./backups/postgres ./backups/keycloak ./backups/realm-export
```

This repo ignores local backup files:

```gitignore
/backups/
```

Backups can contain user data, password hashes, client secrets, and other
sensitive information. Do not commit them to Git.

## Local Postgres Backup

### Default Stack

Back up the Keycloak database:

```bash
docker exec app-postgres pg_dump -U postgres -d keycloak -F c -f /tmp/keycloak.dump
docker cp app-postgres:/tmp/keycloak.dump ./backups/postgres/keycloak.dump
docker exec app-postgres rm /tmp/keycloak.dump
```

Back up the app database:

```bash
docker exec app-postgres pg_dump -U postgres -d admin_starter -F c -f /tmp/admin_starter.dump
docker cp app-postgres:/tmp/admin_starter.dump ./backups/postgres/admin_starter.dump
docker exec app-postgres rm /tmp/admin_starter.dump
```

Back up all databases in SQL form:

```bash
docker exec app-postgres pg_dumpall -U postgres -f /tmp/all-databases.sql
docker cp app-postgres:/tmp/all-databases.sql ./backups/postgres/all-databases.sql
docker exec app-postgres rm /tmp/all-databases.sql
```

### Traefik Stack

Back up the Keycloak database:

```bash
docker exec app-traefik-postgres pg_dump -U postgres -d keycloak -F c -f /tmp/keycloak-traefik.dump
docker cp app-traefik-postgres:/tmp/keycloak-traefik.dump ./backups/postgres/keycloak-traefik.dump
docker exec app-traefik-postgres rm /tmp/keycloak-traefik.dump
```

Back up the app database:

```bash
docker exec app-traefik-postgres pg_dump -U postgres -d admin_starter -F c -f /tmp/admin_starter-traefik.dump
docker cp app-traefik-postgres:/tmp/admin_starter-traefik.dump ./backups/postgres/admin_starter-traefik.dump
docker exec app-traefik-postgres rm /tmp/admin_starter-traefik.dump
```

Back up all databases in SQL form:

```bash
docker exec app-traefik-postgres pg_dumpall -U postgres -f /tmp/all-databases-traefik.sql
docker cp app-traefik-postgres:/tmp/all-databases-traefik.sql ./backups/postgres/all-databases-traefik.sql
docker exec app-traefik-postgres rm /tmp/all-databases-traefik.sql
```

## Local Restore

Restore into a fresh local stack only after you understand which volume will be
overwritten.

### Default Stack Restore

Stop services:

```bash
docker compose -f docker/docker-compose.yml --env-file .env.development down
```

Reset the local volume:

```bash
docker compose -f docker/docker-compose.yml --env-file .env.development down -v
```

Start Postgres:

```bash
docker compose -f docker/docker-compose.yml --env-file .env.development up -d postgres
```

Copy and restore the Keycloak database:

```bash
docker cp ./backups/postgres/keycloak.dump app-postgres:/tmp/keycloak.dump
docker exec app-postgres dropdb -U postgres --if-exists keycloak
docker exec app-postgres createdb -U postgres keycloak
docker exec app-postgres pg_restore -U postgres -d keycloak --clean --if-exists /tmp/keycloak.dump
docker exec app-postgres rm /tmp/keycloak.dump
```

Copy and restore the app database:

```bash
docker cp ./backups/postgres/admin_starter.dump app-postgres:/tmp/admin_starter.dump
docker exec app-postgres dropdb -U postgres --if-exists admin_starter
docker exec app-postgres createdb -U postgres admin_starter
docker exec app-postgres pg_restore -U postgres -d admin_starter --clean --if-exists /tmp/admin_starter.dump
docker exec app-postgres rm /tmp/admin_starter.dump
```

Start the full stack:

```bash
docker compose -f docker/docker-compose.yml --env-file .env.development up -d --wait
```

### Traefik Stack Restore

Stop and reset:

```bash
docker compose -f docker/docker-compose.traefik.yml --env-file .env.traefik down -v
```

Start Postgres:

```bash
docker compose -f docker/docker-compose.traefik.yml --env-file .env.traefik up -d postgres
```

Restore the Keycloak database:

```bash
docker cp ./backups/postgres/keycloak-traefik.dump app-traefik-postgres:/tmp/keycloak-traefik.dump
docker exec app-traefik-postgres dropdb -U postgres --if-exists keycloak
docker exec app-traefik-postgres createdb -U postgres keycloak
docker exec app-traefik-postgres pg_restore -U postgres -d keycloak --clean --if-exists /tmp/keycloak-traefik.dump
docker exec app-traefik-postgres rm /tmp/keycloak-traefik.dump
```

Restore the app database:

```bash
docker cp ./backups/postgres/admin_starter-traefik.dump app-traefik-postgres:/tmp/admin_starter-traefik.dump
docker exec app-traefik-postgres dropdb -U postgres --if-exists admin_starter
docker exec app-traefik-postgres createdb -U postgres admin_starter
docker exec app-traefik-postgres pg_restore -U postgres -d admin_starter --clean --if-exists /tmp/admin_starter-traefik.dump
docker exec app-traefik-postgres rm /tmp/admin_starter-traefik.dump
```

Start the full stack:

```bash
docker compose -f docker/docker-compose.traefik.yml --env-file .env.traefik up -d --build --wait
```

## Keycloak Realm Export Snapshot

Realm exports are useful snapshots and migration aids, but they are not a full
backup. Keycloak's official docs note that import/export has limitations:

- consistency is not guaranteed unless Keycloak nodes are stopped first
- exported data does not include user/admin events
- exported data does not include persisted sessions
- exported data does not include workflow state
- exported data does not include revoked tokens
- Admin Console partial export masks sensitive values and does not export users

Use database backups for recovery. Use realm exports for review, reference, and
recreating configuration.

### Admin Console Partial Export

In Keycloak:

1. Select the `admin-starter` realm.
2. Open **Realm settings**.
3. Use the action menu.
4. Choose **Partial export**.
5. Export clients, roles, groups, and realm settings.
6. Save the file under `backups/realm-export/`.

Do not commit the export unless it has been reviewed and sanitized.

### CLI Export

For a more complete export, stop Keycloak and run a CLI export against the
database. The exact command depends on how the container is launched and where
the export directory is mounted.

General Keycloak command shape:

```bash
/opt/keycloak/bin/kc.sh export --dir /opt/keycloak/data/export --realm admin-starter --users different_files
```

For production, run exports in a maintenance window or from a dedicated export
job that connects to the database while Keycloak is stopped.

## Production Backup Strategy

Production should use automated, tested backups.

Minimum requirements:

- automated Postgres backups
- point-in-time recovery if the provider supports it
- daily backup retention
- off-host backup storage
- encrypted backups at rest
- documented restore procedure
- periodic restore tests into non-production
- Keycloak realm export after major auth changes
- Terraform state backup if Terraform is used
- Traefik ACME storage backup if using file-backed ACME storage

Recommended production ownership:

| Data                      | Backup Method                                 |
| ------------------------- | --------------------------------------------- |
| Keycloak DB               | Managed Postgres backups or scheduled pg_dump |
| App DB                    | Managed Postgres backups or scheduled pg_dump |
| Realm config snapshot     | Keycloak CLI export after config changes      |
| Terraform state           | Encrypted remote backend with versioning      |
| Secrets                   | Secret manager backup/rotation procedure      |
| Traefik ACME certificates | Persistent volume or host mount backup        |
| Docker images             | Registry retention and immutable image tags   |

## Production Restore Order

For a full production recovery:

1. Provision infrastructure.
2. Restore secrets.
3. Restore Postgres.
4. Restore or mount Traefik ACME storage if applicable.
5. Deploy Keycloak pointing at the restored database.
6. Confirm Keycloak realm, clients, users, roles, and groups exist.
7. Deploy the app and API.
8. Run smoke tests.
9. Re-enable scheduled jobs and public traffic.
10. Record the recovery date, backup timestamp, and image tags.

## Production Smoke Tests

After restore:

- Open `https://auth.example.com`.
- Sign in to the Keycloak admin console with a named admin account.
- Open `https://app.example.com`.
- Log in as a normal user.
- Confirm `/users/dashboard` loads.
- Confirm a non-admin cannot access admin routes.
- Log in as an admin.
- Confirm admin routes load.
- If API exists, call an authenticated API endpoint.
- If mobile exists, run an Expo/mobile login flow against the restored auth URL.
- Confirm logout clears the app session.

## Terraform And Backups

Terraform is not a backup. It is desired configuration as code.

Terraform can recreate:

- realm configuration
- clients
- roles
- groups
- client scopes
- protocol mappers
- organizations

Terraform cannot restore:

- users unless you deliberately manage/import them, which is usually not ideal
- sessions
- events
- revoked tokens
- password history
- live operational state

Use Terraform plus database backups:

```text
Terraform: what the config should be
Postgres backup: what actually existed at a point in time
Realm export: readable snapshot for review/migration
```

## Recovery Drills

Do a restore test before production launch and after major auth changes.

Suggested local drill:

1. Configure Keycloak manually or with Terraform.
2. Create a test user.
3. Assign roles and groups.
4. Log in through the app.
5. Back up the Keycloak database.
6. Run `docker compose down -v` for the test stack.
7. Restore the database.
8. Start the stack.
9. Confirm the test user, clients, roles, groups, and login flow still work.

If the restore has not been tested, assume the backup may not work. Bleak, yes,
but honest.

## Safety Rules

- Never run `docker compose down -v` on production.
- Never run `docker system prune --volumes` on a production host.
- Never restore into production without a fresh backup of the current state.
- Never commit database dumps, realm exports with secrets, `.env` files, or
  Terraform state.
- Always verify backup files exist and are non-empty.
- Always test restore commands in a non-production environment.
- Always record which app image, Keycloak image, and database backup belong
  together.

## References

- Keycloak import/export docs:
  <https://www.keycloak.org/server/importExport>
- Keycloak Terraform guide:
  [keycloak-terraform.md](keycloak-terraform.md)
- Production deployment guide:
  [production-deployment.md](production-deployment.md)
- Docker infrastructure notes:
  [../docker/README.md](../docker/README.md)
