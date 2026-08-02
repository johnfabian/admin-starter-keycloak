---
name: skills-audit
description: Audit canonical repository skill packages, portable Python/uv automation, and Claude discovery adapters, and safely create missing relative directory symlinks. Use after adding, renaming, moving, or reviewing a skill under .agents/skills, when Claude skill discovery is incomplete, or before committing skill changes.
---

# Audit repository skills

Run from this skill directory:

```text
uv run scripts/audit_skills.py <repository-root> --fix
uv run scripts/audit_skills.py <repository-root>
uv run scripts/audit_skills.py <repository-root> --json
```

## Workflow

1. Capture the repository revision and dirty state.
2. Run with `--fix` after skill creation. Create only missing `.claude/skills/<name>` symlinks that point to `../../.agents/skills/<name>`.
3. Run again without `--fix` and require zero errors.
4. Inspect every reported copied directory, wrong or broken target, extra adapter, invalid package, or tracked non-symlink mode; correct it explicitly rather than replacing it automatically.
5. Stage the canonical package and adapter together when authorized, then verify the adapter appears in `git ls-files -s` with mode `120000`.
6. Report created links, canonical/adapted counts, untracked adapters, errors, warnings, revision, and checks.

## Safety

- Treat `.agents/skills/` as canonical and `.claude/skills/` as discovery adapters only.
- Never copy a skill body into `.claude/skills/`.
- Never delete, replace, or retarget an existing adapter automatically.
- Stop and report the exact path when the operating system refuses symlink creation.
- Do not stage, commit, or mutate GitHub unless the user explicitly authorizes it.
