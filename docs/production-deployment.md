# Production Deployment And Hardening Guide

This document is a pre-production checklist for deploying the React Router app
with Keycloak-backed authentication. Treat it as a living runbook: update it
when the hosting target, domain names, Postgres provider, or auth flow changes.

## Target Shape

Recommended production shape:

```text
Internet
  -> Traefik TLS reverse proxy / load balancer
    -> React Router app container
    -> FastAPI resource server container
    -> Keycloak
      -> Postgres
```

Keep production separate from the local development Compose stack. The local
`postgres/docker-compose.yml` exposes Postgres directly for developer
convenience, and `auth-server/docker-compose.yml` exposes Keycloak directly.
Production should use a dedicated compose file, orchestrator, or managed
services with stricter networking, secrets, persistence, and backups.

This repo includes local gateway-mode Compose files under `api-gateway/`,
`postgres/`, `auth-server/`, and `web/`. Use them to test the same
reverse-proxy routing model locally before deploying to DigitalOcean.

## Pre-Deployment Decisions

Decide these before building the production environment:

- Public app URL, for example `https://app.example.com`.
- Public Keycloak URL, for example `https://auth.example.com`.
- Public API URL for the future FastAPI resource server, for example
  `https://api.example.com`.
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
WEB_KEYCLOAK_CLIENT_ID=admin-starter-web
WEB_KEYCLOAK_CLIENT_SECRET=

WEB_AUTH_REDIRECT_URI=https://app.example.com/auth/callback
WEB_AUTH_POST_LOGIN_REDIRECT_URI=https://app.example.com/users/dashboard
WEB_AUTH_POST_LOGOUT_REDIRECT_URI=https://app.example.com

WEB_SESSION_SECRET=<long-random-secret>
WEB_DATABASE_URL=<postgres-connection-string>
WEB_TOKEN_ENCRYPTION_KEY=<second-long-random-secret>
WEB_RESOURCE_SERVER_BASE_URL=<resource-server-url>
WEB_KEYCLOAK_API_AUDIENCE=<resource-server-audience>
WEB_TOKEN_REFRESH_LEEWAY_SECONDS=60
WEB_SESSION_LAST_SEEN_UPDATE_SECONDS=300
```

If the Keycloak client is public with PKCE, `WEB_KEYCLOAK_CLIENT_SECRET` can stay
empty. If the client is confidential, store the secret only in the server-side
runtime environment.

Generate `WEB_SESSION_SECRET` and `WEB_TOKEN_ENCRYPTION_KEY` with
cryptographically strong random values. Do not commit production secrets to the
repository.

## Local Traefik Test Stack

Use this when you want to test Traefik locally instead of hitting Vite and
Keycloak directly by port.

1. Copy the local Traefik environment template:

   ```bash
   cp .env.traefik.example .env.traefik
   ```

2. Update `.env.traefik` secrets. For local HTTP testing, keep:

   ```env
   APP_NODE_ENV=development
   APP_EXTERNAL_URL=http://app.localhost
   KEYCLOAK_EXTERNAL_URL=http://auth.localhost
   KEYCLOAK_ISSUER=http://auth.localhost/realms/admin-starter
   WEB_AUTH_REDIRECT_URI=http://app.localhost/auth/callback
   WEB_AUTH_POST_LOGIN_REDIRECT_URI=http://app.localhost/users/dashboard
   WEB_AUTH_POST_LOGOUT_REDIRECT_URI=http://app.localhost
   ```

   The app session cookie is marked `Secure` when `NODE_ENV=production`.
   Keeping `APP_NODE_ENV=development` lets browser login work over local HTTP.
   Use `production` only when Traefik is serving HTTPS.

3. Start the stack:

   ```bash
   corepack pnpm dev:gateway
   ```

4. Open:

   ```text
   http://app.localhost
   http://auth.localhost
   http://localhost:8081
   ```

   `app.localhost` routes to the React Router container, `auth.localhost`
   routes to Keycloak, and `localhost:8081` opens the Traefik dashboard.

5. Configure the Keycloak client for the Traefik local URLs:

   ```text
   Root URL: http://app.localhost
   Home URL: http://app.localhost
   Valid redirect URIs: http://app.localhost/*
   Valid post logout redirect URIs: http://app.localhost/*
   Web origins: http://app.localhost
   ```

6. Stop the stack:

   ```bash
   corepack pnpm dev:gateway:down
   ```

To reset the local Traefik Postgres volume:

```bash
docker compose -f auth-server/docker-compose.gateway.yml --env-file .env.traefik down
docker compose -f postgres/docker-compose.gateway.yml --env-file .env.traefik down -v
```

## Build The App Image

The repo includes a production Dockerfile under `web/` that builds the React
Router app and runs:

```bash
pnpm start
```

Build and tag the image:

```bash
docker build -f web/Dockerfile -t registry.example.com/admin-starter-keycloak:YYYY-MM-DD .
```

Before publishing the image:

```bash
corepack pnpm check
corepack pnpm web:build
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

### Registration Approval

If public self-service registration is enabled, decide how new accounts are
approved before production launch. Keycloak has an **Enabled** switch on each
user, but it does not provide a built-in realm setting that makes
self-registered users disabled by default.

For this starter, the intended global approval model is:

1. User self-registers in Keycloak.
2. User verifies their email.
3. A custom Keycloak event listener handles the `VERIFY_EMAIL` event.
4. The listener sets the user **Enabled** value to off and can add an
   `awaiting_admin_approval=true` user attribute for admin visibility.
5. The listener removes active Keycloak sessions for that user.
6. A Keycloak admin reviews the account.
7. The admin sets **Enabled** back on.
8. The user can then authenticate into any app in the realm.

This keeps approval at the Keycloak layer. The React Router app should not add
an app-level approval page or approval flag for this flow. Disabled users do not
receive tokens, so they never reach `/auth/callback`.

The default Keycloak disabled-account login message is acceptable for the MVP.
Later Keycloakify theme work can style the login experience per client without
changing this approval mechanism.

This repo includes the `disable-after-email-verify` provider under
`auth-server/providers/`. After deploying a Keycloak image that includes the
provider, enable it in the realm:

```text
Realm settings -> Events -> Event listeners
```

Add this provider id:

```text
disable-after-email-verify
```

## Keycloak Server Hardening

For production Keycloak:

- Run Keycloak behind HTTPS.
- Set the production hostname to the public auth domain.
- Do not expose Keycloak directly on an untrusted HTTP port.
- Keep the admin console reachable only by trusted users and networks when
  possible.
- Use a strong Postgres password and a dedicated Keycloak database and user.
- Enable regular Keycloak and Postgres backups.
- Configure logs so login failures, admin events, and suspicious activity are
  retained.
- Keep Keycloak patched; plan upgrades separately from app deploys.
- Export the realm configuration after major auth changes.

If Keycloak is containerized, avoid using `start-dev` in production. Use the
production start mode and configure hostname/proxy settings for the deployment
environment.

Custom Keycloak providers should be built into the production Keycloak image
instead of relying on ad hoc mounted jars. The `auth-server/Dockerfile` builds
the registration-approval provider, copies the jar into
`/opt/keycloak/providers/`, and runs `/opt/keycloak/bin/kc.sh build`. Local
development can use `start-dev` for faster iteration, but production should run
an optimized Keycloak image that already contains the provider.

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

Put the app, Keycloak, and the future FastAPI resource server behind Traefik:

- Terminate TLS with valid certificates.
- Redirect HTTP to HTTPS.
- Send `X-Forwarded-Proto`, `X-Forwarded-Host`, and related proxy headers as
  required by the platform.
- Add HSTS after HTTPS is confirmed stable.
- Set reasonable request body and timeout limits.
- Route `app.example.com` to the React Router container.
- Route `auth.example.com` to Keycloak.
- Route `api.example.com` to the FastAPI container after it exists.

Confirm cookies are secure in production. The app session cookie is configured
with `secure: process.env.NODE_ENV === "production"`, so `NODE_ENV=production`
must be set.

## DigitalOcean Traefik Notes

For a Docker Compose deployment on a DigitalOcean Droplet:

- Point DNS records for `app.example.com`, `auth.example.com`, and later
  `api.example.com` to the Droplet.
- Open only ports `80` and `443` publicly.
- Keep Postgres on a private Docker network or move it to DigitalOcean Managed
  PostgreSQL.
- Use Traefik's Docker provider for service discovery.
- Use a persistent volume or host mount for Traefik ACME certificate storage.
- Do not enable `--api.insecure=true` on a public host. If you keep the Traefik
  dashboard, protect it with authentication and network restrictions.
- Set `APP_NODE_ENV=production` and use only `https://` URLs in app and
  Keycloak environment variables.

Production Traefik should add a secure entrypoint and ACME certificate resolver,
for example:

```yaml
command:
  - --entrypoints.web.address=:80
  - --entrypoints.websecure.address=:443
  - --entrypoints.web.http.redirections.entrypoint.to=websecure
  - --entrypoints.web.http.redirections.entrypoint.scheme=https
  - --certificatesresolvers.letsencrypt.acme.email=ops@example.com
  - --certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json
  - --certificatesresolvers.letsencrypt.acme.httpchallenge=true
  - --certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web
  - --providers.docker=true
  - --providers.docker.exposedbydefault=false
ports:
  - "80:80"
  - "443:443"
volumes:
  - /var/run/docker.sock:/var/run/docker.sock:ro
  - traefik_letsencrypt:/letsencrypt
```

Production routers should use the HTTPS entrypoint and certificate resolver:

```yaml
labels:
  - traefik.enable=true
  - traefik.http.routers.app.rule=Host(`app.example.com`)
  - traefik.http.routers.app.entrypoints=websecure
  - traefik.http.routers.app.tls.certresolver=letsencrypt
  - traefik.http.services.app.loadbalancer.server.port=3000
```

Use the same pattern for Keycloak and the future FastAPI service, changing the
host rule and internal service port.

## Future FastAPI Resource Server

When FastAPI is added, keep it private behind Traefik and validate Keycloak
access tokens on every protected request.

Suggested route shape:

```text
https://api.example.com -> FastAPI container
```

Suggested Compose labels:

```yaml
labels:
  - traefik.enable=true
  - traefik.http.routers.api.rule=Host(`api.example.com`)
  - traefik.http.routers.api.entrypoints=websecure
  - traefik.http.routers.api.tls.certresolver=letsencrypt
  - traefik.http.services.api.loadbalancer.server.port=8000
```

Suggested FastAPI auth settings:

```env
KEYCLOAK_ISSUER=https://auth.example.com/realms/admin-starter
API_PYTHON_KEYCLOAK_AUDIENCE=admin-starter-api-python
```

Create a separate Keycloak client for the API if the API needs its own audience,
service account, or authorization model. Keep the browser app client
`admin-starter-web` separate from the resource server client.

## App Hardening Checklist

Before production launch:

- Use HTTPS-only production URLs in app and Keycloak configuration.
- Use a long random `WEB_SESSION_SECRET`.
- Use a separate long random `WEB_TOKEN_ENCRYPTION_KEY`.
- Confirm the session cookie is `HttpOnly`, `SameSite=Lax`, and `Secure`.
- Confirm `/auth/callback` rejects invalid or missing `state`.
- Confirm login works after browser restart.
- Confirm logout is POST-only and redirects through Keycloak logout.
- Confirm unauthorized users are redirected to `/forbidden`.
- Confirm Admin routes require the `Admins` client role.
- Confirm no Keycloak tokens are stored in `localStorage`.
- Confirm browser cookies contain only the opaque BFF session id, not tokens.
- Add app-level audit logging before sensitive admin workflows go live.

## Deployment Steps

1. Provision production DNS for the app and Keycloak domains.
2. Configure Traefik with HTTPS and ACME certificate storage.
3. Provision Postgres and create required databases/users.
4. Deploy Keycloak and connect it to production Postgres.
5. Create or import the production realm.
6. Configure the production app client and roles.
7. Create initial admin users and groups.
8. Build and push the app image.
9. Deploy the app container with production environment variables.
10. Run smoke tests.
11. Enable monitoring, backups, and alerting.
12. Record the deployed image tag, realm export, and Postgres backup state.

## Smoke Tests

After each production deploy:

- Visit the public app URL.
- Click Login and confirm Keycloak opens over HTTPS.
- Log in as a normal user and confirm `/users/dashboard` loads.
- Visit `/admins/dashboard` as a non-admin and confirm access is denied.
- Log in as an Admin and confirm `/admins/dashboard` loads.
- Click Register and confirm the intended Keycloak registration behavior.
- If the registration-approval provider is enabled, register a new user, verify
  email, confirm Keycloak disables the user, then enable the user manually and
  confirm login succeeds.
- Click Logout and confirm the local BFF session clears and Keycloak ends SSO.
- Restart the app container and confirm existing users can still sign in.

## Backups And Recovery

Minimum backup requirements:

- Automated Postgres backups.
- A documented restore command or provider restore procedure.
- Periodic restore tests into a non-production environment.
- Realm export after major Keycloak configuration changes.
- Secret rotation procedure for `WEB_SESSION_SECRET`, Postgres credentials, and
  Keycloak client secrets.

Before upgrades:

- Take a fresh Postgres backup.
- Export the Keycloak realm.
- Record current image tags.
- Confirm rollback image tags are still available.

## Current Gaps To Close Before Production

Known items from the current proof of concept:

- The included Traefik Compose stack is local HTTP only. Create a hardened
  DigitalOcean production Compose file or deployment manifest before launch.
- Formal app database migrations are not defined yet. The BFF session table is
  created by `postgres/init-app-schema.sql`, which Docker runs only on the first
  boot of an empty Postgres volume — so schema changes have to be applied by
  hand or by recreating the volume. The web server contains no DDL and performs
  no migration at startup.
- Health checks for the app container are not defined yet.
- Production observability, backups, and restore tests are not configured yet.
