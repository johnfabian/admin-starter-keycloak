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
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<local-password>
POSTGRES_DB=admin_starter

KEYCLOAK_ADMIN_USER=<bootstrap-admin-username>
KEYCLOAK_ADMIN_PASSWORD=<bootstrap-admin-password>
KEYCLOAK_HOSTNAME=localhost
```

Start Postgres and Keycloak from the project root:

```bash
docker compose -f docker/docker-compose.yml --env-file .env.development up -d --wait
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
npm run docker:traefik:up
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
`api.localhost` for the FastAPI service when the API stack is running.

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
     postgres: ...
   ```

2. Or pass the project name when running Compose:

   ```bash
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
  - `admin-starter-api-audience` after the API audience scope is created
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
  - Allow `admin-starter-api:api-users`
  - Allow `admin-starter-api:api-admins`

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

Local app logout clears the app session cookie and returns to
`AUTH_POST_LOGOUT_REDIRECT_URI`. Full Keycloak SSO logout requires server-side
session storage for the ID token, because Keycloak may require `id_token_hint`
on the end-session request.

Logout callback options:

- Use front-channel logout only if the browser app needs Keycloak to call a
  front-channel URL during SSO logout.
- Use backchannel logout for a server-side session endpoint such as
  `http://localhost:5173/auth/backchannel-logout` if the app stores its own
  server session that must be invalidated when Keycloak logs the user out.

Use Keycloak for login. The app should redirect to Keycloak rather than render
custom login screens. This app uses React Router framework-mode server routes
with an HttpOnly session cookie instead of storing tokens in browser
`localStorage`. Store only compact user identity and role data in that cookie.
Store Keycloak tokens in a server-side session table before the BFF forwards
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

## FastAPI API Client

Keep the FastAPI resource server behind Traefik at:

```text
http://api.localhost
```

In production, use:

```text
https://api.example.com
```

FastAPI should not use the browser cookie session from the React Router app.
It should validate Keycloak access tokens sent as bearer tokens:

```http
Authorization: Bearer <access-token>
```

Create a separate Keycloak client to represent the API:

```text
admin-starter-api
```

Recommended API client settings:

- Client type: `OpenID Connect`
  - Keeps the API represented in the same OIDC realm as the web and mobile
    clients.
- Client authentication: `Off` to start
  - Use this if the client exists only as a token audience and role container.
    Turn it on only if the API needs confidential client credentials for
    machine-to-machine calls.
- Authorization: `Off`
  - Leave Keycloak Authorization Services off unless the API intentionally
    adopts Keycloak resources, scopes, policies, UMA, and RPT tokens.
- Standard flow: `Off`
  - The API should not redirect users to login.
- Direct access grants: `Off`
  - Do not let the API client accept username/password grant requests.
- Implicit flow: `Off`
  - The API should never receive tokens from an implicit browser flow.
- Service accounts roles: `Off` to start
  - Turn this on only if a trusted background process needs client credentials.
- Root URL:
  - Local Traefik value: `http://api.localhost`
  - Production value: `https://api.example.com`
- Home URL:
  - Local Traefik value: `http://api.localhost`
  - Production value: `https://api.example.com`
- Valid redirect URIs:
  - Leave blank if Keycloak allows it for this client, or set only the exact API
    admin/docs URL if a tool requires redirects.
- Web origins:
  - Leave blank to start.
  - Keycloak web origins affect browser calls to Keycloak, not FastAPI CORS.
    Configure FastAPI CORS separately in the API.

Recommended API client scopes and advanced settings:

- Default client scopes:
  - `roles`
- Optional client scopes:
  - `organization` if the API authorizes tenant access from organization claims
- Full scope allowed: `Off`
  - The API should receive only the role and audience claims it needs.
- Role scope mappings:
  - Allow `admin-starter-api:api-users`
  - Allow `admin-starter-api:api-admins`
- Advanced tab:
  - Access Token Lifespan: leave empty to inherit the realm `5 minutes`
  - Client Session Idle: leave empty unless service accounts are enabled
  - Client Session Max: leave empty unless service accounts are enabled
  - Client Offline Session Idle: leave empty
  - Client Offline Session Max: leave empty
  - Proof Key for Code Exchange Code Challenge Method: leave blank
  - OAuth 2.0 Device Authorization Grant: `Off`
  - OIDC CIBA Grant: `Off`
  - Valid request URIs: leave blank
  - Access Token Signature Algorithm: `RS256`

Recommended API roles on the `admin-starter-api` client:

```text
api-users
api-admins
```

Assign these roles to the same Keycloak groups that receive the web roles:

- `Application Users` group: `admin-starter-web:Users` and
  `admin-starter-api:api-users`
- `Application Admins` group: `admin-starter-web:Admins` and
  `admin-starter-api:api-admins`

The API can then authorize from `resource_access.admin-starter-api.roles`
instead of depending on browser-app roles. This keeps the API permission model
portable for both web and mobile clients.

The mobile client does not need its own app roles at first. Assign user access
through the web and API client roles, then let the Expo app display UI based on
the token claims it receives.

### API Audience Mapper

FastAPI should validate that access tokens were intended for the API. To make
that practical, add an audience mapper so tokens issued to the web and mobile
clients include `admin-starter-api` in the `aud` claim.

Recommended setup:

1. Go to **Client scopes**.
2. Create a client scope named `admin-starter-api-audience`.
3. Set protocol to `openid-connect`.
4. Open the new client scope.
5. Go to **Mappers**.
6. Choose **Configure a new mapper**.
7. Choose **Audience**.
8. Name it `admin-starter-api-audience`.
9. Set **Included Client Audience** to `admin-starter-api`.
10. Turn **Add to access token** on.
11. Save.
12. Open the `admin-starter-web` client.
13. Add `admin-starter-api-audience` as a default client scope.
14. Repeat for the `admin-starter-mobile` client.

Suggested FastAPI validation settings:

```env
KEYCLOAK_ISSUER=http://auth.localhost/realms/admin-starter
KEYCLOAK_AUDIENCE=admin-starter-api
KEYCLOAK_JWKS_URL=http://auth.localhost/realms/admin-starter/protocol/openid-connect/certs
```

Production values should use HTTPS:

```env
KEYCLOAK_ISSUER=https://auth.example.com/realms/admin-starter
KEYCLOAK_AUDIENCE=admin-starter-api
KEYCLOAK_JWKS_URL=https://auth.example.com/realms/admin-starter/protocol/openid-connect/certs
```

## Expo Mobile Client

Create a separate mobile client for the React Native Expo app:

```text
admin-starter-mobile
```

Do not reuse `admin-starter-web` for native mobile. The web app uses a
server-side React Router/BFF session cookie. Native mobile should use OIDC
Authorization Code with PKCE and a mobile redirect URI.

Recommended mobile client settings:

- Client type: `OpenID Connect`
  - Expo mobile auth should use OIDC.
- Client authentication: `Off`
  - Native mobile apps are public clients. Do not put a client secret in the
    Expo app.
- Authorization: `Off`
  - Keep Keycloak Authorization Services off unless the mobile/API permission
    model intentionally adopts them.
- Standard flow: `On`
  - Enables Authorization Code flow.
- Direct access grants: `Off`
  - Avoid password grant from the mobile app.
- Implicit flow: `Off`
  - Do not return tokens directly from the authorization endpoint.
- Service accounts roles: `Off`
  - Mobile apps should not use service accounts.
- PKCE method: `S256`
  - Required for native mobile OAuth clients.
- Root URL:
  - Leave blank for native-only mobile, or use the Expo web URL if this client
    also supports web.
- Home URL:
  - Leave blank for native-only mobile.
- Valid redirect URIs:
  - `adminstarter://auth/callback`
  - `adminstarter:///auth/callback` if Expo generates a triple-slashed value
  - `com.yourcompany.adminstarter://auth/callback` if you choose a reverse-DNS
    scheme
- Valid post logout redirect URIs:
  - `adminstarter://auth/logout`
  - `adminstarter:///auth/logout` if Expo generates a triple-slashed value
- Web origins:
  - Leave blank for native-only mobile.
  - Add the exact Expo web origin only if the mobile app also ships as web.

Recommended mobile client scopes and advanced settings:

- Default client scopes:
  - `profile`
  - `email`
  - `roles`
  - `admin-starter-api-audience`
- Optional client scopes:
  - `organization`
  - `offline_access` only if the mobile app needs long-lived refresh after app
    restarts
- Full scope allowed: `Off`
  - Keep mobile tokens tight. Add only the API and web roles the app needs.
- Role scope mappings:
  - Allow `admin-starter-api:api-users`
  - Allow `admin-starter-api:api-admins`
  - Allow `admin-starter-web:Users` if the app displays shared app roles
  - Allow `admin-starter-web:Admins` if the app exposes admin UI
- Advanced tab:
  - Access Token Lifespan: leave empty to inherit the realm `5 minutes`
  - Client Session Idle: `30 minutes` or shorter
  - Client Session Max: `8 hours` or shorter
  - Client Offline Session Idle: set only if `offline_access` is used
  - Client Offline Session Max: set only if `offline_access` is used
  - Proof Key for Code Exchange Code Challenge Method: `S256`
  - OAuth 2.0 Device Authorization Grant: `Off`
  - OIDC CIBA Grant: `Off`
  - Valid request URIs: leave blank
  - Access Token Signature Algorithm: `RS256`

In the Expo app, log the exact value returned by
`AuthSession.makeRedirectUri()` during setup and add that exact value to
Keycloak. Redirect URI mismatches are the most common mobile auth setup issue.

Expected Expo auth packages:

```bash
npx expo install expo-auth-session expo-web-browser expo-crypto expo-secure-store
```

Recommended Expo environment values:

```env
EXPO_PUBLIC_KEYCLOAK_ISSUER=http://auth.localhost/realms/admin-starter
EXPO_PUBLIC_KEYCLOAK_CLIENT_ID=admin-starter-mobile
EXPO_PUBLIC_API_URL=http://api.localhost
```

These `EXPO_PUBLIC_*` values are bundled into the app. They are fine for public
URLs and public client IDs, but never put secrets there.

Mobile tokens should be stored with `expo-secure-store`, not AsyncStorage or
plain local files. Access tokens should be short-lived. If the app uses refresh
tokens or offline sessions, treat them as sensitive session credentials and
clear them on logout.

## Expo Simulator And Device Development

Expo OAuth/OIDC testing should use a development build, not Expo Go. Expo Go is
excellent for simple UI work, but customized OAuth redirect schemes need a
development build that belongs to your app.

Recommended mobile app setup:

```bash
npx expo install expo-dev-client
```

Add a stable scheme in the Expo app config:

```json
{
  "expo": {
    "scheme": "adminstarter"
  }
}
```

Then use `AuthSession.makeRedirectUri()` in the app and register the generated
redirect URI in Keycloak.

### iPhone Simulator

The iPhone Simulator requires macOS and Xcode. It cannot run directly on this
Windows development machine. To test iOS without a physical iPhone, use one of
these options:

- develop on a Mac with Xcode installed
- use a remote Mac, Mac mini, or Mac cloud provider
- build with EAS for an iOS Simulator target, then run that build on a Mac's
  Simulator

On a Mac:

1. Install Xcode from the Mac App Store.
2. Open Xcode once so it can finish installing required components.
3. Install an iOS Simulator runtime if Xcode prompts for one.
4. Install the Expo app dependencies.
5. Create or run the development build:

   ```bash
   npx expo run:ios
   ```

6. Start the Expo dev server for the development client:

   ```bash
   npx expo start --dev-client
   ```

7. Press `i` in the Expo terminal if the simulator is not already open.

For local Keycloak testing from the iOS Simulator on the same Mac, the simulator
can usually reach services on the Mac through `localhost`. If Traefik is running
on another machine, use a LAN-reachable hostname or an HTTPS tunnel and update
both the Expo env vars and Keycloak redirect/client settings.

### Android Emulator

The Android Emulator is the practical no-phone simulator option on Windows.

Recommended setup:

1. Install Android Studio.
2. In Android Studio, install the Android SDK, Android SDK Platform-Tools,
   Android SDK Build-Tools, and Android Emulator.
3. Open **Device Manager**.
4. Create a virtual device, for example a recent Pixel device.
5. Choose a current stable Android system image.
6. Start the emulator.
7. From the Expo project, create or run the development build:

   ```bash
   npx expo run:android
   ```

8. Start the Expo dev server for the development client:

   ```bash
   npx expo start --dev-client
   ```

For Android Emulator networking, `localhost` points at the emulator itself.
Use Android's special host alias for services running on the development
machine:

```text
http://10.0.2.2
```

If Traefik is on the Windows host and listening on port `80`, the Android
Emulator can usually reach it through:

```text
http://10.0.2.2
```

Host-based routing still needs the `Host` header to be `auth.localhost` or
`api.localhost`, so plain `10.0.2.2` is not a perfect substitute for Traefik
host rules. For smoother mobile auth testing, prefer one of these:

- a LAN DNS name that resolves to the development machine
- a local DNS/hosts setup in the emulator
- a temporary HTTPS tunnel with stable auth and API hostnames
- direct Keycloak/API ports only for early mobile experiments, then Traefik
  hostnames before integration testing

When using a tunnel or LAN hostname, update:

- Expo `EXPO_PUBLIC_KEYCLOAK_ISSUER`
- Expo `EXPO_PUBLIC_API_URL`
- Keycloak mobile client redirect URIs
- Keycloak web origins if testing Expo web
- API `KEYCLOAK_ISSUER` and `KEYCLOAK_AUDIENCE`

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

Dashboard routes:

```text
/admins/dashboard
/admins/manage-users
/admins/manage-groups
/admins/manage-group-permissions
/users/dashboard
/apps
/apps/todos
```

Expected route behavior:

- `/admins` and all Admin child routes require `Admins`.
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
- Add a local user profile table only when app-owned user metadata becomes
  necessary.

## References

- Expo authentication with OAuth or OpenID providers:
  <https://docs.expo.dev/guides/authentication/>
- Expo development builds:
  <https://docs.expo.dev/develop/development-builds/introduction/>
- Expo iOS Simulator:
  <https://docs.expo.dev/workflow/ios-simulator/>
- Expo Android Emulator:
  <https://docs.expo.dev/workflow/android-studio-emulator/>
- Expo SecureStore:
  <https://docs.expo.dev/versions/latest/sdk/securestore/>
- Local roles and permissions guide:
  [keycloak-roles-and-permissions.md](keycloak-roles-and-permissions.md)
- Keycloak securing applications and services:
  <https://www.keycloak.org/docs/latest/securing_apps/>
- Keycloak server administration:
  <https://www.keycloak.org/docs/latest/server_admin/>
