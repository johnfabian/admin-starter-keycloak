---
id: security
paths:
  [
    "web/app/lib/server/**/*",
    "web/app/lib/auth-policy.shared.ts",
    "web/app/lib/security-headers.shared.ts",
    "web/app/routes/auth-*.tsx",
    "auth-server/**/*",
    "api-gateway/**/*",
    "postgres/**/*",
    "**/Dockerfile",
    "**/docker-compose*.yml",
    ".env*.example",
    "pnpm-workspace.yaml",
    "pnpm-lock.yaml",
    "**/package.json",
    "backup-all",
    "scripts/backup*.sh",
    "scripts/restore*.sh",
  ]
applies_to:
  [
    "web/app/lib/server/**/*",
    "web/app/lib/auth-policy.shared.ts",
    "web/app/lib/security-headers.shared.ts",
    "web/app/routes/auth-*.tsx",
    "auth-server/**/*",
    "api-gateway/**/*",
    "postgres/**/*",
    "**/Dockerfile",
    "**/docker-compose*.yml",
    ".env*.example",
    "pnpm-workspace.yaml",
    "pnpm-lock.yaml",
    "**/package.json",
    "backup-all",
    "scripts/backup*.sh",
    "scripts/restore*.sh",
  ]
owner: unassigned
enforcement:
  ["repository-check", "dependency-policy", "configuration-review", "human-security-gate"]
wiki:
  [
    "/architecture/react-router-bff.md",
    "/architecture/access-control-model.md",
    "/architecture/known-production-gaps.md",
    "/conventions/dependency-supply-chain-hardening.md",
    "/integrations/local-edge-and-identity.md",
    "/operations/backup-scope.md",
    "/operations/restore-keycloak-local.md",
    "/schemas/web-bff-sessions.md",
  ]
config:
  [
    "/package.json",
    "/pnpm-workspace.yaml",
    "/web/eslint.config.mjs",
    "/web/tsconfig.json",
    "/api-gateway/docker-compose.yml",
    "/auth-server/docker-compose.gateway.yml",
    "/web/docker-compose.gateway.yml",
    "/postgres/docker-compose.gateway.yml",
    "/scripts/backup-lib.sh",
    "/scripts/restore-keycloak-local-default.sh",
    "/scripts/restore-keycloak-local-traefik.sh",
  ]
---

# Security rules

## Required

- Preserve the server-side token boundary, opaque HttpOnly session cookie, same-origin mutation checks, and explicit role authorization.
- Validate external input and identity claims at the trusted boundary; test negative authorization paths when behavior changes.
- Keep secrets in environment/secret stores and inspect example files only for names and safe placeholders.
- Preserve the declared pnpm age, provenance, source, and lifecycle-script controls unless a narrow exception receives attributable review.
- Preserve `exposedByDefault=false`, explicit router opt-in, read-only Docker socket access, and mode-correct Keycloak proxy/hostname settings.
- Name the exact restore stack, container, database or volume, and backup file; obtain explicit destructive-action confirmation and take a recoverable pre-restore backup when applicable.
- Review proxy/header/TLS, public-port, database, backup/restore, and rollback impact for matching changes.
- Stop for attributable human security approval before identity, authorization, secrets, externally reachable edge, or material data-classification changes proceed.

## Prohibited

- Do not expose access/refresh tokens to browser code, logs, telemetry, handoffs, or issue prose.
- Do not expose environment secrets, database dumps, restore payloads, or SMTP credentials in Git, logs, command output, issues, or handoffs.
- Do not enable insecure forwarded-header trust, public management endpoints, or production `api.insecure` behavior.
- Do not relax supply-chain controls or trust new privileged dependencies without an approved review.
- Do not run a wildcard, inferred, or unconfirmed restore target or volume deletion.

## Checks

- Run `corepack pnpm check` for matching TypeScript/application changes.
- Run applicable `docker compose ... config` validation with approved example/environment inputs for changed Compose files.
- For backup/restore changes, run non-destructive syntax checks and record the exact target/confirmation guard reviewed; perform a restore only with explicit authority.
- Record security review and authorization-test status explicitly; static checks do not satisfy the human gate.
