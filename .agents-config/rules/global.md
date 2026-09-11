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

- Use a dedicated linked worktree and feature branch for every writing agent; run corepack pnpm agent:check before edits and corepack pnpm verify:commit before commits. Bootstrap changes validate Git identity first.

- Preserve unrelated work and inspect `git status` before and after editing.
- Keep changes within the authorized scope and cite repository evidence for new durable knowledge.
- Use root `corepack pnpm` scripts so repository environment wrappers are preserved.
- Implement new repository automation as portable Python `.py` files; invoke Python automation through `uv run` and maintain existing POSIX backup/restore scripts in place unless migration is explicitly authorized.
- Keep automation platform-neutral and pass subprocess arguments without shell-specific command strings.
- Run `corepack pnpm format:check`; run `corepack pnpm check` for application-affecting changes.
- Record unavailable or failed checks exactly; never infer a pass.

## AI Workflow & Invocation Decision Framework

### Invocation metadata

- Determine invocation mode from the selected package's metadata, never from its `meta/`, `ops/`, or `dev/` directory.
- Read `disable-model-invocation` from `SKILL.md` for Claude and `policy.allow_implicit_invocation` from `agents/openai.yaml` for Codex before invoking a skill.
- Treat a skill as explicit-only when `disable-model-invocation: true` and `allow_implicit_invocation: false` are both present. Treat it as contextual/model-eligible when the Claude lock is absent and the Codex policy is absent or `true`.
- Reject a one-provider mismatch and run the skill/rule audits; never guess the intended invocation mode.
- All skills remain user-invokable as `/skill-name` in Claude or `$skill-name` in Codex, including contextual skills.

### Explicit-only workflows

- Map the workflow and its side effects in the task plan before an authorized human manually invokes it as `/skill-name` in Claude or `$skill-name` in Codex.
- Run these workflows sequentially and never infer authorization from task context alone.
- Use `plan-feature` as the primary explicit SDLC entry point. It may identify one next specialist skill but must not bypass a specialist workflow or human gate.

### Contextual skills

- Use the short frontmatter description for discovery and load full instructions on demand only when the current task matches.
- Permit direct user invocation even when a contextual skill could have been selected implicitly.

## Prohibited

- Do not print or commit ignored secrets, dumps, logs, backups, or local environment values. Authorized Keycloak/environment helpers may read an explicitly selected local environment file in-process without displaying values; graph extraction must exclude it.
- Do not treat plans, placeholders, agent prose, or documentation as proof of implemented behavior.
- Do not mutate GitHub, production systems, or protected branches without explicit authority.
- Do not add PowerShell (`.ps1`, `powershell`, or `pwsh`) or Node (`.js`, `.cjs`, or `.mjs`) automation under repository or skill `scripts/` directories; JavaScript tool configuration modules are exempt.

## Checks

- Formatter: `corepack pnpm format:check` via [`package.json`](../../package.json).
- Static application gate: `corepack pnpm check` via [`package.json`](../../package.json).
