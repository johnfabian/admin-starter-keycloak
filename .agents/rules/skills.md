---
id: skills
paths: [".agents/skills/**/*", ".claude/skills/*"]
applies_to: [".agents/skills/**/*", ".claude/skills/*"]
owner: unassigned
enforcement: ["skills-audit", "skill-package-validation", "human-review"]
wiki: ["/conventions/repository-tooling.md"]
config:
  ["/.agents/skills/skills-audit/SKILL.md", "/.agents/skills/skills-audit/scripts/audit_skills.py"]
---

# Skill package rules

## Required

- Keep the authoritative package under `.agents/skills/<skill-name>/` with matching lowercase hyphen-case `name` metadata.
- Keep each skill self-contained; resolve instruction links within its own package.
- After adding, renaming, moving, or reviewing a skill, run `$skills-audit` with missing-adapter repair and then its read-only audit.
- Keep `.claude/skills/<skill-name>` as a relative directory symlink to `../../.agents/skills/<skill-name>` and verify tracked mode `120000`.
- Write skill automation as portable Python, declare its Python requirement in `uv` script metadata, and invoke it with `uv run`; prefer the standard library when no dependency is required.
- Keep skill instructions and subprocess calls platform-neutral.

## Prohibited

- Do not copy skill bodies into `.claude/skills/` or maintain provider-specific duplicates.
- Do not automatically delete, overwrite, or retarget copied, broken, extra, or incorrect adapters.
- Do not stage or commit skill changes without explicit authority.
- Do not embed PowerShell-only commands or add PowerShell or Node `.mjs` automation to a skill package.

## Checks

- Repair missing adapters: `uv run .agents/skills/skills-audit/scripts/audit_skills.py . --fix`.
- Audit package and adapter parity: `uv run .agents/skills/skills-audit/scripts/audit_skills.py .`.
