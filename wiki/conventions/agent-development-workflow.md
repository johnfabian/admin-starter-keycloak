---
type: Convention
title: Three-flow agent development
description: Selected developer workflow combining specification critique, delivery planning approval, and implementation through pull request.
tags: [agents, workflow, specifications, testing, review]
status: draft
generated: { by: "codex/gpt-6", at: "2026-09-11T20:04:15Z" }
stale_after: 2026-12-11
sources:
  - id: selected-workflow
    resource: /specs/features/2026-09-11-agent-development-workflow.md
    title: Draft specification recording the user-selected three-flow structure
    last_modified: 2026-09-11
  - id: current-planning
    resource: /.agents-config/skills/dev/plan-feature/SKILL.md
    title: Existing planning skill and invocation limitations
    last_modified: 2026-09-11
  - id: current-stories
    resource: /.agents-config/skills/dev/decompose-stories/SKILL.md
    title: Existing vertical-story decomposition procedure
    last_modified: 2026-09-11
  - id: verification
    resource: /package.json
    title: Existing local verification and graph commands
    last_modified: 2026-09-11
---

# Three flows

The user selected this workflow in conversation on 2026-09-11 and requested that it be documented here. This is the intended development convention; the combined automation is not implemented yet. The named entry points below describe the target interface, not three currently available end-to-end commands.[^selected-workflow][^current-planning]

| Flow                                         | Work performed together                                                                                                                                    | Result                                                                                |
| -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| **Plan feature**: plan-feature               | Interview only where needed, write the feature specification, independently critique it, and revise it                                                     | Critiqued specification in specs/features/YYYY-MM-DD-feature-slug.md                  |
| **Plan implementation**: plan-implementation | Define vertical stories and dependencies, independently critique and revise the plan, then obtain the developer's approval                                 | Approved implementation plan in specs/implementation-plans/YYYY-MM-DD-feature-slug.md |
| **Implement feature**: implement-feature     | Implement, run automated tests, perform independent adversarial review and fixes, integrate, update wiki/graph, run audits, commit/push, and submit the PR | Verified feature PR ready for human merge                                             |

Critique, testing, audits, and documentation are internal steps. Developers should not have to invoke each specialist skill separately. The specification and implementation plan remain separate artifacts even though each flow performs its own critique.

# Approval and completion

The single routine approval point is at the end of implementation planning. It covers the exact specification, plan, and delivery scope through the intended feature branch push and PR submission. Already authorized routine steps do not require repeated permission prompts. Material scope changes, a different publication target, missing authority, or unresolved blocking findings require resolution. PR merge and deployment remain human decisions.

Independent review and automated tests run within implementation, including after relevant fixes and against the integrated result. Review/fix loops are bounded to prevent endless retries; the current draft interprets the requested maximum as five rounds for the feature including integration. That budget interpretation remains a draft detail. Exhaustion does not count as passing review.

# Keep features small

A small feature can remain one vertical story. A story delivers one observable outcome across whichever layers it needs: data/model and migration, service or BFF/API, UI, and verification. It need not touch every layer. Use the implemented stack; a placeholder directory or planned dependency is not an implemented service.[^current-stories]

Parallelize only independent slices. Ready work has its prerequisites integrated and verified; having other stories depend on it does not prevent it from starting. Each writer uses its own branch and linked worktree. Keep at most two writers initially, with one integration owner for shared files, lockfiles, migrations, and infrastructure. Shared live browser testing remains serialized.

# Knowledge responsibilities

- Feature specifications describe outcomes and scope; implementation plans hold stories and dependencies.
- GitHub issues/PRs record delivery, approval, review, and verification evidence against the relevant revisions.
- The wiki explains reusable architecture, conventions, and runbooks; [ADRs](/adr/index.md) record architectural decisions with honest approval provenance.
- [Graphify](/conventions/code-graph.md) supplies generated source relationships for code navigation. Refresh after source changes and integration; verify important claims in source.
- Skills define reusable procedures; rules define working constraints. Run skills-audit and rules-audit when those packages or rules change, and wiki-audit after wiki changes.

# Applicability

Local [automated verification](/testing/automated-local-verification.md), [worktree isolation](/operations/agent-worktrees.md), and graph commands already exist.[^verification] The current plan-feature skill still directs the user to the next specialist, and the new coordinator/renames remain implementation work. This page documents the selected direction without claiming those behaviors already work.[^current-planning]

Keep the core procedures harness-neutral. Discovery symlinks alone do not establish delegation, approval, or resume compatibility; ORCA-specific support remains unverified until the exact harness is identified.

[^selected-workflow]: Draft specification recording the user's selected flow grouping; implementation approval remains pending.

[^current-planning]: Existing planning skill, inspected at source revision 342ec668b7848fe0200a9c317812831ca546b885.

[^current-stories]: Existing vertical-story decomposition skill at the same revision.

[^verification]: Root verification and graph commands at the same revision.

# Related decision records

These proposals record the decision and tradeoffs; this page retains the current behavior or operational procedure.

- [ADR-0004: Use three developer flows with one routine approval (proposed)](/adr/ADR-0004-three-flow-development.md)
- [ADR-0009: Keep canonical agent procedures portable across harnesses (proposed)](/adr/ADR-0009-portable-agent-tooling.md)
