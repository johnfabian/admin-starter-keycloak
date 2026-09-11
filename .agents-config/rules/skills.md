---
id: skills
paths: [".agents-config/skills/**/*", ".agents/skills/*", ".claude/skills/*", "README.md"]
applies_to: [".agents-config/skills/**/*", ".agents/skills/*", ".claude/skills/*", "README.md"]
owner: unassigned
enforcement: ["skills-audit", "skill-package-validation", "human-review"]
wiki: ["/conventions/repository-tooling.md"]
config:
  [
    "/.agents-config/skills/meta/skills-audit/SKILL.md",
    "/.agents-config/skills/meta/skills-audit/scripts/audit_skills.py",
  ]
---

# Shared skill package rules

## Required

- Keep the authoritative package under `.agents-config/skills/<type>/<skill-name>/`; use only `meta`, `ops`, or `dev` as the type and match lowercase hyphen-case `name` metadata.
- Keep each skill self-contained; resolve instruction links within its own package.
- Put configuration/audit workflows in `meta/`, environment or destructive Git workflows in `ops/`, and development workflows/helpers in `dev/`.
- Treat the type directory as purpose classification only; determine invocation mode from package metadata.
- Read Claude's `disable-model-invocation` from `SKILL.md` and Codex's `policy.allow_implicit_invocation` from `agents/openai.yaml`.
- Use both locks for explicit-only skills and neither lock for contextual/model-eligible skills. Reject a Claude/Codex lock mismatch.
- Keep the current configuration, environment, destructive-Git, planning-anchor, implementation, and publication workflows explicit-only. All skills remain directly user-invokable.
- Keep `.agents/skills/<skill-name>` and `.claude/skills/<skill-name>` as relative directory symlinks to the same typed canonical package; require unique skill base names and tracked mode `120000`.
- After adding, renaming, moving, or reviewing a skill, explicitly run `$skills-audit` with repair and then run its read-only audit.
- Write skill automation as portable Python, declare its Python requirement in uv script metadata, and invoke it with `uv run`; prefer the standard library when no dependency is required.
- Keep skill instructions and subprocess calls platform-neutral.
- Keep approved feature-planning artifacts and handoffs in exact, idempotently keyed GitHub issue comments after preview and human approval. Treat `.agent-work` copies as provisional and never delete them automatically.
- Keep the README skill catalog between its audit markers complete and linked to every canonical package; summarize purpose and invocation mode without copying skill bodies.

## Prohibited

- Do not copy skill bodies into `.agents/`, `.claude/`, or a global provider directory.
- Do not overwrite a real file or directory while repairing a symlink.
- Do not stage or commit skill changes without explicit authority.
- Do not embed PowerShell-only commands or add PowerShell, JavaScript, CommonJS, or Node `.mjs` automation to a skill package.

## Checks

- Categorize packages and repair project/global adapters: explicitly invoke `$skills-audit`, which runs `uv run .agents-config/skills/meta/skills-audit/scripts/audit_skills.py . --fix`.
- Audit package, README catalog, invocation-policy, and adapter parity: `uv run .agents-config/skills/meta/skills-audit/scripts/audit_skills.py .`.
