---
name: prune-deleted-branches
description: Find local branches whose remote was deleted by a merged PR and interactively delete the ones the user picks. User-invoked only via /prune-deleted-branches.
disable-model-invocation: true
---

# Prune deleted branches

Clean up local branches left behind after their PRs merged and GitHub deleted
the remote branch. Deletion is `git branch -D`, so the user picks what goes —
never delete on your own judgment.

## 1. Refresh remote state

```bash
git fetch --prune
```

This is what makes deleted remote branches show up as `gone` locally. Without
it you're reading stale tracking refs and will miss branches or offer ones
that still exist.

## 2. Find branches whose upstream is gone

```bash
git branch -vv | grep ': gone]'
```

If nothing comes back, tell the user there's nothing to prune and stop.

Set aside anything you shouldn't touch: the currently checked-out branch,
`master`/`main`, and branches checked out in another worktree (`git worktree
list`). Mention them only if they'd otherwise have been candidates.

## 3. Confirm each one against a merged PR

A `gone` upstream alone isn't proof the work shipped — the branch may have
been deleted manually or pushed under a different name. For each candidate:

```bash
gh pr list --state merged --head <branch-name> --json number,title,headRefOid
```

No result means no merged PR: leave the branch alone and say so, rather than
dropping it silently. The user usually wants to know a branch they expected
to be merged isn't.

Also compare the branch's local tip (`git rev-parse <branch>`) against the
PR's `headRefOid`. If they differ, the branch has local commits that were
never part of the merge, and deleting it loses them. Don't exclude it — just
flag it in the picker so the user can decide.

Note that "is it merged into master" is the wrong question here: squash and
rebase merges never put the branch's commits in the base branch, so
`git branch --merged` would wrongly report almost everything as unmerged.
The merged PR is the source of truth.

## 4. Let the user pick

Use `AskUserQuestion` with `multiSelect: true` so they can select several with
the spacebar. One option per branch:

- **label**: the branch name
- **description**: the PR number and title — plus `has N local commit(s) not
in the merged PR` when the tips differed in step 3

They can select any subset, or choose "Other" to cancel.

## 5. Delete and report

Delete only what they selected:

```bash
git branch -D <branch-name>
```

Then summarize: which branches were deleted, and which candidates were left
alone and why (no merged PR, protected, checked out elsewhere). If a delete
fails, name the branch and show the error instead of reporting success.

## If `gh` isn't available

`gh` missing or unauthenticated (`gh auth status`) means step 3 can't run.
Say so and point at `gh auth login` — don't fall back to deleting branches on
the `gone` marker alone, since that's the check keeping unmerged work safe.
