# Lint Format Checks

Date: 2026-05-12

## Summary

Add Prettier and ESLint so the project can be formatted and linted before
pushing a branch.

## Key Changes

- Add Prettier config and ignore file.
- Add ESLint flat config for TypeScript and React.
- Add scripts:
  - `format`
  - `format:check`
  - `lint`
  - `check`
- Run format, lint, and typecheck after setup.

## Test Plan

- Run `npm run format`.
- Run `npm run lint`.
- Run `npm run typecheck`.
- Run `npm run check`.

## Assumptions

- Use Prettier as the formatter source of truth.
- Use ESLint for code-quality checks, not formatting.

## Implementation Status

- Completed
