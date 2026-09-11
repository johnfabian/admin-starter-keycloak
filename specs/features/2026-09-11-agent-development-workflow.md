# Agent development workflow

Date: 2026-09-11
Status: Implementation authorized in conversation; verification recorded in the feature PR
Feature ID: FEAT-AGENT-WORKFLOW
Source and existing skill version: 342ec668b7848fe0200a9c317812831ca546b885
Branch: sdlc/feature-workflow-design
Related plan: [Implementation plan](../implementation-plans/2026-09-11-agent-development-workflow.md)

## Outcome and scope

A developer can request a feature in ordinary language, review its specification and delivery plan, and let a coordinator implement dependency-ready vertical stories using isolated agent worktrees. The workflow should be understandable without memorizing the specialist skill catalog and resumable across supported harnesses.

This feature changes the starter kit's workflow, artifacts, validation, adapters, and maintained knowledge. It does not add a sample application, introduce Express or Drizzle, redesign shared identity, change Keycloak policy, or deploy anything. Those are separate features unless the interview explicitly changes scope.

## Three developer flows

| Entry point         | Internal steps                                                                                                                 | Result                                                     |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------- |
| plan-feature        | Brief interview when needed, feature spec, independent critique, revisions                                                     | Critiqued spec in specs/features                           |
| plan-implementation | Vertical stories and dependencies, independent critique, revisions, one human approval                                         | Approved implementation plan in specs/implementation-plans |
| implement-feature   | Implementation, automated tests, adversarial review/fixes, integration, wiki/graph updates, audits, commit/push, PR submission | Verified feature PR ready for human merge                  |

The user selected this grouping in conversation on 2026-09-11. The single routine approval point is at the end of flow two and binds the exact specification, implementation plan, and delivery scope through feature PR submission. Flow three continues without repeated permission prompts for that already approved scope. Material ambiguity, changed scope or destination, missing actual authority, or blocking failures require resolution. PR merge and deployment remain outside this flow.

Critiques, tests, audits, and knowledge updates are internal steps, not extra developer commands. A small feature can be one vertical story. Use parallel writers only when independent slices justify them; do not manufacture extra stories or database/API/UI layers just to exercise the process. The current login/roles foundation is context for future application features, not a request to build those applications now.

## Historical reviewed baseline

- The implemented application is React Router Framework Mode with server-side BFF authentication, Postgres sessions, Keycloak, and a Java registration-approval listener. Express is a README placeholder; Drizzle and an existing-database migration framework are absent.
- Chromium/axe browser tests, Python tooling tests, worktree preflight, shared-stack locking, and per-worktree Graphify tooling already exist.
- There are 29 canonical skills, six rule cards, and 42 wiki concepts. The decomposition skill already describes vertical stories, but there is no executable feature-wide dispatch/resume contract.
- Current plan-feature names a next specialist and stops; implement-story requires separate explicit invocation. The state validator assumes GitHub publication of every planning artifact before durable completion.
- There are 15 legacy files in specs/plans and no prior feature-spec/implementation-plan directory split.
- ADR-0001 through ADR-0003 are proposed. PR #19 explicitly preserved that state; its merge does not establish acceptance of the proposals.

The baseline is supported by the [root commands](../../package.json), [web manifest](../../web/package.json), and [current planning contract](../../.agents-config/skills/dev/plan-feature/SKILL.md) at the source revision above. The documentation reconciliation is recorded in the [ADR register](../../wiki/adr/index.md). This is a repository/documentation review, not a new live runtime verification.

## Requirements

### REQ-001: Feature specification

Actor: developer and planning coordinator.
Behavior: create specs/features/YYYY-MM-DD-feature-slug.md with stable feature/requirement IDs, actor-visible outcomes, scope, non-goals, positive/denied/failure criteria, architecture questions, test expectations, and pending decisions. Interview only on material uncertainty.
Authority: a request to plan permits research and drafting; drafting never implies approval or publication.
Failure: unresolved material choices are explicit; contradictory or incomplete inputs prevent approval.
Evidence: valid/invalid fixtures, naming/path validation, and a clean-session resume exercise.

### REQ-002: Independent specification critique

Actor: independent reviewer.
Behavior: critique-feature-spec evaluates requirements, evidence, scope, ambiguity, feasibility, and acceptance criteria before implementation planning. Rename critique-plan and update active references, metadata, discovery links, templates, and validators.
Authority: reviewer can raise/dispose findings with evidence, but cannot grant human approval or accept risk.
Failure: unresolved blocking findings prevent advancement; changed specification invalidates its prior critique/approval as applicable.
Evidence: stale-digest and missing-criterion scenarios; critique tied to the exact document revision.

### REQ-003: Implementation plan and critique

Actor: planning coordinator and independent reviewer.
Behavior: plan-implementation evolves decompose-stories into specs/implementation-plans/YYYY-MM-DD-feature-slug.md. Include complete story packets, requirement coverage, dependency graph, affected layers, owned/shared paths, tests, rollback, and integration order. critique-implementation-plan independently evaluates feasibility, verticality, dependencies, and coverage.
Authority: the single routine approval at the end of flow two covers the exact critiqued specification, plan, and delivery through PR submission; it does not authorize merge or deployment.
Failure: missing dependencies, duplicate IDs, cycles, uncovered requirements, ownership conflicts, and unresolved architectural choices block readiness.
Evidence: deterministic validation of valid and adversarial plans; traceable critique disposition.

### REQ-004: Dependency-aware implementation

Actor: integration owner and story workers.
Behavior: implement-feature delivers implementation, tests, adversarial review/fixes, integration, knowledge updates, audits, and PR submission as one flow. It selects stories whose prerequisites are integrated and verified. Dispatch at most two disjoint writers, each on its own branch/worktree. A story may have dependents and still be ready. Recalculate readiness after each integration.
Authority: workers inherit bounded approved scope and path ownership; they cannot expand shared contracts, change identity policy, or publish beyond authorization.
Failure: blocked stories and their dependents remain blocked. Disjoint work can continue within the approved plan. A stale base or changed contract triggers revalidation.
Evidence: diamond dependency graph, failed prerequisite, ownership collision, stale base, interrupted worker, duplicate dispatch, and resume tests.

### REQ-005: Vertical delivery and shared resources

Actor: story worker.
Behavior: deliver one observable outcome across needed layers: schema/model, migration, service/BFF/API, UI, and tests. Use the actual project stack; justify layers that do not apply. Keep shared migrations, lockfiles, infrastructure, and integration files under one owner.
Authority: no automatic database/realm repairs or shared-service termination.
Failure: acquire the shared test-stack lock before live verification; verify the tested server belongs to the worktree; report missing prerequisites.
Evidence: existing ownership/locking tests plus scheduling scenarios; each integrated story has its declared tests and rollback evidence.

### REQ-006: Bounded independent review

Actor: independent reviewer and implementer.
Behavior: perform adversarial review appropriate to each story, fix findings, and rerun relevant checks. Working interpretation: at most five feature-level review-and-fix rounds, including final integration review. Targeted story reviews feed the same finding record; workers and resumed sessions cannot reset or multiply the budget.
Authority: no self-approval; only the designated human can accept material risk.
Failure: exhaustion means blocked, not passed. Persist round counts and findings across resume; changed revisions require re-review. Proposed blocking threshold is unresolved critical/high defects.
Evidence: limit exhaustion, stale review, repeated findings, retry counter persistence, reviewer independence, and final combined-diff checks.
The implementation uses this feature-level budget under the user-approved plan; ADR acceptance remains a separate record.

### REQ-007: Knowledge and ADR ownership

Actor: integration owner.
Behavior: refresh the local source graph after edit batches and integration; maintain wiki explanations/runbooks and ADRs for reusable decisions. Source-backed specs hold feature scope; GitHub holds delivery, review, and approval evidence under the proposed ownership model.
Authority: never mark an ADR accepted from inference. Record actual approver, accepted outcome, date, and evidence; existing draft ADRs retain IDs.
Failure: missing/stale graph triggers setup/refresh; extraction failure blocks graph-dependent verification. Missing approval leaves ADR proposed.
Evidence: graph checks, wiki audit, ADR provenance/lineage review, source verification, and no active-plan duplication into wiki.

### REQ-008: Harness portability and audit safety

Actor: any supported agent harness.
Behavior: canonical Markdown skills, portable Python validators, and explicit work packets remain harness-neutral. Provider adapters handle discovery, delegation, tool access, and invocation policy. Project discovery must not require rewriting global links in every worktree.
Authority: adapters preserve approval policy and worktree boundaries; global installation is a separately scoped operation.
Failure: unsupported capabilities are reported. Serial fallback preserves isolation; lack of an independent reviewer blocks that review gate rather than fabricating it.
Evidence: project-link parity, isolated-home global tests, two-worktree non-interference, clean-session transfer, and capability documentation. ORCA verification awaits the exact project/version.
Run skills-audit and rules-audit after additions or modifications; run wiki audit after knowledge changes.

### REQ-009: Legacy migration

Actor: integration owner.
Behavior: remove the 15 explicitly identified legacy specs/plans files after mapping still-relevant decisions and open gaps to maintained knowledge or new scoped proposals. Update active references and stop treating obsolete plans as application facts.
Authority: deletion is requested by the user; preserve Git history, unrelated files, and ignored stability-pilot drafts.
Failure: conflicting history is documented, never converted to fabricated accepted decisions.
Evidence: deletion manifest, active-link audit, historical source references pinned to the baseline commit, and unchanged unrelated drafts.

## Interview and decisions

The three-flow structure is selected by the user. Other entries are working defaults or compatibility limits, not additional routine interview gates. The later instruction "yes implement it then redo the PR" authorizes this implementation and updating PR #20.

| ID      | Decision                      | Status and outcome                                                                                                                                                    |
| ------- | ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DEC-001 | Workflow and approval cadence | User-selected: spec + critique; implementation plan + critique + approval; implementation + review + tests + PR. One routine approval at the end of flow two.         |
| DEC-002 | Stack scope                   | Working default: use the implemented stack. Express/Drizzle and sample apps belong to a separately scoped feature.                                                    |
| DEC-003 | Specification ownership       | Working default consistent with the requested folders: versioned specs define scope/plans; GitHub records delivery and attributable approval against their revisions. |
| DEC-004 | Review budget                 | Working interpretation: five feature-level review-and-fix rounds including integration, with unresolved blocking defects stopping delivery.                           |
| DEC-005 | ORCA identity                 | Exact project/version unknown. Keep the core portable and defer specific ORCA compatibility claims until identified.                                                  |

Keep two concurrent writers initially. Flow-two approval includes the feature branch push and PR submission so the same authorized scope does not need another routine publication prompt. Merge and release remain human-owned. Drafting and critique do not require GitHub publication.

## Definition of done

All approved requirements have executable or explicit procedural evidence. Skill/rule/wiki audits pass under their declared scopes. Workflow negative-path tests pass. Formatting and applicable tooling checks pass; story verification runs for affected behavior and the integration pilot. No secrets or generated graphs enter Git. Independent review covers approval binding, dependency scheduling, ownership, fixture cleanup, and hook preservation. A clean receiving session resumes from versioned artifacts and a sanitized checkpoint without the original chat.

## Portability sources

The [Agent Skills specification](https://agentskills.io/specification) defines portable package structure. The [client integration guide](https://agentskills.io/client-implementation/adding-skills-support) describes harness-side discovery and activation. These do not by themselves establish ORCA support or a universal parallel execution API.

## Implementation authorization

The user instructed: "yes implement it then redo the PR, we will start using this pattern for the features, right now I'm just trying to get the project stable before we start building". This authorizes implementing the reviewed plan on sdlc/feature-workflow-design and updating johnfabian/admin-starter-keycloak PR #20 targeting master. It does not accept historical ADR proposals or authorize merge/deployment. The previous source revision and baseline above remain historical evidence.

## Validated feature contract

```feature-spec
{
  "version": 2,
  "id": "FEAT-AGENT-WORKFLOW",
  "title": "Three-flow agent development",
  "scope": [
    "Workflow skills, portable contracts, isolated delivery and maintained knowledge"
  ],
  "nonGoals": [
    "Application features, identity policy, merge, deployment and unverified ORCA support"
  ],
  "requirements": [
    {
      "id": "REQ-001",
      "actor": "developer and planning coordinator.",
      "outcome": "create specs/features/YYYY-MM-DD-feature-slug.md with stable feature/requirement IDs, actor-visible outcomes, scope, non-goals, positive/denied/failure criteria, architecture questions, test expectations, and pending decisions. Interview only on material uncertainty.",
      "denied": "a request to plan permits research and drafting; drafting never implies approval or publication.",
      "failure": "unresolved material choices are explicit; contradictory or incomplete inputs prevent approval.",
      "acceptance": [
        "valid/invalid fixtures, naming/path validation, and a clean-session resume exercise."
      ]
    },
    {
      "id": "REQ-002",
      "actor": "independent reviewer.",
      "outcome": "critique-feature-spec evaluates requirements, evidence, scope, ambiguity, feasibility, and acceptance criteria before implementation planning. Rename critique-plan and update active references, metadata, discovery links, templates, and validators.",
      "denied": "reviewer can raise/dispose findings with evidence, but cannot grant human approval or accept risk.",
      "failure": "unresolved blocking findings prevent advancement; changed specification invalidates its prior critique/approval as applicable.",
      "acceptance": [
        "stale-digest and missing-criterion scenarios; critique tied to the exact document revision."
      ]
    },
    {
      "id": "REQ-003",
      "actor": "planning coordinator and independent reviewer.",
      "outcome": "plan-implementation evolves decompose-stories into specs/implementation-plans/YYYY-MM-DD-feature-slug.md. Include complete story packets, requirement coverage, dependency graph, affected layers, owned/shared paths, tests, rollback, and integration order. critique-implementation-plan independently evaluates feasibility, verticality, dependencies, and coverage.",
      "denied": "the single routine approval at the end of flow two covers the exact critiqued specification, plan, and delivery through PR submission; it does not authorize merge or deployment.",
      "failure": "missing dependencies, duplicate IDs, cycles, uncovered requirements, ownership conflicts, and unresolved architectural choices block readiness.",
      "acceptance": [
        "deterministic validation of valid and adversarial plans; traceable critique disposition."
      ]
    },
    {
      "id": "REQ-004",
      "actor": "integration owner and story workers.",
      "outcome": "implement-feature delivers implementation, tests, adversarial review/fixes, integration, knowledge updates, audits, and PR submission as one flow. It selects stories whose prerequisites are integrated and verified. Dispatch at most two disjoint writers, each on its own branch/worktree. A story may have dependents and still be ready. Recalculate readiness after each integration.",
      "denied": "workers inherit bounded approved scope and path ownership; they cannot expand shared contracts, change identity policy, or publish beyond authorization.",
      "failure": "blocked stories and their dependents remain blocked. Disjoint work can continue within the approved plan. A stale base or changed contract triggers revalidation.",
      "acceptance": [
        "diamond dependency graph, failed prerequisite, ownership collision, stale base, interrupted worker, duplicate dispatch, and resume tests."
      ]
    },
    {
      "id": "REQ-005",
      "actor": "story worker.",
      "outcome": "deliver one observable outcome across needed layers: schema/model, migration, service/BFF/API, UI, and tests. Use the actual project stack; justify layers that do not apply. Keep shared migrations, lockfiles, infrastructure, and integration files under one owner.",
      "denied": "no automatic database/realm repairs or shared-service termination.",
      "failure": "acquire the shared test-stack lock before live verification; verify the tested server belongs to the worktree; report missing prerequisites.",
      "acceptance": [
        "existing ownership/locking tests plus scheduling scenarios; each integrated story has its declared tests and rollback evidence."
      ]
    },
    {
      "id": "REQ-006",
      "actor": "independent reviewer and implementer.",
      "outcome": "perform adversarial review appropriate to each story, fix findings, and rerun relevant checks. Working interpretation: at most five feature-level review-and-fix rounds, including final integration review. Targeted story reviews feed the same finding record; workers and resumed sessions cannot reset or multiply the budget.",
      "denied": "no self-approval; only the designated human can accept material risk.",
      "failure": "exhaustion means blocked, not passed. Persist round counts and findings across resume; changed revisions require re-review. Proposed blocking threshold is unresolved critical/high defects.",
      "acceptance": [
        "limit exhaustion, stale review, repeated findings, retry counter persistence, reviewer independence, and final combined-diff checks."
      ]
    },
    {
      "id": "REQ-007",
      "actor": "integration owner.",
      "outcome": "refresh the local source graph after edit batches and integration; maintain wiki explanations/runbooks and ADRs for reusable decisions. Source-backed specs hold feature scope; GitHub holds delivery, review, and approval evidence under the proposed ownership model.",
      "denied": "never mark an ADR accepted from inference. Record actual approver, accepted outcome, date, and evidence; existing draft ADRs retain IDs.",
      "failure": "missing/stale graph triggers setup/refresh; extraction failure blocks graph-dependent verification. Missing approval leaves ADR proposed.",
      "acceptance": [
        "graph checks, wiki audit, ADR provenance/lineage review, source verification, and no active-plan duplication into wiki."
      ]
    },
    {
      "id": "REQ-008",
      "actor": "any supported agent harness.",
      "outcome": "canonical Markdown skills, portable Python validators, and explicit work packets remain harness-neutral. Provider adapters handle discovery, delegation, tool access, and invocation policy. Project discovery must not require rewriting global links in every worktree.",
      "denied": "adapters preserve approval policy and worktree boundaries; global installation is a separately scoped operation.",
      "failure": "unsupported capabilities are reported. Serial fallback preserves isolation; lack of an independent reviewer blocks that review gate rather than fabricating it.",
      "acceptance": [
        "project-link parity, isolated-home global tests, two-worktree non-interference, clean-session transfer, and capability documentation. ORCA verification awaits the exact project/version."
      ]
    },
    {
      "id": "REQ-009",
      "actor": "integration owner.",
      "outcome": "remove the 15 explicitly identified legacy specs/plans files after mapping still-relevant decisions and open gaps to maintained knowledge or new scoped proposals. Update active references and stop treating obsolete plans as application facts.",
      "denied": "deletion is requested by the user; preserve Git history, unrelated files, and ignored stability-pilot drafts.",
      "failure": "conflicting history is documented, never converted to fabricated accepted decisions.",
      "acceptance": [
        "deletion manifest, active-link audit, historical source references pinned to the baseline commit, and unchanged unrelated drafts."
      ]
    }
  ],
  "decisions": [
    {
      "question": "Which workflow grouping?",
      "status": "resolved",
      "disposition": "Three flows selected and implementation authorized by the user"
    },
    {
      "question": "ORCA adapter version?",
      "status": "deferred",
      "disposition": "No ORCA-specific compatibility claim; core remains portable"
    }
  ]
}
```
