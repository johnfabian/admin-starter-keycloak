---
type: Test Strategy
title: Verification baseline
description: Current repository verification commands, CI status, and executable-test gap.
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

# Missing enforcement

At the inventory revision, package manifests declare no `test` script or test-runner dependency, and the tracked tree contains no executable unit, integration, end-to-end, or test-runner configuration files.[^root-package][^web-package][^tracked-tree] Files under `specs/plans/` describe intended test plans but are not executable evidence.[^tracked-tree]

No `.github/workflows/` or other tracked CI configuration is present at the inventory revision.[^tracked-tree]

# Evidence language

- Report formatting, lint, type-check, build, and tests as separate categories.
- Do not state that tests passed when only the static gate ran.
- When adding a runner, declare package/root scripts and map the testing rule to the real configuration.

# Uncertainty

External organization-level checks or branch protection may exist, but they are not discoverable from this repository and were not queried or mutated.

[^root-package]: Root package manifest

[^web-package]: Web package manifest

[^tracked-tree]: Tracked repository tree at inventory revision 06bf358
