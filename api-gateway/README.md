# API Gateway

Local Traefik gateway for routing browser, mobile, auth, web, and API traffic.

The gateway compose file only runs Traefik. Each app or API service opts into
Traefik by joining the `admin-starter-public` Docker network and adding Docker
labels.

## Local Hosts

The gateway currently reserves these local hostnames:

```text
app.localhost
auth.localhost
api.localhost
api-python.localhost
api-express.localhost
api-dotnet.localhost
```

`api.localhost` is the default friendly API host. Use the technology-specific
hosts when running more than one API example at the same time.

## Start And Stop

From the repo root:

```bash
corepack pnpm gateway:up
corepack pnpm gateway:logs
corepack pnpm gateway:down
```

The full local gateway stack is:

```bash
corepack pnpm dev:gateway
```

## Required API Service Settings

Every API container exposed through Traefik should:

- attach to the external Docker network named `admin-starter-public`
- set `traefik.enable=true`
- set `traefik.docker.network=admin-starter-public`
- route by `Host(...)`
- point the Traefik service port at the API container's internal listen port

## Python/FastAPI Route

Default single-API host:

```yaml
labels:
  - traefik.enable=true
  - traefik.docker.network=admin-starter-public
  - traefik.http.routers.api-python.rule=Host(`api.localhost`)
  - traefik.http.routers.api-python.entrypoints=web
  - traefik.http.services.api-python.loadbalancer.server.port=8000
networks:
  - public

networks:
  public:
    external: true
    name: admin-starter-public
```

Side-by-side API host:

```yaml
- traefik.http.routers.api-python.rule=Host(`api-python.localhost`)
```

## Express Route

```yaml
labels:
  - traefik.enable=true
  - traefik.docker.network=admin-starter-public
  - traefik.http.routers.api-express.rule=Host(`api-express.localhost`)
  - traefik.http.routers.api-express.entrypoints=web
  - traefik.http.services.api-express.loadbalancer.server.port=8001
```

## .NET Route

```yaml
labels:
  - traefik.enable=true
  - traefik.docker.network=admin-starter-public
  - traefik.http.routers.api-dotnet.rule=Host(`api-dotnet.localhost`)
  - traefik.http.routers.api-dotnet.entrypoints=web
  - traefik.http.services.api-dotnet.loadbalancer.server.port=8002
```

## Related Knowledge

- [Gateway routing](../wiki/architecture/gateway-routing.md)
- [Gateway network model](../wiki/architecture/gateway-network-model.md)
- [Traefik static configuration](../wiki/integrations/traefik-static-config.md)
- [Gateway troubleshooting](../wiki/operations/troubleshoot-gateway.md)
- [Express API placeholder](../api-express/README.md)
