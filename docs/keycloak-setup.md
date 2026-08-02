# Keycloak Setup Guide

This project uses Keycloak for authentication, identity, groups, and app roles.
The React application should not implement its own login, registration,
password reset, or role assignment UI for this starter.

The current realm is expected to be named `admin-starter`.

## Local Services

Copy the environment template and fill in local values:

```bash
cp .env.example .env.development
```

Required local values:

```env
POSTGRES_USER=app
POSTGRES_PASSWORD=<local-password>
POSTGRES_DB=admin_starter

KEYCLOAK_ADMIN_USER=<bootstrap-admin-username>
KEYCLOAK_ADMIN_PASSWORD=<bootstrap-admin-password>
KEYCLOAK_HOSTNAME=localhost
```

Start the shared Postgres database and Keycloak from the project root:

```bash
corepack pnpm db:up
corepack pnpm auth:up
```

Open the Keycloak admin console:

```text
http://localhost:8080
```

Sign in with `KEYCLOAK_ADMIN_USER` and `KEYCLOAK_ADMIN_PASSWORD`.

The bootstrap admin values only apply the first time Keycloak initializes its
database. After that, manage admin accounts from the Keycloak console.

## Local Traefik Services

Use this stack when you want to test the app through Traefik locally:

```bash
cp .env.traefik.example .env.traefik
corepack pnpm dev:gateway
```

Open:

```text
http://app.localhost
http://auth.localhost
http://api.localhost
http://localhost:8081
```

`http://localhost:8081` is the local Traefik dashboard. The app and Keycloak
should be opened through `app.localhost` and `auth.localhost` so the same
host-based routing model matches real DigitalOcean domains. Use
`api.localhost` for the Express resource server once it exists. Until then it
returns a Traefik 404, since nothing is routed there yet.

## Docker Desktop Project Names

The local Compose files include explicit project names so Docker Desktop groups
them by boundary:

```text
admin-starter-local-mail-server   local-mail-server/docker-compose.yml
admin-starter-postgres            postgres/docker-compose.yml
admin-starter-auth-server         auth-server/docker-compose.yml
admin-starter-api-gateway         api-gateway/docker-compose.yml
admin-starter-postgres-gateway    postgres/docker-compose.gateway.yml
admin-starter-auth-gateway        auth-server/docker-compose.gateway.yml
admin-starter-web-gateway         web/docker-compose.gateway.yml
```

Container names, which are what `docker ps` and `docker exec` need:

```text
direct   app-mailpit, app-postgres, app-keycloak
gateway  app-mailpit, app-traefik, app-traefik-postgres,
         app-traefik-keycloak, app-traefik-web
```

Mailpit is shared by both stacks and has no gateway variant.

## Realm

Use the existing realm:

```text
admin-starter
```

If you need to recreate it:

1. Open the Keycloak admin console.
2. Select the realm dropdown.
3. Choose **Create realm**.
4. Enter `admin-starter`.
5. Save.

All app users, groups, and roles for this starter should live in this realm.

## Realm Baseline Settings

Configure these realm-level settings before tuning individual clients.

Recommended realm settings:

- Realm display name: `Admin Starter`
  - User-facing label shown on Keycloak pages if a custom theme uses it.
- User registration: `On` only if public self-service registration is intended
  - The app's Register button sends users to Keycloak registration. Keep this
    off for private/internal deployments.
- Login with email: `On`
  - Lets users sign in with either username or email.
- Duplicate emails: `Off`
  - Keeps email addresses unique enough for account recovery and admin support.
- Verify email: `On` for production
  - Use local development exceptions only for test accounts.
- Forgot password: `On` after SMTP is configured
  - Password reset emails require working SMTP settings.
- Remember me: `Off` to start
  - Enable only if longer browser SSO sessions are an explicit product choice.
- Brute force detection: `On`
  - Configure lockout thresholds before exposing login publicly.
- Password policy:
  - Minimum length: at least `12`
  - Not username: `On`
  - Not email: `On`
  - History: `3` or more
  - Password blacklist: `On` if available in the deployed Keycloak version
- Events:
  - Save events: `On`
  - Save admin events: `On`
  - Include representation: `Off` unless debugging a specific admin issue

Recommended realm session and token baseline:

- SSO Session Idle: `30 minutes`
- SSO Session Max: `8 hours`
- Client Session Idle: leave empty or set below SSO Session Idle
- Client Session Max: leave empty or set below SSO Session Max
- Access Token Lifespan: `5 minutes`
- Access Token Lifespan For Implicit Flow: leave default; implicit flow is off
- Client Login Timeout: `1 minute`
- Login Timeout: `5 minutes`
- Login Action Timeout: `5 minutes`

Keycloak requires client-specific session settings to stay within the realm SSO
session limits. If a client needs a shorter session, set it on that client's
Advanced tab. Do not set a client session idle or max value longer than the
realm SSO value.

## App Client

Create an application client for this React app:

```text
admin-starter-web
```

Recommended local client settings:

- Client type: `OpenID Connect`
  - Tells Keycloak this client uses the OIDC/OAuth flow. Use this for React
    apps and most modern web applications.
- Client authentication: `Off`
  - Makes the client public. Browser apps cannot safely keep a client secret.
    Turn this on only for a server-side confidential client that can keep a
    secret.
- Authorization: `Off`
  - Leaves Keycloak Authorization Services disabled. This starter uses client
    roles for coarse app access instead of Keycloak resources, scopes, policies,
    UMA, and RPT tokens.
- Standard flow: `On`
  - Enables the Authorization Code flow, which is the normal browser redirect
    sign-in flow.
- Direct access grants: `Off`
  - Disables username/password token requests directly to Keycloak. Keep this
    off unless a trusted tool specifically needs password-grant behavior.
- Implicit flow: `Off`
  - Disables the older browser flow that returns tokens directly from the
    authorization endpoint. Prefer Standard flow with PKCE.
- Service accounts roles: `Off`
  - Disables machine-to-machine client credentials for this browser client.
    Use a separate confidential client if background services need this.
- PKCE method: `S256` if available
  - Adds proof-key protection to the Authorization Code flow for public browser
    clients.
- Root URL:
  - Value: `http://localhost:5173`
  - Traefik local value: `http://app.localhost`
  - The base URL Keycloak can use when resolving relative client URLs.
- Home URL:
  - Value: `http://localhost:5173`
  - Traefik local value: `http://app.localhost`
  - Where Keycloak can send users when launching or returning to the app from
    client-related screens.
- Valid redirect URIs:
  - Value: `http://localhost:5173/*`
  - Value: `http://localhost:5173/auth/callback`
  - Traefik local value: `http://app.localhost/*`
  - Traefik local value: `http://app.localhost/auth/callback`
  - The allowed callback destinations after login. Keep this restricted to
    trusted app URLs so tokens cannot be redirected elsewhere.
- Valid post logout redirect URIs:
  - Value: `http://localhost:5173/*`
  - Traefik local value: `http://app.localhost/*`
  - The allowed destinations after logout. The app logout flow should return
    users only to one of these URLs.
- Web origins:
  - Value: `http://localhost:5173`
  - Traefik local value: `http://app.localhost`
  - Controls browser CORS origins for this client. Use the exact dev origin
    instead of `*` for a tighter local setup.

Recommended client scopes and role scope settings:

- Default client scopes:
  - `profile`
  - `email`
  - `roles`
  - `web-origins`
  - `admin-starter-api-express-audience` after the API audience scope is created
- Optional client scopes:
  - `organization`
  - `offline_access` only if the app intentionally requests offline tokens
- Full scope allowed: `Off`
  - Keep role exposure explicit. If turning this off hides expected roles from
    tokens, add the required client roles through role scope mappings instead
    of enabling broad scope access.
- Role scope mappings:
  - Allow `admin-starter-web:Users`
  - Allow `admin-starter-web:Admins`
  - Allow `admin-starter-api-express:api-users`
  - Allow `admin-starter-api-express:api-admins`

Recommended Advanced tab settings:

- Access Token Lifespan: leave empty to inherit the realm `5 minutes`
  - Use a shorter value only for very sensitive routes.
- Client Session Idle: leave empty to inherit the realm setting
  - If overridden, keep it shorter than realm SSO Session Idle.
- Client Session Max: leave empty to inherit the realm setting
  - If overridden, keep it shorter than realm SSO Session Max.
- Client Offline Session Idle: leave empty unless offline tokens are used
- Client Offline Session Max: leave empty unless offline tokens are used
- Proof Key for Code Exchange Code Challenge Method: `S256`
- OAuth 2.0 Device Authorization Grant: `Off`
- OIDC CIBA Grant: `Off`
- Valid request URIs: leave blank
  - Required only if using signed request objects or pushed/request URI flows.
- Fine grain OpenID Connect configuration:
  - Access Token Signature Algorithm: `RS256`
  - ID Token Signature Algorithm: `RS256`
  - User Info Signed Response Algorithm: `unsigned`
  - Request Object Required: `Not required`

Recommended local logout settings:

- Front channel logout: `Off`
  - When on, Keycloak logs clients out through the user's browser, usually with
    a front-channel URL or iframe. Leave it off unless the app has a route that
    intentionally handles front-channel logout.
- Front-channel logout URL: leave blank
  - The browser URL Keycloak would call during front-channel logout. Blank is
    correct while there is no logout callback route.
- Front-channel logout session required: leave default
  - Controls whether Keycloak includes session and issuer values in the
    front-channel logout request. It only matters when front-channel logout is
    enabled.
- Backchannel logout URL: leave blank
  - The server endpoint Keycloak would call with a logout token. Blank is
    correct until this starter adds an explicit backchannel logout route.
- Backchannel logout session required: leave default
  - Controls whether Keycloak includes the session id claim in the backchannel
    logout token. It only matters when a backchannel logout URL exists.
- Backchannel logout revoke offline sessions: `Off`
  - Controls whether Keycloak tells the client to revoke offline sessions
    during backchannel logout. This starter does not use offline sessions.
- Logout confirmation: `Off` if available
  - Skips Keycloak's "you are logged out" confirmation page when a valid
    post-logout redirect is supplied.

For this starter, the app should use Keycloak's normal OIDC logout endpoint and
return the user to one of the configured **Valid post logout redirect URIs**.
Do not configure a front-channel or backchannel logout URL until the application
has a real route that can receive and process that logout request.

Local app logout is a POST action that clears the BFF session cookie, deletes
the server-side session record, and redirects through Keycloak's OIDC logout
endpoint with `id_token_hint` when available.

The `id_token_hint` logout parameter is an intentional OIDC logout exception.
It preserves full Keycloak SSO logout behavior, but production deployments
should use HTTPS, no-store auth responses, strict referrer policy, short-lived
minimal ID token claims, and proxy logging that avoids full query strings.

Logout callback options:

- Use front-channel logout only if the browser app needs Keycloak to call a
  front-channel URL during SSO logout.
- Use backchannel logout for a server-side session endpoint such as
  `http://localhost:5173/auth/backchannel-logout` if the app stores its own
  server session that must be invalidated when Keycloak logs the user out.

Use Keycloak for login. The app should redirect to Keycloak rather than render
custom login screens. This app uses React Router framework-mode server routes
with an HttpOnly session cookie instead of storing tokens in browser
`localStorage`. The cookie stores only an opaque BFF session id; Keycloak tokens
are encrypted in the server-side session table before the BFF forwards access
tokens to a resource server.

Successful app login redirects to the user dashboard:

```text
http://localhost:5173/users/dashboard
```

The server-side callback route is:

```text
http://localhost:5173/auth/callback
```

Registration uses the Keycloak registration action. Enable realm self-service
registration if the app's Register button should create new users.

## API Client

API-specific Keycloak setup lives with the API service that needs it:

- [Express API setup](../api-express/README.md) - client creation, audience
  mapper, and token validation settings
- [Traefik API gateway setup](../api-gateway/README.md) - routing and hostnames

The pattern is the same for any resource server. Create a separate Keycloak
client to represent the API, add an audience mapper so tokens issued to
`admin-starter-web` carry the API audience in the `aud` claim, and have the API
validate bearer tokens against Keycloak JWKS. A resource server must never use
the browser cookie session from the React Router app:

```http
Authorization: Bearer <access-token>
```

Behind Traefik the API is reachable at `http://api.localhost` locally and
`https://api.example.com` in production.

## Application Roles

Create these as **client roles** on the `admin-starter-web` client:

```text
Admins
Users
```

The app should treat these roles as coarse-grained access roles:

- `Admins` can access the Admin section and manage users, groups, and group
  permissions.
- `Users` can access normal authenticated app areas such as Apps and Todos.

Groups are dynamic and should not be hard-coded in the application. Assign the
`Admins` or `Users` client role to Keycloak groups, then add users to those
groups. The app should read roles from the authenticated user's token and make
decisions from the client roles, not group names.

Composite roles and fine-grained permission roles are optional. If the app grows
beyond this simple model, `Admins` can become a composite role that contains
permissions such as `admin-read`, `admin-update`, `admin-delete`, and
`admin-fullcontrol`.

## Admin User

Create an application Admin user in the `admin-starter` realm:

1. Go to **Users**.
2. Choose **Create new user**.
3. Fill in username, email, first name, and last name.
4. Set **Email verified** if this is a local development account.
5. Save.
6. Open the new user.
7. Go to **Credentials**.
8. Set an initial password.
9. Disable **Temporary** for local development if you do not want a forced
   password change.

Assign Admin access:

1. Open the user.
2. Go to **Role mapping**.
3. Choose **Assign role**.
4. Filter by client roles for `admin-starter-web`.
5. Assign `Admins`.

Alternatively, create a Keycloak group such as `Application Admins`, assign the
`Admins` client role to that group, then add the user to the group. The group
name is only an administration convenience; the application should only depend
on the client role.

## Token Verification

After sign-in, verify that the user's token contains the assigned client roles.
For the `admin-starter-web` client, Keycloak commonly emits client roles under:

```json
{
  "resource_access": {
    "admin-starter-web": {
      "roles": ["Admins"]
    }
  }
}
```

The application role helper should normalize those roles into a flat role list
and check for the exact role names documented above.

## App Routes

Routes that exist today, as wired in `web/app/lib/app-settings.shared.ts`:

```text
/                      splash (public)
/users/dashboard
/profile
/settings
/apps/dashboard
/apps/todos            placeholder page
/admins/dashboard
/forbidden
/auth/login|register|callback|account|logout
```

Route behavior:

- `/` is the only app page an unauthenticated visitor can reach. The `/auth/*`
  routes are public because login has to be reachable.
- Everything in the signed-in shell — `/users/*`, `/profile`, `/settings`,
  `/apps/*` — requires the `Users` role.
- `/admins/*` requires `Admins`.
- `Admins` reaches every route, since it belongs to both access groups.
- `/users`, `/admins`, and `/apps` redirect to their `/dashboard` pages.
- A signed-in user without either role lands on `/forbidden`.

Use shadcn UI controls for tables, buttons, forms, dialogs, sidebars, dropdowns,
badges, and navigation primitives.

## Local User Data

There is no todos table yet — `/apps/todos` renders a placeholder page. This
section records the intended shape for when app-owned data is added.

Application data should be persisted in Postgres and scoped to the current
Keycloak user. Use the Keycloak token `sub` claim as the stable user id:

```text
todos.keycloak_user_id = token.sub
```

The app does not need a local users table for authentication or permissions.
Keycloak owns identity, login, groups, and role assignment.

A local users table is optional. Add one only if the application needs
app-owned user profile data, denormalized display names or emails, audit
metadata, or foreign-key convenience for larger domain models.

Recommended starting point for Todos:

- Store `keycloak_user_id` directly on each todo.
- Query todos by the authenticated user's `sub`.
- Never allow one user to query or mutate another user's todos.
- Add a local user profile table only when app-owned user metadata becomes
  necessary.

## References

- Local roles and permissions guide:
  [keycloak-roles-and-permissions.md](keycloak-roles-and-permissions.md)
- Local email verification setup:
  [keycloak-email-verification.md](keycloak-email-verification.md)
- Keycloak securing applications and services:
  <https://www.keycloak.org/docs/latest/securing_apps/>
- Keycloak server administration:
  <https://www.keycloak.org/docs/latest/server_admin/>
