---
type: Integration
title: Express resource API
description: Current placeholder status and documented boundary for a future Express resource server.
resource: /api-express
tags: [express, api, placeholder, keycloak]
status: draft
generated: { by: codex/gpt-5, at: 2026-08-02T15:45:23Z }
stale_after: 2026-10-02
sources:
  - id: express-readme
    resource: /api-express/README.md
    title: Express API placeholder documentation
    last_modified: 2026-05-15
  - id: workspace
    resource: /pnpm-workspace.yaml
    title: pnpm workspace configuration
    last_modified: 2026-07-28
  - id: root-package
    resource: /package.json
    title: Root package manifest
    last_modified: 2026-08-01
---

# Repository state

`api-express/` contains only a README and explicitly identifies itself as a placeholder.[^express-readme] Although the directory is named in the pnpm workspace, it has no package manifest, source, start/build command, test command, or Compose service.[^workspace][^root-package]

# Documented seam

The placeholder documentation describes a possible Keycloak-protected resource API with issuer, signature, audience, and role validation behind Traefik.[^express-readme] Treat every endpoint, client, port, role policy, and deployment statement there as proposed until code, configuration, and tests exist.

# Boundary

The implemented browser session/BFF currently remains in `web/`. A resource API must validate its own bearer token and request authorization rather than trusting the browser or BFF's route decision. Creating the service requires explicit contracts, audience and role decisions, real package tooling, tests, and gateway configuration.

# Related concepts

- [Repository implementation boundaries](/architecture/repository-boundaries.md)
- [React Router BFF](/architecture/react-router-bff.md)
- [Access control model](/architecture/access-control-model.md)
- [Realm and client facts](/integrations/keycloak/realm-and-client-facts.md)
- [Verification baseline](/testing/verification-baseline.md)

[^express-readme]: Express API placeholder documentation

[^workspace]: pnpm workspace configuration

[^root-package]: Root package manifest

# Related decision records

These accepted ADRs record the decisions and tradeoffs; this page retains the current behavior or operational procedure.

- [ADR-0006: Enforce routes server-side using the current role contract (accepted)](/adr/ADR-0006-server-side-role-authorization.md)
