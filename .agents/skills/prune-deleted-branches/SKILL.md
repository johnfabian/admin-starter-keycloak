---
name: prune-deleted-branches
description: Find local branches whose upstream disappeared, verify each against a merged pull request, and delete only branches the user explicitly selects. Use only when the user asks to prune deleted branches.
---

# Prune deleted branches

Never delete a branch on your own judgment.

1. Run `git fetch --prune`, then inspect `git branch -vv` for upstreams marked `gone`.
2. Exclude the current branch, `main`/`master`, and branches checked out in another worktree.
3. For every candidate, run `gh pr list --state merged --head <branch> --json number,title,headRefOid`. Leave candidates without a merged PR untouched.
4. Compare `git rev-parse <branch>` with `headRefOid` and flag local commits not represented by the PR.
5. Ask the user to select candidates, showing the PR and any tip mismatch. Treat no selection as cancellation.
6. Run `git branch -D <branch>` only for explicitly selected branches, then report deleted and retained candidates.

If `gh` is missing or unauthenticated, stop and point to `gh auth login`; do not rely on a `gone` marker alone.
