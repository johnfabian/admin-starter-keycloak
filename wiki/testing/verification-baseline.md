---
type: Test Strategy
title: Verification baseline
description: Current static, tooling and browser verification commands; hosted CI remains deferred.
tags: [testing, lint, typecheck, ci, evidence]
status: draft
generated: { by: codex/gpt-5, at: 2026-08-02T15:45:23Z }
stale_after: 2026-10-02
sources:
  - id: root-package
    resource: /package.json
    title: Root package manifest
    last_modified: 2026-08-01
  - id: web-package
    resource: /web/package.json
    title: Web package manifest
    last_modified: 2026-05-21
  - id: tracked-tree
    resource: git:06bf358
    title: Tracked repository tree at inventory revision 06bf358
    last_modified: 2026-08-01
---

# Current gate

`corepack pnpm check` is the declared static verification gate. It runs formatting validation, ESLint, React Router type generation, and TypeScript checking.[^root-package][^web-package] `corepack pnpm web:build` is available as a separate production build check.[^root-package]

# Local automated verification

The standalone tests/browser package declares pinned Playwright Chromium and axe dependencies.
Root test:fast adds Python automation tests and browser-test type checking. test:e2e exercises the
existing local Keycloak realm with owned fixtures; verify:story runs the build, graph checks and two
browser passes. See [automated local verification](/testing/automated-local-verification.md).

The earlier inventory had no executable suite. That historical gap is replaced by the local tooling;
no hosted CI workflow is configured. A configured test is not evidence that its live execution passed.

# Evidence language

- Report formatting, lint, type-check, build, and tests as separate categories.
- Do not state that tests passed when only the static gate ran.
- When adding a runner, declare package/root scripts and map the testing rule to the real configuration.

# Uncertainty

External organization-level checks or branch protection may exist, but they are not discoverable from this repository and were not queried or mutated.

[^root-package]: Root package manifest

[^web-package]: Web package manifest

[^tracked-tree]: Tracked repository tree at inventory revision 06bf358
