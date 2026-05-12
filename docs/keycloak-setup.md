# Keycloak Setup Guide

This project uses Keycloak for authentication, identity, groups, and app roles.
The React application should not implement its own login, registration,
password reset, or role assignment UI for this starter.

The current realm is expected to be named `admin-starter`.

## Local Services

Copy the environment template and fill in local values:

```powershell
Copy-Item .env.example .env.development
```

Required local values:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<local-password>
POSTGRES_DB=admin_starter

KEYCLOAK_ADMIN_USER=<bootstrap-admin-username>
KEYCLOAK_ADMIN_PASSWORD=<bootstrap-admin-password>
KEYCLOAK_HOSTNAME=localhost
```

Start Postgres and Keycloak from the project root:

```powershell
docker compose -f docker/docker-compose.yml --env-file .env.development up -d --wait
```

Open the Keycloak admin console:

```text
http://localhost:8080
```

Sign in with `KEYCLOAK_ADMIN_USER` and `KEYCLOAK_ADMIN_PASSWORD`.

The bootstrap admin values only apply the first time Keycloak initializes its
database. After that, manage admin accounts from the Keycloak console.

## Docker Desktop Project Name

Docker Desktop currently shows the Compose app as `docker` because the Compose
file is located in the `docker` directory. Docker Compose uses the directory
name as the default project name unless a project name is supplied.

Recommended options to rename the Docker Desktop group to
`admin-starter-keycloak`:

1. Add a top-level name to `docker/docker-compose.yml`:

   ```yaml
   name: admin-starter-keycloak

   services:
     postgres:
       ...
   ```

2. Or pass the project name when running Compose:

   ```powershell
   docker compose -p admin-starter-keycloak -f docker/docker-compose.yml --env-file .env.development up -d --wait
   ```

The individual containers are currently named `app-postgres` and
`app-keycloak`.

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
    Turn this on only if a server-side confidential client is added later.
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
    Use a separate confidential client later if background services need this.
- PKCE method: `S256` if available
  - Adds proof-key protection to the Authorization Code flow for public browser
    clients.
- Root URL:
  - Value: `http://localhost:5173`
  - The base URL Keycloak can use when resolving relative client URLs.
- Home URL:
  - Value: `http://localhost:5173`
  - Where Keycloak can send users when launching or returning to the app from
    client-related screens.
- Valid redirect URIs:
  - Value: `http://localhost:5173/*`
  - The allowed callback destinations after login. Keep this restricted to
    trusted app URLs so tokens cannot be redirected elsewhere.
- Valid post logout redirect URIs:
  - Value: `http://localhost:5173/*`
  - The allowed destinations after logout. The app logout flow should return
    users only to one of these URLs.
- Web origins:
  - Value: `http://localhost:5173`
  - Controls browser CORS origins for this client. Use the exact dev origin
    instead of `*` for a tighter local setup.

Recommended local logout settings:

- Front channel logout: `Off`
  - When on, Keycloak logs clients out through the user's browser, usually with
    a front-channel URL or iframe. Leave it off until the app has a route that
    intentionally handles this.
- Front-channel logout URL: leave blank
  - The browser URL Keycloak would call during front-channel logout. Blank is
    correct while there is no logout callback route.
- Front-channel logout session required: leave default
  - Controls whether Keycloak includes session and issuer values in the
    front-channel logout request. It only matters when front-channel logout is
    enabled.
- Backchannel logout URL: leave blank
  - The server endpoint Keycloak would call with a logout token. Blank is
    correct while the app does not store its own server-side session.
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

Future logout callback options:

- Use front-channel logout only if the browser app needs Keycloak to call a
  front-channel URL during SSO logout.
- Use backchannel logout for a server-side session endpoint such as
  `http://localhost:5173/auth/backchannel-logout` if the app later stores its
  own server session that must be invalidated when Keycloak logs the user out.

Use Keycloak for login. The app should redirect to Keycloak rather than render
custom login screens.

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

Composite roles and fine-grained permission roles can be revisited later. If the
app grows beyond this simple model, `Admins` can become a composite role that
contains permissions such as `admin-read`, `admin-update`, `admin-delete`, and
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

The future application role helper should normalize those roles into a flat role
list and check for the exact role names documented above.

## Future App Routes

Planned dashboard routes:

```text
/admin
/admin/manage-users
/admin/manage-groups
/admin/manage-group-permissions
/apps
/apps/todos
```

Expected route behavior:

- `/admin` and all Admin child routes require `Admins`.
- Admin edit and delete controls are available to `Admins`.
- `/apps` and `/apps/todos` require an authenticated user with `Users` or
  `Admins`.
- `/apps/todos` is scoped to the current user.

Reusable admin UI should live in the shared components area chosen for this
React Router app, with feature-oriented groups such as:

```text
components/admin/manage-users
components/admin/manage-groups
components/admin/manage-group-permissions
```

Use shadcn UI controls for tables, buttons, forms, dialogs, sidebars, dropdowns,
badges, and navigation primitives.

## Todos And Local User Data

Todos should be persisted in Postgres and scoped to the current Keycloak user.
Use the Keycloak token `sub` claim as the stable user id:

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
- Add a local user profile table later only when app-owned user metadata becomes
  necessary.
