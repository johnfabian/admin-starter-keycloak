# Keycloak Roles, Permissions, Organizations, And Multi-Tenancy

This guide explains the identity and authorization model for this project. Use
it with [keycloak-setup.md](keycloak-setup.md), which has the click-by-click
setup values.

## Recommended Model

Use one Keycloak realm per environment:

```text
local/dev: admin-starter
staging:   admin-starter-staging
prod:      admin-starter-prod
```

Inside each realm, use separate clients for each application surface:

```text
admin-starter-web          React Router browser app
admin-starter-api-express  Express resource server (not built yet)
```

Any additional resource server follows the same convention:
`admin-starter-api-<name>`.

Use groups for assigning app access:

```text
Application Users
Application Admins
```

Use client roles for what the app/API authorizes:

```text
admin-starter-web:Users
admin-starter-web:Admins
admin-starter-api-express:api-users
admin-starter-api-express:api-admins
```

Use Organizations when the product needs B2B tenants, customer workspaces,
partner organizations, organization-scoped login, organization invitations, or
organization-aware identity providers.

## Core Concepts

### Realms

A realm is an isolated identity boundary. A realm owns users, credentials,
roles, groups, clients, identity providers, sessions, and token settings. Users
log into a realm, and one realm cannot directly manage or authenticate users
from another realm.

Use realms for hard isolation:

- separate production from staging and development
- separate unrelated products
- separate customers only when legal, compliance, operational, or data
  isolation requirements justify the extra complexity
- isolate radically different login policies or identity provider rules

Avoid creating one realm per customer by default. Multi-realm systems are
harder to operate because every client, mapper, theme, identity provider,
password policy, and token setting must be repeated or automated per realm.

### Clients

A client represents an app, API, CLI, service, or other thing that asks
Keycloak to authenticate users or issue tokens.

For this project:

- `admin-starter-web` is the browser-facing React Router app.
- `admin-starter-api-express` represents the Express resource server and token
  audience.

The client boundary matters because roles are usually scoped to clients. A user
can be an admin in the web app without automatically receiving API admin
permissions unless those roles are also assigned.

### Realm Roles

Realm roles belong to the whole realm. They are useful for broad identity-level
meaning such as:

```text
realm:platform-admin
realm:support-operator
realm:billing-admin
```

Use realm roles sparingly in this project. They are broad by design and can
become ambiguous when the realm contains multiple apps.

### Client Roles

Client roles belong to one client. They are the best default for application
authorization because the role's owner is clear:

```text
admin-starter-web:Admins
admin-starter-api-express:api-admins
```

Use client roles for:

- route access in the React Router app
- API access in Express
- admin UI visibility
- coarse product permissions

The web app should read `admin-starter-web` roles. The API should read
`admin-starter-api-express` roles. A client may display UI from token claims, but the API
must still enforce permissions server-side.

### Composite Roles

A composite role contains other roles. If a user receives the composite role,
the user effectively receives the roles inside it.

Example:

```text
admin-starter-web:Admins
  includes admin-starter-web:Users
  includes admin-starter-api-express:api-users
  includes admin-starter-api-express:api-admins
```

Composite roles are useful when one role should imply another. They can also
hide complexity, so document them clearly and avoid deep nesting.

Good use cases:

- `Admins` includes `Users`
- `api-admins` includes `api-users`
- `support-admin` includes read-only support permissions

Risky use cases:

- large composites that include unrelated permissions
- composites used as a substitute for tenant membership checks
- composites that cross too many clients without documentation

### Groups

Groups are an administration tool for assigning roles and attributes to users.
Users inherit role mappings from their groups.

Recommended groups:

```text
Application Users
  role mappings:
    admin-starter-web:Users
    admin-starter-api-express:api-users

Application Admins
  role mappings:
    admin-starter-web:Admins
    admin-starter-api-express:api-admins
```

Use groups for:

- assigning many users the same app access
- making admin work easier
- mapping external IdP groups to local app access
- onboarding users through a predictable access package

Do not hard-code group names in the app as authorization checks. Groups are
admin organization. Roles are application permissions.

## Permission Layers

Think about permissions in layers:

```text
Keycloak
  authenticates users
  issues identity, role, audience, and organization claims

React Router app
  protects browser routes
  manages the web session cookie
  shows or hides UI affordances

Express
  validates bearer tokens
  enforces API roles
  enforces tenant and resource ownership

Postgres
  stores app data
  scopes records by user id, organization id, or tenant id
```

Keycloak should answer:

- Who is the user?
- Which app/API roles does the user have?
- Which organizations is the user a member of?
- Which identity provider authenticated the user?

Express should answer:

- Is the token valid?
- Was this token intended for this API?
- Does the user have the required API role?
- Does the user belong to the tenant/organization for this record?
- Does the user own or have permission to mutate this resource?

Do not rely on front-end checks alone. Browser UI checks are helpful
for usability, but the API is the enforcement point for protected data.

## Token Claims

Client roles commonly appear in access tokens under `resource_access`:

```json
{
  "resource_access": {
    "admin-starter-web": {
      "roles": ["Users"]
    },
    "admin-starter-api-express": {
      "roles": ["api-users"]
    }
  }
}
```

Realm roles commonly appear under `realm_access`:

```json
{
  "realm_access": {
    "roles": ["platform-admin"]
  }
}
```

When the API audience mapper is configured, access tokens issued for the web
client should include the API audience:

```json
{
  "aud": ["admin-starter-api-express"]
}
```

Express should validate `iss`, `aud`, signature, expiration, and required
roles. A token that lacks `admin-starter-api-express` in `aud` should not be accepted by
the API.

## Organizations

Organizations are Keycloak's model for B2B or CIAM-style tenants inside a
realm. They are useful when the realm serves multiple companies, customers,
partners, or workspaces.

Use Organizations for:

- customer tenants in a SaaS product
- partner companies
- business accounts with multiple members
- organization invitations and membership
- organization-specific identity providers
- organization claims in tokens

Organizations are not a replacement for application data permissions. The app
and API still need tenant-scoped Postgres records and server-side authorization.

### Organization Claims

Keycloak has a built-in optional `organization` client scope. When the app asks
for this scope, Keycloak can include organization membership information in the
token.

Example shape:

```json
{
  "organization": {
    "acme": {
      "id": "42c3e46f-2477-44d7-a85b-d3b43f6b31fa"
    }
  }
}
```

The `organization` scope can be requested in different forms:

```text
organization
organization:<alias>
organization:*
```

Use `organization:<alias>` when the app already knows which tenant/workspace
the user is trying to access. Use `organization` when the user has one
organization or can choose during login. Use `organization:*` carefully because
it can put all organization memberships into the token.

### Organization Identity Providers

Organizations can be paired with identity providers for B2B login flows. This
lets a customer organization use its own identity provider while users still
land in the shared `admin-starter` realm.

Example:

```text
Organization: acme
Identity provider: Acme Azure AD / OIDC
Members: Acme employees
Token claim: organization.acme
```

The app still needs to enforce which organization is active for a request.
Membership in `acme` should not automatically authorize access to every Acme
record unless the API checks the matching tenant id and role.

## Groups Vs Organizations

Groups and Organizations solve different problems.

| Concept       | Best For                                               | App Should Use For                          |
| ------------- | ------------------------------------------------------ | ------------------------------------------- |
| Roles         | Permissions and capabilities                           | Authorization checks                        |
| Groups        | Admin-managed access packages and inherited role maps  | Assignment convenience, not hard-coded auth |
| Organizations | B2B tenants, customer workspaces, org-specific login   | Tenant membership and tenant context        |
| Realms        | Hard isolation of users, clients, policies, and config | Environment or strong tenant isolation      |

Practical rule:

- Use roles to decide what a user can do.
- Use organizations to decide where the user can do it.
- Use groups to assign the roles efficiently.
- Use realms when isolation matters more than shared administration.

## Multi-Tenant Patterns

### Single Realm, Organizations As Tenants

Recommended default for this project when B2B tenancy is needed.

```text
Realm: admin-starter-prod
  Organization: acme
  Organization: globex
  Organization: initech
  Clients: web, api
```

Pros:

- one client setup to maintain
- one login domain
- shared app and API clients
- organization claims can describe tenant membership
- easier to support users who belong to multiple tenants

Cons:

- not a hard isolation boundary
- app/API/Postgres must enforce tenant isolation carefully
- tenant-specific policies may require more custom logic

Use this when tenants share the same product, same deployment, same auth
policies, and same operational environment.

### Realm Per Tenant

```text
Realm: acme
Realm: globex
Realm: initech
```

Pros:

- stronger administrative isolation
- separate client secrets, users, policies, identity providers, and sessions
- useful for regulated or highly isolated customers

Cons:

- every client and mapper must be repeated
- operational overhead grows with each tenant
- cross-tenant users are harder
- app/API must choose the correct issuer and JWKS per request

Use this only when the product requires strong tenant isolation, separate
identity policy, or customer-specific Keycloak administration.

### Hybrid

Use one realm per environment for normal customers, and separate realms for
exceptional customers that require hard isolation.

Example:

```text
admin-starter-prod
  org: acme
  org: globex

admin-starter-prod-bank-customer
  dedicated realm for one regulated customer
```

This is operationally more complex, but it keeps normal tenants simple while
allowing exceptions.

## Recommended Tenant Authorization Flow

For a tenant-scoped API request:

```text
GET /organizations/acme/todos
Authorization: Bearer <token>
```

Express should:

1. Validate token signature against Keycloak JWKS.
2. Validate `iss`.
3. Validate `aud` includes `admin-starter-api-express`.
4. Validate the user has `admin-starter-api-express:api-users` or
   `admin-starter-api-express:api-admins`.
5. Validate the token organization claim includes `acme`, or look up
   membership server-side.
6. Query data with a tenant filter such as `organization_id = acme-id`.
7. Apply resource ownership or admin checks before returning data.

Never trust a path like `/organizations/acme` by itself. The path is only the
requested tenant. The token and Postgres decide whether access is allowed.

## Authorization Services

Keycloak Authorization Services are a separate feature for resource, scope,
policy, permission, UMA, and RPT-based authorization.

This starter does not need Authorization Services for the first pass. Client
roles plus API-side checks are easier to reason about.

Consider Authorization Services only when:

- permissions become resource-level and centrally managed in Keycloak
- admins need to define policies without changing API code
- UMA-style permission tickets are required
- the product needs Keycloak to be the central policy decision point

If Authorization Services are enabled, document the resource model carefully.
They add power, but also complexity.

## Naming Conventions

Use stable, boring names. They age better.

Clients:

```text
admin-starter-web
admin-starter-api-express
```

Web roles:

```text
Users
Admins
```

API roles:

```text
api-users
api-admins
```

Groups:

```text
Application Users
Application Admins
Tenant Admins
Tenant Members
```

Organizations:

```text
acme
globex
initech
```

Prefer immutable organization aliases. If a company changes its display name,
change the display name, not the alias used by URLs and Postgres records.

## Common Mistakes

- Checking group names in app code instead of roles.
- Accepting API tokens without validating `aud`.
- Treating a role like `Admins` as tenant membership.
- Putting every permission into realm roles.
- Enabling `Full scope allowed` and exposing more roles than needed.
- Reusing the browser client for a different application surface.
- Putting a client secret in a public client.
- Creating one realm per customer before the product actually needs hard
  isolation.
- Assuming organization membership alone protects data without API checks.
- Letting front-end route guards be the only authorization layer.

## Setup Checklist

- Create realm `admin-starter`.
- Create clients `admin-starter-web` and `admin-starter-api-express`.
- Create web roles `Users` and `Admins`.
- Create API roles `api-users` and `api-admins`.
- Create groups `Application Users` and `Application Admins`.
- Assign client roles to groups.
- Add users to groups, not directly to roles, unless testing.
- Create `admin-starter-api-express-audience` client scope.
- Add the API audience scope to the web client.
- Keep `Full scope allowed` off once role scope mappings are explicit.
- Add organizations when tenant membership is needed.
- Request `organization` scope only when the app/API needs organization claims.
- Enforce tenant permissions in Express.

## References

- Keycloak Server Administration Guide:
  <https://www.keycloak.org/docs/latest/server_admin/>
- Keycloak roles, groups, and composite roles:
  <https://www.keycloak.org/docs/latest/server_admin/#assigning-permissions-using-roles-and-groups>
- Keycloak clients:
  <https://www.keycloak.org/docs/latest/server_admin/#_clients>
- Keycloak OIDC advanced client settings:
  <https://www.keycloak.org/docs/latest/server_admin/#_oidc-advanced-settings>
- Keycloak organizations:
  <https://www.keycloak.org/docs/latest/server_admin/#_organizations>
- Keycloak organization claims:
  <https://www.keycloak.org/docs/latest/server_admin/#mapping-organization-claims>
- Keycloak securing applications and services:
  <https://www.keycloak.org/docs/latest/securing_apps/>
