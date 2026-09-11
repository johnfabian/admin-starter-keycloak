---
type: Architecture
title: Access control model
description: Implemented route-role mapping and token-role resolution in the React Router BFF.
resource: /web/app/lib/server/route-guards.server.ts
tags: [authorization, roles, keycloak, react-router]
status: draft
generated: { by: codex/gpt-5, at: 2026-08-02T16:44:19Z }
stale_after: 2026-11-02
sources:
  - id: access-settings
    resource: /web/app/lib/app-settings.shared.ts
    title: Application roles and access areas
    last_modified: 2026-05-22
  - id: token-roles
    resource: /web/app/lib/server/current-user.server.ts
    title: Current-user role extraction
    last_modified: 2026-05-21
  - id: route-guards
    resource: /web/app/lib/server/route-guards.server.ts
    title: Server route guards
    last_modified: 2026-05-21
---

# Implemented model

The BFF authorizes guarded routes by exact, case-sensitive role strings. `userRoutes` accepts `Users` or `Admins`; `adminRoutes` accepts only `Admins`. Roles are the de-duplicated union of `realm_access.roles` and `resource_access[WEB_KEYCLOAK_CLIENT_ID].roles` from the verified access token.[^access-settings][^token-roles]

Protected loaders call `requireUserRoute` or `requireAdminRoute`; authentication without one of the accepted roles redirects to `/forbidden`. Navigation visibility is presentation only and is not an authorization boundary.[^route-guards]

# Boundary

- Enforce access in server loaders or another trusted server boundary.
- Treat realm and client roles with the same names as equivalent inputs to the current union.
- Keep any future resource API responsible for its own token validation and authorization.
- Do not infer protection from a route name; a new route is protected only when its loader applies a guard.

# Uncertainty

The local browser suite exercises a declared protected-route matrix for anonymous, no-role, Users, and Admins accounts. That list does not automatically cover future routes; see [automated local verification](/testing/automated-local-verification.md). Live realm role definitions and mappings can drift from the code, so test preflight checks remain necessary.

# Related concepts

- [React Router BFF](/architecture/react-router-bff.md)
- [Realm and client facts](/integrations/keycloak/realm-and-client-facts.md)
- [Express resource API](/integrations/express-resource-api.md)

[^access-settings]: Application roles and access areas

[^token-roles]: Current-user role extraction

[^route-guards]: Server route guards

# Related decision records

These proposals record the decision and tradeoffs; this page retains the current behavior or operational procedure.

- [ADR-0006: Enforce routes server-side using the current role contract (proposed)](/adr/ADR-0006-server-side-role-authorization.md)
