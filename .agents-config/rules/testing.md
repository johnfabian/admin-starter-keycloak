---
id: testing
paths:
  [
    "**/*.{test,spec}.{js,jsx,ts,tsx}",
    "**/{test,tests,__tests__}/**/*",
    "**/{vitest,jest,playwright,cypress}.config.*",
  ]
applies_to:
  [
    "**/*.{test,spec}.{js,jsx,ts,tsx}",
    "**/{test,tests,__tests__}/**/*",
    "**/{vitest,jest,playwright,cypress}.config.*",
  ]
owner: unassigned
enforcement: ["repository-check", "manual-test-gap"]
wiki: ["/testing/verification-baseline.md"]
config: ["/package.json", "/web/package.json", "/web/eslint.config.mjs", "/web/tsconfig.json"]
---

# Testing rules

## Required

- Distinguish static checks, builds, unit tests, integration tests, and end-to-end tests in evidence.
- Keep tests deterministic, isolated from production data, and explicit about required containers or fixtures.
- Cover negative authorization and failure behavior when identity, roles, sessions, or data ownership changes.
- Add a declared package/root test command with any introduced test framework.

## Prohibited

- Do not count files under `specs/plans/` as executable tests.
- Do not claim tests passed when only lint, formatting, type-check, or build ran.
- Do not place real credentials, tokens, personal data, or production payloads in fixtures.

## Checks

- Run `corepack pnpm check` for the current static gate.
- Record automated tests as unavailable until a test runner and test scripts exist.
