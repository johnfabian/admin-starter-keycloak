# API Gateway

Local Traefik gateway for routing browser, auth, web, and API traffic.

The gateway compose file only runs Traefik. Each app or API service opts into
Traefik by joining the `admin-starter-public` Docker network and adding Docker
labels.

## Local Hosts

The gateway currently reserves these local hostnames:

```text
app.localhost
auth.localhost
api.localhost
api-express.localhost
```

`api.localhost` is the default friendly API host. `api-express.localhost` is
reserved for the Express resource server so both can be routed at once.

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

## Express Route

```yaml
labels:
  - traefik.enable=true
  - traefik.docker.network=admin-starter-public
  - traefik.http.routers.api-express.rule=Host(`api-express.localhost`)
  - traefik.http.routers.api-express.entrypoints=web
  - traefik.http.services.api-express.loadbalancer.server.port=8001
networks:
  - public

networks:
  public:
    external: true
    name: admin-starter-public
```

To serve it on the default `api.localhost` host instead:

```yaml
- traefik.http.routers.api-express.rule=Host(`api.localhost`)
```

## Related Docs

- [Traefik guide](../docs/traefik-guide.md)
- [Express API setup](../api-express/README.md)
