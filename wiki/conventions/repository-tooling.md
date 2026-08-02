---
type: Convention
title: Repository tooling
description: Current pnpm, uv/Python automation, and static enforcement configuration.
tags: [pnpm, uv, python, prettier, eslint, typescript, tooling]
status: draft
generated: { by: codex/gpt-5, at: 2026-08-02T21:05:25Z }
stale_after: 2026-11-02
sources:
  - id: root-package
    resource: /package.json
    title: Root package manifest
    last_modified: 2026-08-01
  - id: web-package
    resource: /web/package.json
    title: Web package manifest
    last_modified: 2026-05-21
  - id: prettier-config
    resource: /prettier.config.mjs
    title: Prettier configuration
    last_modified: 2026-05-12
  - id: eslint-config
    resource: /web/eslint.config.mjs
    title: Web ESLint flat configuration
    last_modified: 2026-05-15
  - id: tsconfig
    resource: /web/tsconfig.json
    title: Web TypeScript configuration
    last_modified: 2026-05-15
  - id: workspace
    resource: /pnpm-workspace.yaml
    title: pnpm workspace and dependency policy
    last_modified: 2026-07-28
  - id: skills-audit-script
    resource: /.agents-config/skills/meta/skills-audit/scripts/audit_skills.py
    title: Skills audit Python automation
    last_modified: 2026-08-02
  - id: skills-rule
    resource: /.agents-config/rules/skills.md
    title: Shared skill package rule
    last_modified: 2026-08-02
---

# Commands

The root declares `pnpm@11.1.2` and wraps web commands with `corepack pnpm`.[^root-package] The root `check` command runs Prettier check, web ESLint, React Router type generation, and TypeScript checking in sequence.[^root-package][^web-package]

Use the root wrappers for environment-dependent web commands: the root build/dev/typecheck scripts inject `.env.development` through `dotenv-cli` without requiring agents to read the file.[^root-package]

Agent-framework skill automation is implemented in Python and launched through `uv run`. Canonical packages are typed under `.agents-config/skills/`; flat `.agents/skills/` and `.claude/skills/` symlinks expose the same packages to Codex and Claude.[^skills-audit-script][^skills-rule] Skill scripts are self-contained and currently require only the Python standard library. Existing operational backup/restore runbooks remain POSIX shell scripts; JavaScript `.mjs` files remain only where the JavaScript formatter or linter requires a configuration module.[^skills-audit-script][^prettier-config][^eslint-config]

# Configuration ownership

- `prettier.config.mjs` is the formatter source.[^prettier-config]
- `web/eslint.config.mjs` is the web lint source.[^eslint-config]
- `web/tsconfig.json` enables strict, no-emit TypeScript and React Router generated types.[^tsconfig]
- `pnpm-workspace.yaml` defines workspace membership and supply-chain constraints.[^workspace]

# Related concepts

- [Verification baseline](/testing/verification-baseline.md)
- [Repository implementation boundaries](/architecture/repository-boundaries.md)

# Uncertainty

There is no tracked CI workflow enforcing these commands. Rule ownership and required branch-protection checks are not recorded in the repository.

[^root-package]: Root package manifest

[^web-package]: Web package manifest

[^prettier-config]: Prettier configuration

[^eslint-config]: Web ESLint flat configuration

[^tsconfig]: Web TypeScript configuration

[^workspace]: pnpm workspace and dependency policy

[^skills-audit-script]: Skills audit Python automation

[^skills-rule]: Shared skill package rule
