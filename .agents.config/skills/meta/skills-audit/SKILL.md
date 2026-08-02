---
name: skills-audit
description: Audit and repair the typed shared skill catalog, portable Python/uv automation, project discovery adapters, and flat Claude/Codex global symlinks. Use explicitly after adding, renaming, moving, or reviewing a skill under .agents.config/skills.
disable-model-invocation: true
---

# Audit shared skills

Run this configuration-changing workflow only when the user explicitly invokes it. From this skill directory:

```text
uv run scripts/audit_skills.py <repository-root> --fix
uv run scripts/audit_skills.py <repository-root>
uv run scripts/audit_skills.py <repository-root> --json
```

Use `--home <temporary-directory>` to validate global-link behavior without changing the current user's home.

## Step 1: Categorize packages

1. Ensure `.agents.config/skills/meta/`, `.agents.config/skills/ops/`, and `.agents.config/skills/dev/` exist.
2. Move flat `skills-audit` and `rules-audit` packages to `meta/`.
3. Move flat `start-project`, `stop-project`, `start-server`, `stop-server`, and `prune-deleted-branches` packages to `ops/` when present.
4. Move other flat developer utility packages to `dev/`.
5. If the built-in creator placed a real package in `.agents/skills/`, move it to the matching canonical type before recreating its Codex adapter.
6. Stop on a destination collision; never merge two package directories implicitly.

## Step 2: Clean broken global links

Inspect every entry in both `~/.claude/skills/` and `~/.codex/skills/`. The Python repair implements the portable equivalent of checking that an entry is a symlink while its target does not exist, then unlinking only that broken symlink. Never delete a real file or directory.

## Step 3: Deep-flatten symlinks

1. Recursively discover `.agents.config/skills/*/*/SKILL.md` and require every skill base name to be unique.
2. Resolve each canonical package with `realpath` semantics.
3. Maintain flat, relative project adapters at `.agents/skills/<skill-name>` and `.claude/skills/<skill-name>`.
4. Maintain flat, absolute global adapters at `~/.claude/skills/<skill-name>` and `~/.codex/skills/<skill-name>` using safe Python symlink replacement equivalent to `ln -sfn` for symlinks only.
5. Refuse to overwrite a real global or project file/directory.

## Package checks

- Require `meta/` and `ops/` skills to declare `disable-model-invocation: true` and `policy.allow_implicit_invocation: false`.
- Let `dev/` skills use progressive disclosure by default, but permit explicit-only workflow anchors when both provider locks are present.
- Require `feature-plan`, `implement-story`, and `publish-issues` to remain explicit-only and reject any one-provider lock mismatch.
- Require every package to be self-contained and every skill script to be portable Python with uv script metadata.
- Reject PowerShell-dependent instructions and non-Python files under skill-local `scripts/` directories.
- Verify project adapters are relative directory symlinks and tracked adapters use Git mode `120000`.

## Report

Run the read-only audit after repair and require zero errors and warnings. Report revision, dirty state, package counts by type, project/global adapter counts, changes, collisions, and exact validation evidence. Do not stage, commit, or mutate GitHub unless separately authorized.
