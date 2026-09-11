---
name: skills-audit
description: Audit and repair the typed shared skill catalog, README catalog, portable Python/uv automation, project discovery adapters, and optionally flat Claude/Codex global symlinks. Use explicitly after adding, renaming, moving, or reviewing a skill under .agents-config/skills.
disable-model-invocation: true
---

# Audit shared skills

Run this configuration-changing workflow when explicitly invoked or as a specialist step of an authorized development flow. Keep repairs within the authorized repository scope. From this skill directory:

```text
uv run scripts/audit_skills.py <repository-root> --fix
uv run scripts/audit_skills.py <repository-root>
uv run scripts/audit_skills.py <repository-root> --json
```

The default scope is project adapters only. Global audit or repair requires explicit `--global-adapters` opt-in; normal feature worktree checks must omit it. To validate global-link behavior without changing the current user's home, use `--global-adapters --home <temporary-directory>`. `--home` alone does not enable global operations.

## Step 1: Categorize packages

1. Ensure `.agents-config/skills/meta/`, `.agents-config/skills/ops/`, and `.agents-config/skills/dev/` exist.
2. Move flat `skills-audit` and `rules-audit` packages to `meta/`.
3. Move flat `start-project`, `stop-project`, `start-server`, `stop-server`, and `prune-deleted-branches` packages to `ops/` when present.
4. Move other flat developer utility packages to `dev/`.
5. If the built-in creator placed a real package in `.agents/skills/`, move it to the matching canonical type before recreating its Codex adapter.
6. Stop on a destination collision; never merge two package directories implicitly.

## Step 2: Clean obsolete adapters

Remove only obsolete project symlinks for `critique-plan` to `critique-feature-spec` and `decompose-stories` to `plan-implementation` when the replacement package exists and the old package is absent. Preserve real files and directories as collisions.

With explicit `--global-adapters` opt-in, inspect every entry in both `~/.claude/skills/` and `~/.codex/skills/`. The Python repair implements the portable equivalent of checking that an entry is a symlink while its target does not exist, then unlinking only that broken symlink. Never delete a real file or directory.

## Step 3: Deep-flatten symlinks

1. Recursively discover `.agents-config/skills/*/*/SKILL.md` and require every skill base name to be unique.
2. Resolve each canonical package with `realpath` semantics.
3. Maintain flat, relative project adapters at `.agents/skills/<skill-name>` and `.claude/skills/<skill-name>`.
4. Only with `--global-adapters`, maintain flat, absolute global adapters at `~/.claude/skills/<skill-name>` and `~/.codex/skills/<skill-name>` using safe Python symlink replacement equivalent to `ln -sfn` for symlinks only.
5. Refuse to overwrite a real global or project file/directory.

## Package checks

- Treat `meta/`, `ops/`, and `dev/` as purpose categories only; never infer invocation mode from a package path.
- Read invocation mode from `SKILL.md` and `agents/openai.yaml`: paired `disable-model-invocation: true` and `policy.allow_implicit_invocation: false` mean explicit-only; absent locks mean contextual/model-eligible.
- Require the configuration, environment, destructive-Git, and issue-publication workflows to remain explicit-only.
- Allow `plan-feature`, `plan-implementation`, `implement-feature`, and `implement-story` to be contextual. Invocation policy controls discovery; actual action authority remains scoped to the approved task.
- Reject any one-provider lock mismatch for every skill. All skills remain directly user-invokable regardless of implicit-invocation policy.
- Require every package to be self-contained and every skill script to be portable Python with uv script metadata.
- Reject PowerShell-dependent instructions and non-Python files under skill-local `scripts/` directories.
- Verify project adapters are relative directory symlinks and tracked adapters use Git mode `120000`.
- Verify the README catalog contains exactly one canonical link for every skill and no stale package links. The audit reports drift but never rewrites explanatory prose.

## Report

Run the read-only audit after repair and require zero errors and warnings. Report revision, dirty state, package counts by type, project/global adapter counts, changes, collisions, and exact validation evidence. Do not stage, commit, or mutate GitHub unless separately authorized.
