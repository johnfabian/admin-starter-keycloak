# Implementation plan: Agent development workflow

Date: 2026-09-11
Status: Draft - user-selected three flows; critique and implementation approval pending
Feature: [FEAT-AGENT-WORKFLOW](../features/2026-09-11-agent-development-workflow.md)
Source and existing skill version: 342ec668b7848fe0200a9c317812831ca546b885
Integration owner: primary agent, within user-approved scope
Execution status: planning documents and wiki/ADR proposals prepared; skill/rule/application automation is not implemented, and legacy plans are retained

## Three developer flows

| Entry point         | Internal steps                                                                                                                 | Result                                               |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------- |
| plan-feature        | Brief interview when needed, feature spec, independent critique, revisions                                                     | Critiqued spec in specs/features                     |
| plan-implementation | Vertical stories and dependencies, independent critique, revisions, one human approval                                         | Approved spec and plan in specs/implementation-plans |
| implement-feature   | Implementation, automated tests, adversarial review/fixes, integration, wiki/graph updates, audits, commit/push, PR submission | Verified feature PR ready for human merge            |

The user selected this grouping in conversation on 2026-09-11. The single routine approval point is at the end of flow two and binds the exact specification, implementation plan, and delivery scope through feature PR submission. Flow three continues without repeated permission prompts for that already approved scope. Material ambiguity, changed scope or destination, missing actual authority, or blocking failures require resolution. PR merge and deployment remain outside this flow.

Critiques, tests, audits, and knowledge updates are internal steps, not extra developer commands. A small feature can be one vertical story. Use parallel writers only when independent slices justify them; do not manufacture extra stories or database/API/UI layers just to exercise the process. The current login/roles foundation is context for future application features, not a request to build those applications now.

The six delivery stories below organize this tooling change internally; they are not six additional user workflows.

## Skill changes

| Existing surface                          | Proposed change                                                                                                                              |
| ----------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| plan-feature                              | Actively orchestrate research/interview/spec creation and critique; stop at material decisions, not after every skill.                       |
| critique-plan                             | Rename to critique-feature-spec and narrow to specification quality; preserve old package references in historical evidence.                 |
| decompose-stories                         | Rename/evolve to plan-implementation; retain vertical decomposition and produce the complete implementation-plan artifact.                   |
| New critique-implementation-plan          | Independently evaluate story coverage, dependencies, readiness, ownership, verification, and rollback.                                       |
| New implement-feature                     | Own the complete implement/test/review/update/PR flow; dispatch workers, preserve progress, integrate, and verify before publication.        |
| implement-story                           | Accept coordinator-delegated authority for the approved story, with isolated worktree, tests, independent review, and bounded fix loops.     |
| parallel-implementation                   | Internal coordination procedure used by implement-feature; one owner for shared changes and at most two writers.                             |
| adversarial-review                        | Explicit counter, revision-bound findings, blocking threshold, exhaustion behavior, and independent reviewer contract.                       |
| preview-issues / publish-issues / handoff | Align persistence with the chosen specs/GitHub ownership; preserve exact-content approval and read-back for authorized external publication. |
| skills-audit / rules-audit                | Update invocation contracts and renamed packages; separate project validation from optional global adapter installation.                     |
| record-adr / wiki-update / graphify       | Integrate into story/feature completion without treating plans or generated graphs as accepted architecture.                                 |

Keep specialist research, requirements, architecture, edge cases, tests, and audits reusable. This proposal yields about 31 canonical packages, but only three primary developer entry points: plan-feature, plan-implementation, and implement-feature. Critiques remain directly callable.

## Delivery stories and dependencies

This is workflow/tooling work, so vertical slices run from developer invocation through artifact/validation/resume behavior; they do not manufacture database or UI changes.

### STORY-001: Create and critique a reusable feature specification

Requirements: REQ-001, REQ-002, REQ-008.
Outcome: a developer request produces a dated specification, material interview questions, and a revision-bound independent critique.
Own: plan-feature, critique-feature-spec rename, their templates/state validators/scenarios, feature-spec contract.
Shared owner: integration owner controls discovery links, README catalog, invocation policy, and audit allowlists.
Tests: naming/slug validation, missing criteria, pending decision, stale digest, approval invalidation, natural-language routing, injected repository instructions, and legacy state compatibility.
Dependencies: none; material interview decisions must be resolved before finalizing the contract.
Done: no mandatory per-specialist invocation; spec and critique survive a clean-session resume. Existing 1.x state is explicitly legacy and never silently promoted to approved new state.
Rollback: restore prior workflow version and retain the draft spec; never rewrite historical records.

### STORY-002: Turn a specification into a validated delivery plan

Requirements: REQ-003, REQ-005.
Outcome: a complete implementation plan covers each requirement with vertical stories and a valid dependency graph.
Own: plan-implementation rename/evolution, critique-implementation-plan, plan schema/validator and fixtures.
Tests: duplicate IDs, cycles, unknown/self dependencies, uncovered requirements, unjustified horizontal stories, path overlap, missing tests, changed spec hash, blocked decision, migration ownership.
Dependencies: STORY-001.
Done: a reviewer can determine ready work and validation without conversation context.
Rollback: leave the plan draft and disable dispatch on its schema version.

### STORY-003: Execute and resume feature delivery through PR submission

Requirements: REQ-004, REQ-005, REQ-006, REQ-007.
Outcome: implement-feature delivers the approved scope through coding, tests, independent adversarial review, knowledge updates, integration, and PR submission without repeated routine prompts or concurrent ownership conflicts.
Own: implement-feature, implement-story, parallel-implementation, adversarial-review and their portable validators/state helpers.
Shared owner: integration owner controls bootstrap/test-lock/hook integration and any root script changes.
Tests: diamond graph (A -> B/C -> D), no-premature D dispatch, maximum two writers, path reservations, worker failure, interrupted resume, duplicate claim prevention, stale base, failed integration, exact reviewed revision, feature-level five-round exhaustion, no PR on failed verification, approved branch/remote binding, and idempotent PR resume.
Dependencies: STORY-002.
Done: readiness depends on integrated verified prerequisites; independent reviews are genuine; browser runs honor existing shared-stack locking and fixture ownership.
Rollback: stop dispatch, preserve worker branches/checkpoints, resume serially under the same approvals.

### STORY-004: Use the same workflow from isolated harness contexts

Requirements: REQ-008.
Outcome: a fresh supported harness discovers project-local skills and resumes the same work packet without modifying another worktree's global configuration.
Own: provider capability contract and scoped adapter audit changes.
Shared owner: integration owner applies README/router/catalog/rule changes.
Tests: project-relative symlinks, real-file collisions, optional global links in an isolated temporary home, two-worktree non-interference, missing delegation capability, missing independent reviewer, invocation-metadata parity.
Dependencies: STORY-001; can be implemented alongside STORY-002 only after explicit ownership of audit scripts/shared catalogs is reserved.
Done: Codex/Claude discovery checked; ORCA adapter either verified against the identified version or explicitly outside the completed compatibility claim.
Rollback: retain canonical packages and use project-local discovery; no destructive cleanup of personal skill directories.

### STORY-005: Migrate knowledge and legacy plans without losing decisions

Requirements: REQ-007, REQ-009.
Outcome: the wiki describes current capabilities, ADR status is honest, and the requested specs directory layout replaces legacy plans.
Own: wiki concepts/indexes/log, legacy plan deletion manifest, sdlc-prd.md alignment or clearly marked supersession, knowledge runbook.
Shared owner: integration owner controls ADR identifiers and final graph configuration/refresh.
Tests: skill/rule/wiki audits, active link/name audit, immutable historical references, ADR provenance and supersession, no generated graphs/secrets staged.
Dependencies: STORY-002; may run alongside STORY-003 if paths do not overlap. Final wording must be reconciled after STORY-003 and STORY-004.
Done: each legacy file has a disposition; no obsolete local-only logout/cookie design is represented as current. Original stability-pilot drafts remain untouched.
Rollback: recover deleted tracked documents from Git; never delete draft checkpoints automatically.

### STORY-006: Prove the workflow through integration and clean-session handoff

Requirements: all.
Outcome: a small declared workflow pilot exercises planning, critique, dependency-ready dispatch, failed-story blocking, review/fix, integration, and provider-neutral resume.
Own: integration evidence and final coordination updates; integration owner only.
Tests: applicable tooling tests, format/static/build checks, skill/rule/wiki audits, graph build/check, verify:commit, affected verify:story, and independent final review at the actual integrated revision.
Dependencies: STORY-003, STORY-004, STORY-005.
Done: no open blocking findings or invented approvals; evidence distinguishes simulated scheduler tests from real agent runs and real browser tests. Publish only under explicit granted scope.
Rollback: preserve reviewed branches and report the exact blocked stage; do not treat a pilot failure as completion.

## Proposed execution groups

- Group 1: STORY-001.
- Group 2: STORY-002 and STORY-004, only with disjoint ownership; otherwise serialize.
- Group 3: STORY-003 and the independent documentation portion of STORY-005.
- Group 4: reconcile shared changes, then STORY-006.

The main agent owns integration and shared files. If it writes while workers run, it counts toward the two-writer limit. Read-only reviewers do not consume a writer slot. Parallel writers use dedicated linked worktrees from the agreed base; no shared-checkout editing.

## State and verification design

Version the workflow schema. Store stable IDs, source revisions, spec/plan digests, prerequisite IDs, reservations, worker branch/worktree, integration revisions, review round counts, finding dispositions, and evidence paths. Reject stale/malformed state before execution. Git-tracked specifications remain reviewable; ignored execution state is recovery data, not authority.

Python helpers validate and calculate ready work; harness adapters perform actual delegation. Do not claim a universal scheduler is implemented merely because Markdown describes it. Exercise portable helpers deterministically, then prove real delegation in a supported harness.

Reviews bind to exact content. A fix invalidates affected evidence and triggers the required checks/review. The working interpretation is one feature-level budget of at most five review-and-fix rounds including final integration, without resetting or multiplying the budget per story, worker, or resume. The fifth unsuccessful round leaves the gate blocked and prevents submission as a completed feature.

Use existing agent:check, graph:update/check, verify:commit, and verify:story conventions. Never run concurrent live browser stacks against the shared realm. Preserve existing hooks and the staged-snapshot/index guarantees.

## ADR reconciliation

Existing proposed ADRs:

- ADR-0001 worktree isolation: preserve ID; obtain attributable acceptance or retain proposed status.
- ADR-0002 graph/wiki ownership: update the proposal to distinguish versioned specs from delivery records if approved.
- ADR-0003 shared-realm tests: preserve owned fixtures, separate admin realm, serialized stack and explicit repair policy.

The wiki reconciliation now contains ADR-0004 through ADR-0012 as draft/proposed records: three-flow development, BFF session/token and logout boundary, role authorization, registration approval, realm-local administration, portable agent tooling, dependency trust, local gateway isolation, and database recovery. Each links its source guidance, which remains in place. The audit classified all 43 pre-existing wiki concepts; four current-state/configuration/gap pages needed no new decision record.

These proposals capture source-backed choices and explicitly identify unknown historical rationale/approval. They are not accepted decisions or implementation authorization. The remaining implementation work must verify consistency, obtain attributable acceptance where appropriate, and preserve immutable identifiers. See [ADR register](../../wiki/adr/index.md).

Do not create an ADR for every setting or treat the proposed Express/Drizzle service as implemented. Known production gaps and draft console values remain unresolved guidance until a specific decision is made.

## Decisions and remaining scope

DEC-001 is selected by the user: three combined flows, with one routine approval after implementation planning. DEC-002 through DEC-004 are documented working defaults; DEC-005 limits ORCA-specific claims. The plan still needs independent critique and implementation approval. Choosing its workflow shape does not approve the whole change. No application or workflow behavior has been changed.

The current skill audit has four missing global adapters, which this work will resolve under the chosen project/global policy. Rules and wiki structure pass. This documentation change corrects four stale test-absence claims; broader workflow/rule alignment remains implementation work.
