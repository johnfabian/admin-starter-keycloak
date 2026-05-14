# Production Deployment And Hardening Guide

This document is a pre-production checklist for deploying the React Router app
with Keycloak-backed authentication. Treat it as a living runbook: update it
when the hosting target, domain names, database provider, or auth flow changes.

## Target Shape

Recommended production shape:

```text
Internet
  -> TLS reverse proxy / load balancer
    -> React Router app container
    -> Keycloak
      -> Postgres
```

Keep production separate from the local development Compose stack. The local
`docker/docker-compose.yml` exposes Postgres and Keycloak directly for developer
convenience. Production should use a dedicated compose file, orchestrator, or
managed services with stricter networking, secrets, persistence, and backups.

## Pre-Deployment Decisions

Decide these before building the production environment:

- Public app URL, for example `https://app.example.com`.
- Public Keycloak URL, for example `https://auth.example.com`.
- Whether Postgres is self-hosted in Docker or managed by a cloud provider.
- Where Docker images will be built and stored.
- Where secrets will live: platform secrets, Docker secrets, SOPS, Vault, or
  another secret manager.
- Backup location and restore procedure for Postgres.
- Who owns the first production Keycloak admin account.

## Application Environment

Production values should not reuse `.env.development`.

Required production variables:

```env
NODE_ENV=production

KEYCLOAK_ISSUER=https://auth.example.com/realms/admin-starter
KEYCLOAK_CLIENT_ID=admin-starter-web
KEYCLOAK_CLIENT_SECRET=

AUTH_REDIRECT_URI=https://app.example.com/auth/callback
AUTH_POST_LOGIN_REDIRECT_URI=https://app.example.com/users/dashboard
AUTH_POST_LOGOUT_REDIRECT_URI=https://app.example.com

SESSION_SECRET=<long-random-secret>
```

If the Keycloak client is public with PKCE, `KEYCLOAK_CLIENT_SECRET` can stay
empty. If the client is confidential, store the secret only in the server-side
runtime environment.

Generate `SESSION_SECRET` with a cryptographically strong random value. Do not
commit production secrets to the repository.

## Build The App Image

The repo includes a production Dockerfile that builds the React Router app and
runs:

```bash
bun run start
```

Build and tag the image:

```bash
docker build -t registry.example.com/admin-starter-keycloak:YYYY-MM-DD .
```

Before publishing the image:

```bash
npm run check
npm run build
```

Push the image to the deployment registry:

```bash
docker push registry.example.com/admin-starter-keycloak:YYYY-MM-DD
```

## Keycloak Production Settings

In the production realm:

- Use a dedicated realm such as `admin-starter`.
- Enable Standard flow.
- Enable PKCE with `S256`.
- Disable Implicit flow.
- Disable Direct access grants unless a trusted integration needs it.
- Disable Service accounts on the browser/web client unless needed.
- Keep Authorization Services off unless the app intentionally adopts them.
- Set valid redirect URIs to the exact production callback URL:
  `https://app.example.com/auth/callback`.
- Set valid post logout redirect URIs to trusted production app URLs only.
- Set web origins to `https://app.example.com`, not `*`.
- Enable self-service registration only if public registration is intended.
- Configure SMTP before enabling email verification or password reset.
- Require email verification if user identity quality matters.
- Configure password policy, brute force protection, and account lockout.
- Create roles and groups intentionally; do not assign broad admin access by
  default.

After bootstrap, create named admin users and stop relying on the bootstrap
admin credentials for daily use.

## Keycloak Server Hardening

For production Keycloak:

- Run Keycloak behind HTTPS.
- Set the production hostname to the public auth domain.
- Do not expose Keycloak directly on an untrusted HTTP port.
- Keep the admin console reachable only by trusted users and networks when
  possible.
- Use a strong database password and a dedicated database/user for Keycloak.
- Enable regular Keycloak and database backups.
- Configure logs so login failures, admin events, and suspicious activity are
  retained.
- Keep Keycloak patched; plan upgrades separately from app deploys.
- Export the realm configuration after major auth changes.

If Keycloak is containerized, avoid using `start-dev` in production. Use the
production start mode and configure hostname/proxy settings for the deployment
environment.

## Postgres Hardening

For production Postgres:

- Prefer a managed Postgres service if available.
- Do not publish port `5432` to the public internet.
- Use strong unique passwords.
- Use separate databases and users for app data and Keycloak when practical.
- Enable automated backups and point-in-time recovery if the provider supports
  it.
- Test restore before launch.
- Monitor disk usage, connection count, replication/backups, and slow queries.
- Restrict network access to only the app and Keycloak runtime.

For self-hosted Docker Postgres:

- Use named volumes or host mounts with an explicit backup plan.
- Do not run `docker compose down -v` in production.
- Do not run `docker system prune --volumes` on the production host.
- Snapshot the volume before major upgrades.

## Reverse Proxy And TLS

Put the app and Keycloak behind a reverse proxy or load balancer:

- Terminate TLS with valid certificates.
- Redirect HTTP to HTTPS.
- Send `X-Forwarded-Proto`, `X-Forwarded-Host`, and related proxy headers as
  required by the platform.
- Add HSTS after HTTPS is confirmed stable.
- Set reasonable request body and timeout limits.
- Route `app.example.com` to the React Router container.
- Route `auth.example.com` to Keycloak.

Confirm cookies are secure in production. The app session cookie is configured
with `secure: process.env.NODE_ENV === "production"`, so `NODE_ENV=production`
must be set.

## App Hardening Checklist

Before production launch:

- Use HTTPS-only production URLs in app and Keycloak configuration.
- Use a long random `SESSION_SECRET`.
- Confirm the session cookie is `HttpOnly`, `SameSite=Lax`, and `Secure`.
- Confirm `/auth/callback` rejects invalid or missing `state`.
- Confirm login works after browser restart.
- Confirm logout behavior is acceptable for launch.
- Confirm unauthorized users are redirected to `/forbidden`.
- Confirm Admin routes require the `Admins` client role.
- Confirm no Keycloak tokens are stored in `localStorage`.
- Add server-side session storage before forwarding Keycloak tokens to a future
  API/resource server.
- Add full Keycloak SSO logout when the server stores `id_token` for
  `id_token_hint`.
- Add app-level audit logging before sensitive admin workflows go live.

## Deployment Steps

1. Provision production DNS for the app and Keycloak domains.
2. Provision TLS certificates.
3. Provision Postgres and create required databases/users.
4. Deploy Keycloak and connect it to production Postgres.
5. Create or import the production realm.
6. Configure the production app client and roles.
7. Create initial admin users and groups.
8. Build and push the app image.
9. Deploy the app container with production environment variables.
10. Run smoke tests.
11. Enable monitoring, backups, and alerting.
12. Record the deployed image tag, realm export, and database backup state.

## Smoke Tests

After each production deploy:

- Visit the public app URL.
- Click Login and confirm Keycloak opens over HTTPS.
- Log in as a normal user and confirm `/users/dashboard` loads.
- Visit `/admins/dashboard` as a non-admin and confirm access is denied.
- Log in as an Admin and confirm `/admins/dashboard` loads.
- Click Register and confirm the intended Keycloak registration behavior.
- Click Logout and confirm the local app session clears.
- Restart the app container and confirm existing users can still sign in.

## Backups And Recovery

Minimum backup requirements:

- Automated Postgres backups.
- A documented restore command or provider restore procedure.
- Periodic restore tests into a non-production environment.
- Realm export after major Keycloak configuration changes.
- Secret rotation procedure for `SESSION_SECRET`, database credentials, and
  Keycloak client secrets.

Before upgrades:

- Take a fresh database backup.
- Export the Keycloak realm.
- Record current image tags.
- Confirm rollback image tags are still available.

## Current Gaps To Close Before Production

Known items from the current proof of concept:

- Production Compose or deployment manifests do not exist yet.
- Logout currently clears only the app session; full Keycloak SSO logout still
  needs server-side storage for `id_token_hint`.
- Keycloak tokens are not persisted server-side yet; add server-side sessions
  before calling a resource API on behalf of the user.
- App database schema and migrations are not defined yet.
- Health checks for the app container are not defined yet.
- Production observability, backups, and restore tests are not configured yet.

