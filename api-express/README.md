# API Express

Placeholder for the Express API resource server.

When implemented, this service should validate Keycloak access tokens, enforce
API roles, and expose business/resource endpoints behind Traefik at a local API
hostname or path chosen for the Express example.

## Local URLs

```text
Direct local API: http://localhost:8001
Traefik local API: http://api-express.localhost
Production API: https://api-express.example.com
```

## Environment

Expected local values:

```env
KEYCLOAK_ISSUER=http://auth.localhost/realms/admin-starter
API_EXPRESS_KEYCLOAK_AUDIENCE=admin-starter-api-express
API_EXPRESS_EXTERNAL_URL=http://api-express.localhost
```

For direct local development without Traefik:

```env
KEYCLOAK_ISSUER=http://localhost:8080/realms/admin-starter
API_EXPRESS_EXTERNAL_URL=http://localhost:8001
```

## Keycloak Setup

Create a dedicated Keycloak client for the Express resource server.

1. Open the `admin-starter` realm.
2. Go to **Clients**.
3. Create client.
4. Set **Client type** to `OpenID Connect`.
5. Set **Client ID** to `admin-starter-api-express`.
6. Turn **Client authentication** `Off` to start.
7. Turn **Authorization** `Off`.
8. Turn **Standard flow** `Off`.
9. Turn **Direct access grants** `Off`.
10. Turn **Implicit flow** `Off`.
11. Turn **Service accounts roles** `Off` unless the API needs machine-to-machine auth.
12. Set Root URL and Home URL to `http://api-express.localhost` locally.
13. Leave Valid redirect URIs blank unless an API documentation or admin tool needs redirects.
14. Leave Web origins blank; configure CORS in Express.
15. Save.

Create client roles on `admin-starter-api-express`:

```text
api-users
api-admins
```

Assign roles through groups:

```text
Application Users  -> admin-starter-api-express:api-users
Application Admins -> admin-starter-api-express:api-admins
```

## Audience Mapper

Tokens issued to the web and mobile clients should include the Express API in
the `aud` claim.

1. Go to **Client scopes**.
2. Create `admin-starter-api-express-audience`.
3. Open the client scope.
4. Go to **Mappers**.
5. Configure a new **Audience** mapper.
6. Name it `admin-starter-api-express-audience`.
7. Set **Included Client Audience** to `admin-starter-api-express`.
8. Turn **Add to access token** on.
9. Save.
10. Add this client scope as a default scope on `admin-starter-web`.
11. Add this client scope as a default scope on `admin-starter-mobile`.

The API should validate:

- token signature using the realm JWKS
- `iss` equals `KEYCLOAK_ISSUER`
- `aud` includes `API_EXPRESS_KEYCLOAK_AUDIENCE`
- required roles are present in `resource_access.admin-starter-api-express.roles`

## Traefik Setup

When the API container exists, attach it to `admin-starter-public` and add
labels like this:

```yaml
labels:
  - traefik.enable=true
  - traefik.docker.network=admin-starter-public
  - traefik.http.routers.api-express.rule=Host(`api-express.localhost`)
  - traefik.http.routers.api-express.entrypoints=web
  - traefik.http.services.api-express.loadbalancer.server.port=8001
```

See [../api-gateway/README.md](../api-gateway/README.md) for the shared gateway
rules. The current authorization behavior and this placeholder's actual repository
state are recorded in the [access-control model](../wiki/architecture/access-control-model.md)
and [Express resource API concept](../wiki/integrations/express-resource-api.md).
