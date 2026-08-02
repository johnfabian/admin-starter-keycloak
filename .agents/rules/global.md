---
id: global
paths: ["**/*"]
applies_to: ["**/*"]
owner: unassigned
enforcement: ["prettier", "repository-check"]
wiki: ["/conventions/repository-tooling.md"]
config: ["/package.json", "/prettier.config.mjs", "/.prettierignore", "/.gitignore"]
---

# Global rules

## Required

- Preserve unrelated work and inspect `git status` before and after editing.
- Keep changes within the authorized scope and cite repository evidence for new durable knowledge.
- Use root `corepack pnpm` scripts so repository environment wrappers are preserved.
- Implement new repository automation as portable Python `.py` files; invoke Python automation through `uv run` and maintain existing POSIX backup/restore scripts in place unless migration is explicitly authorized.
- Keep automation platform-neutral and pass subprocess arguments without shell-specific command strings.
- Run `corepack pnpm format:check`; run `corepack pnpm check` for application-affecting changes.
- Record unavailable or failed checks exactly; never infer a pass.

## Prohibited

- Do not read, commit, or print ignored secrets, dumps, logs, backups, or local environment files.
- Do not treat plans, placeholders, agent prose, or documentation as proof of implemented behavior.
- Do not mutate GitHub, production systems, or protected branches without explicit authority.
- Do not add PowerShell (`.ps1`, `powershell`, or `pwsh`) or Node (`.js`, `.cjs`, or `.mjs`) automation under repository or skill `scripts/` directories; JavaScript tool configuration modules are exempt.

## Checks

- Formatter: `corepack pnpm format:check` via [`package.json`](../../package.json).
- Static application gate: `corepack pnpm check` via [`package.json`](../../package.json).
