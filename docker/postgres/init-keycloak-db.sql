-- Runs once on first container boot via docker-entrypoint-initdb.d.
-- Gives Keycloak its own database inside the shared Postgres instance,
-- separate from the app's schema.
CREATE DATABASE keycloak;