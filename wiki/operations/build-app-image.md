---
type: Runbook
title: Build the app image
description: Current Docker image build workflow and evidence required before publication.
tags: [docker, react-router, build, deployment]
status: draft
generated: { by: codex/gpt-5, at: 2026-08-02T16:44:19Z }
stale_after: 2026-10-02
sources:
  - id: web-dockerfile
    resource: /web/Dockerfile
    title: React Router multi-stage image
    last_modified: 2026-05-15
  - id: root-scripts
    resource: /package.json
    title: Static verification and web build scripts
    last_modified: 2026-08-01
  - id: security-headers
    resource: /web/app/lib/security-headers.shared.ts
    title: Production CSP implementation
    last_modified: 2026-08-01
---

# Verify and build

Run the static gate and production build first:

```bash
corepack pnpm check
corepack pnpm web:build
```

Build from the repository root because the Dockerfile copies workspace manifests and the web package:[^web-dockerfile]

```bash
docker build -f web/Dockerfile -t <registry>/admin-starter-keycloak:<immutable-tag> .
```

The image starts `react-router-serve` and carries no runtime secrets or database migration step. Supply all required environment values at runtime.

# Release boundary

The static gate does not run a browser or live Keycloak flow.[^root-scripts] Production CSP currently lacks the nonce described as required in the source comments, so test hydration and interactive controls against the built image before publication.[^security-headers] No registry, signing, provenance, scanning, promotion, or rollback policy is configured in the repository.

# Related concepts

- [Known production gaps](/architecture/known-production-gaps.md)
- [Environment variables](/operations/environment-variables.md)
- [Verification baseline](/testing/verification-baseline.md)

[^web-dockerfile]: React Router multi-stage image

[^root-scripts]: Static verification and web build scripts

[^security-headers]: Production CSP implementation
