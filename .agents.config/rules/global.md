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

## AI Workflow & Invocation Decision Framework

### Slash command workflows

- Treat every skill under `.agents.config/skills/meta/` or `.agents.config/skills/ops/` as explicit-only. Also treat a `dev/` workflow as explicit-only when it begins implementation, crosses a human approval gate, mutates external state, or performs destructive work.
- Require both provider locks for every explicit-only skill: `disable-model-invocation: true` in `SKILL.md` and `allow_implicit_invocation: false` under `policy` in `agents/openai.yaml`.
- Map the workflow and its side effects in the task plan before an authorized human manually invokes it as `/skill-name` in Claude or `$skill-name` in Codex.
- Run these workflows sequentially and never infer authorization from task context alone.
- Use `feature-plan` as the primary explicit SDLC entry point. It may identify one next specialist skill but must not bypass a specialist workflow or human gate.

### Progressive disclosure skills

- Treat helpers under `.agents.config/skills/dev/` as contextual by default.
- Permit a dev workflow to opt into explicit-only invocation only when both provider locks are present; never lock only one provider.
- For unlocked dev helpers, use only the short frontmatter description for discovery and load full instructions on demand when the current development task matches.

## Prohibited

- Do not read, commit, or print ignored secrets, dumps, logs, backups, or local environment files.
- Do not treat plans, placeholders, agent prose, or documentation as proof of implemented behavior.
- Do not mutate GitHub, production systems, or protected branches without explicit authority.
- Do not add PowerShell (`.ps1`, `powershell`, or `pwsh`) or Node (`.js`, `.cjs`, or `.mjs`) automation under repository or skill `scripts/` directories; JavaScript tool configuration modules are exempt.

## Checks

- Formatter: `corepack pnpm format:check` via [`package.json`](../../package.json).
- Static application gate: `corepack pnpm check` via [`package.json`](../../package.json).
