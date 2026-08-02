---
name: decompose-stories
description: Turn approved requirements, architecture impact, edge cases, and test strategy into small, independently valuable vertical story previews with explicit dependencies and definition-of-ready/done evidence. Use before GitHub issue preview; reject horizontal technical slices unless they are justified enabling work.
---

# Decompose vertical stories

Use the full Git commit containing this package as the skill version ID and record it in every artifact. A dirty package is unversioned and cannot satisfy a completed gate.

1. Confirm requirements and material decisions are approved or explicitly deferred.
2. Group work by one observable outcome, not by UI/API/database layer.
3. Give every story scope, non-scope, requirement IDs, acceptance criteria, tests, affected boundaries, owned paths, dependencies, risks, and definition of ready/done.
4. Split only when each smaller story retains value or sequencing is necessary.
5. Label unavoidable horizontal work as an enabling task and explain what vertical story it unblocks.
6. Keep shared contracts, lockfiles, migrations, generated artifacts, infrastructure, and release state serial unless an owner approves otherwise.
7. Render [templates/stories.md](templates/stories.md). Do not publish issues.

Use [references/scenarios.md](references/scenarios.md) to challenge verticality.
