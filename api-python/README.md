# API Python

Placeholder for the FastAPI resource server.

When implemented, this service should validate Keycloak access tokens, enforce
API roles, and expose business/resource endpoints behind Traefik at
`api.localhost` locally and `api.example.com` in production.

## Local URLs

```text
Direct local API: http://localhost:8000
Traefik local API: http://api.localhost
Alternative local host: http://api-python.localhost
Production API: https://api.example.com
```

Use `api.localhost` as the default Python API hostname while this is the primary
API example. Use `api-python.localhost` if you want all API examples running
side by side.

## Environment

Expected local values:

```env
KEYCLOAK_ISSUER=http://auth.localhost/realms/admin-starter
API_PYTHON_KEYCLOAK_AUDIENCE=admin-starter-api-python
API_PYTHON_EXTERNAL_URL=http://api.localhost
```

For direct local development without Traefik:

```env
KEYCLOAK_ISSUER=http://localhost:8080/realms/admin-starter
API_PYTHON_EXTERNAL_URL=http://localhost:8000
```

## Keycloak Setup

Create a dedicated Keycloak client for the Python/FastAPI resource server.

1. Open the `admin-starter` realm.
2. Go to **Clients**.
3. Create client.
4. Set **Client type** to `OpenID Connect`.
5. Set **Client ID** to `admin-starter-api-python`.
6. Turn **Client authentication** `Off` to start.
7. Turn **Authorization** `Off`.
8. Turn **Standard flow** `Off`.
9. Turn **Direct access grants** `Off`.
10. Turn **Implicit flow** `Off`.
11. Turn **Service accounts roles** `Off` unless the API needs machine-to-machine auth.
12. Set Root URL and Home URL to `http://api.localhost` locally.
13. Leave Valid redirect URIs blank unless an API docs/admin tool needs redirects.
14. Leave Web origins blank; configure CORS in FastAPI.
15. Save.

Create client roles on `admin-starter-api-python`:

```text
api-users
api-admins
```

Assign roles through groups:

```text
Application Users  -> admin-starter-api-python:api-users
Application Admins -> admin-starter-api-python:api-admins
```

## Audience Mapper

Tokens issued to the web and mobile clients should include the Python API in
the `aud` claim.

1. Go to **Client scopes**.
2. Create `admin-starter-api-python-audience`.
3. Open the client scope.
4. Go to **Mappers**.
5. Configure a new **Audience** mapper.
6. Name it `admin-starter-api-python-audience`.
7. Set **Included Client Audience** to `admin-starter-api-python`.
8. Turn **Add to access token** on.
9. Save.
10. Add this client scope as a default scope on `admin-starter-web`.
11. Add this client scope as a default scope on `admin-starter-mobile`.

The API should validate:

- token signature using the realm JWKS
- `iss` equals `KEYCLOAK_ISSUER`
- `aud` includes `API_PYTHON_KEYCLOAK_AUDIENCE`
- required roles are present in `resource_access.admin-starter-api-python.roles`

## Traefik Setup

When the API container exists, attach it to `admin-starter-public` and add
labels like this:

```yaml
labels:
  - traefik.enable=true
  - traefik.docker.network=admin-starter-public
  - traefik.http.routers.api-python.rule=Host(`api.localhost`)
  - traefik.http.routers.api-python.entrypoints=web
  - traefik.http.services.api-python.loadbalancer.server.port=8000
```

If running all API examples at once, use:

```yaml
- traefik.http.routers.api-python.rule=Host(`api-python.localhost`)
```

See [../api-gateway/README.md](../api-gateway/README.md) for the shared gateway
rules and [../docs/keycloak-roles-and-permissions.md](../docs/keycloak-roles-and-permissions.md)
for the authorization model.
