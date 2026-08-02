---
id: express
paths: ["api-express/**/*"]
applies_to: ["api-express/**/*"]
owner: unassigned
enforcement: ["prettier", "manual-placeholder-boundary"]
wiki:
  [
    "/integrations/express-resource-api.md",
    "/architecture/access-control-model.md",
    "/testing/verification-baseline.md",
  ]
config: ["/package.json", "/pnpm-workspace.yaml", "/prettier.config.mjs"]
---

# Express rules

## Required

- Treat `api-express/` as a placeholder until a package manifest and implementation exist.
- Add package-local lint, type-check, and test scripts and wire them into the root gate before claiming an Express service is implemented.
- Validate request inputs, token issuer/signature/audience, authorization, and error contracts at the API boundary.
- Define idempotency and audit behavior for mutating operations before implementation.

## Prohibited

- Do not claim an Express runtime, tests, or enforcement that the repository does not contain.
- Do not move the current browser session/BFF responsibility into this resource API without an approved architecture decision.
- Do not log authorization headers, tokens, secrets, or sensitive request bodies.

## Checks

- Run the currently available `corepack pnpm format:check`.
- Record Express lint, type-check, and test checks as unavailable until real scripts/configuration are added.
