---
type: Architecture
title: Repository implementation boundaries
description: Current runnable packages, infrastructure areas, and placeholder service boundaries in the repository.
tags: [monorepo, boundaries, react-router, express]
status: draft
generated: { by: codex/gpt-5, at: 2026-08-02T15:45:23Z }
stale_after: 2026-11-02
sources:
  - id: workspace
    resource: /pnpm-workspace.yaml
    title: pnpm workspace configuration
    last_modified: 2026-07-28
  - id: root-package
    resource: /package.json
    title: Root package manifest
    last_modified: 2026-08-01
  - id: web-package
    resource: /web/package.json
    title: React Router web package manifest
    last_modified: 2026-05-21
  - id: express-readme
    resource: /api-express/README.md
    title: Express API placeholder documentation
    last_modified: 2026-05-15
---

# Implemented boundary

The pnpm workspace names `web` and `api-express`, but only `web/` currently contains a package manifest and runnable scripts.[^workspace][^web-package] Root commands wrap the web package and Docker Compose services; there is no root Express start/build/test command.[^root-package]

The implemented application boundary is therefore the React Router Framework Mode application under `web/`, supported by Docker-managed Postgres, Keycloak, Traefik, and Mailpit configuration. `api-express/` contains documentation only and explicitly describes itself as a placeholder.[^express-readme]

# Retrieval guidance

- Retrieve [React Router BFF](/architecture/react-router-bff.md) for browser, auth, route, or server-loader changes.
- Retrieve [Express resource API](/integrations/express-resource-api.md) before work under `api-express/`.
- Do not infer that a workspace entry is a runnable service without a manifest and source.

# Uncertainty

The repository README mentions additional future application directories that are not present in the tracked tree. Their architecture is not part of this baseline.

[^workspace]: pnpm workspace configuration

[^root-package]: Root package manifest

[^web-package]: React Router web package manifest

[^express-readme]: Express API placeholder documentation
