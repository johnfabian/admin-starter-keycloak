# Keycloak Setup Guide

This project uses Keycloak for authentication, identity, groups, and app
permissions. The React application should not implement its own login,
registration, password reset, or permission assignment UI for this starter.

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

All app users, groups, and permission roles for this starter should live in
this realm.

## App Client

Create an application client for this React app:

```text
admin-starter-web
```

Recommended local client settings:

- Client type: `OpenID Connect`
- Client authentication: off for browser-based development unless a server-side
  confidential client is added later
- Standard flow: enabled
- Direct access grants: disabled unless specifically needed for tooling
- Valid redirect URIs:
  - `http://localhost:5173/*`
- Valid post logout redirect URIs:
  - `http://localhost:5173/*`
- Web origins:
  - `http://localhost:5173`

Use Keycloak for login. The app should redirect to Keycloak rather than render
custom login screens.

## Permission Roles

Create these as **client roles** on the `admin-starter-web` client:

```text
admin-read
admin-update
admin-delete
admin-fullcontrol
```

The app should treat these roles as permission strings:

- `admin-read` allows access to the Admin section.
- `admin-update` enables edit actions.
- `admin-delete` enables delete actions.
- `admin-fullcontrol` enables all Admin actions.

Groups are dynamic and should not be hard-coded in the application. Assign
client roles to Keycloak groups, then add users to those groups. The app should
read permissions from the authenticated user's token and make decisions from the
permission roles, not group names.

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

Assign Admin permissions:

1. Open the user.
2. Go to **Role mapping**.
3. Choose **Assign role**.
4. Filter by client roles for `admin-starter-web`.
5. Assign `admin-fullcontrol`.

Alternatively, create a Keycloak group such as `Application Admins`, assign the
`admin-fullcontrol` client role to that group, then add the user to the group.
The group name is only an administration convenience; the application should
only depend on the permission role.

## Token Verification

After sign-in, verify that the user's token contains the assigned client roles.
For the `admin-starter-web` client, Keycloak commonly emits client roles under:

```json
{
  "resource_access": {
    "admin-starter-web": {
      "roles": ["admin-fullcontrol"]
    }
  }
}
```

The future application permission helper should normalize those roles into a
flat permission list and check for the exact role names documented above.

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

- `/admin` and all Admin child routes require `admin-read` or
  `admin-fullcontrol`.
- Edit controls require `admin-update` or `admin-fullcontrol`.
- Delete controls require `admin-delete` or `admin-fullcontrol`.
- `/apps/todos` is an authenticated app route scoped to the current user.

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
Keycloak owns identity, login, groups, and permission-role assignment.

A local users table is optional. Add one only if the application needs
app-owned user profile data, denormalized display names or emails, audit
metadata, or foreign-key convenience for larger domain models.

Recommended starting point for Todos:

- Store `keycloak_user_id` directly on each todo.
- Query todos by the authenticated user's `sub`.
- Never allow one user to query or mutate another user's todos.
- Add a local user profile table later only when app-owned user metadata becomes
  necessary.
