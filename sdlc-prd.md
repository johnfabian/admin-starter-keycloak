> **Superseded historical design.** Retained for provenance, not active agent instructions. The current workflow is documented in [the wiki](wiki/conventions/agent-development-workflow.md) and implemented by the three canonical entry skills. Old skill names, explicit step gates and GitHub-only planning rules below describe the earlier design.

---

title: Enterprise Repository-Native AI SDLC Framework
document_type: Product Requirements Document
status: Draft for approval
version: 1.1
date: 2026-08-02
owner: Engineering Enablement

---

# Enterprise Repository-Native AI SDLC Framework

## Document control

| Field              | Value                                                                                            |
| ------------------ | ------------------------------------------------------------------------------------------------ |
| Status             | Draft for approval                                                                               |
| Decision requested | Approve phased implementation, governance model, and pilot scope                                 |
| Primary outcome    | Repeatable, evidence-based AI-assisted delivery without making either model the system of record |
| Execution surfaces | Claude Code and Codex remain interchangeable execution surfaces                                  |

## Executive summary

This PRD defines an enterprise, repository-native AI SDLC framework for planning, implementing, reviewing, and improving software changes. The framework keeps product intent, architecture knowledge, architectural decision records (ADRs), scoped implementation rules, skill packages, handoffs, evaluation data, and delivery evidence under version control. Claude Code and OpenAI Codex are interchangeable execution engines, not sources of truth.

The framework makes work predictable by turning a feature request into a controlled chain of small, reviewable artifacts: research, requirements, architecture impact, edge cases, vertical stories, critique, approved GitHub issues, implementation evidence, adversarial review, and a model-neutral handoff. GitHub is the feature and delivery system of record after approval. Each capability is an independently invokable skill. A thin `plan-feature` skill only orders stages, maintains ephemeral state, and asks for approval; it does not duplicate specialist instructions. Humans retain explicit authority over scope, architecture, risk acceptance, publication, merge, and production release.

Markdown is the default artifact format because engineers and agents can review, diff, and link it in Git. JSON is reserved for temporary workflow state, contracts, schemas, and deterministic evidence. The repository contains an Open Knowledge Format (OKF)-compatible knowledge bundle retrieved at runtime. It is the progressive-disclosure layer for architecture, ADRs, policy, schemas, conventions, and stable operational knowledge; agents retrieve only relevant concepts instead of preloading a large wiki. A separate, path-scoped rules layer supplies concise, imperative React, Express, testing, security, and style guidance only while work is in its scope.

The initial pilot targets the existing React Router 7 Framework Mode application acting as a BFF over an Express.js API, with Keycloak and Traefik in Docker. The framework requires a secure, observable vertical path from browser through BFF and gateway to API, identity, storage, and telemetry. It relies on tests, validators, policies, and approvals—not model self-attestation—to decide whether a change is done.

## 1. Problem and opportunity

Teams using coding agents often have inconsistent planning, long unstructured conversations, unclear ownership, model-specific instructions, and completion claims that are weakly connected to tests or operational evidence. The result is oversized issues, fragmented front-end/API work, duplicated code, security gaps, context loss, and expensive rework.

The opportunity is to introduce a lightweight control plane inside the existing repository. It should improve delivery quality without replacing GitHub, the current application stack, native Claude Code, or Codex. It must work incrementally: one feature, one story, and one evidence trail at a time.

## 2. Goals and non-goals

### Goals

- Produce small, vertical, independently testable stories from a feature request.
- Make each planning stage reusable through a self-contained skill and direct provider-native invocation.
- Preserve durable knowledge, decisions, and delivery evidence in the repository.
- Permit Claude/Codex switching without requiring the next agent to reconstruct a conversation.
- Make deterministic checks and human approval authoritative for readiness and completion.
- Enforce enterprise security, least privilege, auditability, and separation of duties.
- Improve outcomes through versioned, reproducible evaluations and operational feedback.
- Integrate with GitHub Issues and Projects without adding a new planning product.

### Non-goals

- Build a general autonomous-agent platform or replace native Claude Code/Codex workflows.
- Replace native Claude Code or Codex workflows with a custom execution platform.
- Automatically publish, close, rewrite, or reprioritize GitHub issues without defined approval.
- Replace the Express API, Keycloak, Traefik, or the existing deployment platform.
- Load the full wiki, all rules, or the whole repository into every agent context.
- Treat model-generated prose as proof that a requirement, test, or security control has passed.

## 3. Personas

| Persona                    | Need                                                        | Framework response                                                                          |
| -------------------------- | ----------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| Product owner              | Clear scope, tradeoffs, and approved backlog                | Feature brief, requirements, decisions, issue preview, approval gate                        |
| Staff engineer             | Architectural consistency and safe change boundaries        | Repository reconnaissance, architecture-impact artifact, OKF knowledge retrieval, ADR links |
| Implementer                | A bounded story with testable behavior and relevant context | Story packet, task-specific skill, TDD workflow, handoff state                              |
| Reviewer/security engineer | Independent evidence and a non-anchored view                | Clean-context review packet, deterministic evidence, threat and authorization checks        |
| Engineering manager        | Predictable throughput and measurable improvement           | Project views, milestone gates, trend telemetry, evaluation dashboard                       |
| Platform/SRE engineer      | Secure edge configuration and traceable operations          | Traefik/Keycloak boundary requirements, OpenTelemetry conventions, runtime evidence         |

## 4. Product principles

1. **The repository is the control plane.** Durable instructions, knowledge, ADRs, artifacts, schemas, and evidence are versioned with the code.
2. **Models propose; deterministic systems and authorized humans decide.** Tests, schemas, policy checks, and approval gates decide completion.
3. **One skill, one bounded job.** A skill contains its own instructions, templates, examples, scripts, and references; it does not reference files outside its folder for its operation.
4. **Direct invocation first.** Each capability is usable by itself as a skill; provider syntax is an adapter, and orchestration is optional and thin.
5. **Markdown for meaning; JSON for precision.** Markdown is the reviewable default. JSON carries state, contracts, schemas, results, and evidence.
6. **Vertical value over technical layers.** A story normally spans UI, BFF, API, authorization, data, tests, and telemetry where needed.
7. **Runtime retrieval over preload.** Retrieve only authoritative, relevant repository knowledge and record what was used.
8. **Independent verification.** The implementation agent cannot be the sole approver of its own work.
9. **Least privilege by workflow.** Research is read-only; planning does not publish; publication does not reinterpret requirements; production edits have a single owner.
10. **Measured improvement.** Improve skills and rules only through versioned evidence, evaluation results, and review.
11. **Knowledge explains; rules direct.** The wiki captures durable context and rationale; small, scoped rules prescribe verifiable implementation behavior. Neither replaces automated enforcement.

## 5. Target architecture

```text
GitHub Issues / Projects
  approved feature scope, decisions, stories, dependencies, status, handoffs
        | links to repository knowledge and CI/PR evidence
        v
Repository-native control plane
  AGENTS.md + CLAUDE.md: concise wiki/rule/skill routers
  .agents-config/skills: canonical, typed, self-contained shared capabilities
  .agents-config/rules: canonical, scoped implementation guidance
  .agents + .claude: flat provider discovery symlinks to the shared configuration
  wiki/: OKF-compatible progressive-disclosure layer
  CI + branch protection: deterministic gates
        |
        +--> Claude Code (native skills, subagents, hooks)
        +--> Codex (AGENTS.md, skills/subagents/customization)
        |
        v
React Router 7 BFF -> Traefik -> Express API -> Keycloak / persistence
        |
        v
OpenTelemetry collector -> approved telemetry backends
```

### 5.1 Repository layout

```text
/
├── AGENTS.md                          # concise router: wiki retrieval, skills, evidence
├── CLAUDE.md                          # concise Claude peer of AGENTS.md
├── .agents-config/                    # canonical shared configuration
│   ├── skills/
│   │   ├── meta/                      # configuration and audit workflows
│   │   ├── ops/                       # environment and operational workflows
│   │   └── dev/                       # development workflows and helpers
│   │       └── feature-research/
│   │           ├── SKILL.md
│   │           ├── templates/
│   │           ├── references/
│   │           └── scripts/
│   └── rules/                         # canonical concise, imperative rule cards
│       ├── index.md                   # path-to-rule catalog; loaded via router
│       ├── global.md
│       ├── react-router.md
│       ├── express.md
│       ├── testing.md
│       └── security.md
├── .agents/
│   ├── skills/                        # flat Codex symlinks to typed shared packages
│   └── rules -> ../.agents-config/rules
├── .claude/
│   ├── skills/                        # flat Claude symlinks to typed shared packages
│   └── rules -> ../.agents-config/rules
├── wiki/                              # OKF-compatible progressive-disclosure wiki
│   ├── index.md
│   ├── architecture/
│   ├── adr/                      # durable ADR register and decision index
│   ├── constitution/                   # enduring engineering tenets and decision rights
│   ├── policy/
│   ├── schemas/
│   ├── conventions/
│   └── operations/
├── .github/                           # issue forms, workflows, project views/integration
└── .agent-work/                       # gitignored, ephemeral drafts/state only; optional
```

`AGENTS.md` and `CLAUDE.md` must remain short bootstrap documents. Each shall include a **Using the wiki** section that directs the agent to start at `wiki/index.md`, search/retrieve only concepts relevant to the task, prefer current/high-trust concepts, verify claims against code or configuration, and record retrieved knowledge in the GitHub issue or PR when material. They shall also include an **Applying scoped rules** section that requires the agent to identify the changed-file paths, retrieve only matching rule cards before planning, editing, or reviewing, and run their mapped automated checks. They shall direct the agent to use a named skill for procedural work, not load all wiki concepts, rules, or skill instructions at session start. They must not become a second, ever-growing wiki.

The canonical package lives in `.agents-config/skills/<type>/<skill-name>/`, where `<type>` is `meta`, `ops`, or `dev`. The type classifies purpose only and does not determine invocation behavior. Each entry in `.agents/skills/` and `.claude/skills/` is a flat directory symlink to the same typed canonical package so both providers discover one source without copying it. These are discovery adapters only; they contain no instructions, scripts, or templates of their own. Global flat adapters may be deployed to the provider application roots by the explicit `skills-audit` workflow. Invocation behavior is package metadata: Claude reads `disable-model-invocation` from `SKILL.md`, and Codex reads `policy.allow_implicit_invocation` from `agents/openai.yaml`. Paired locks make a skill explicit-only; absent locks leave it eligible for contextual discovery. A mismatch is invalid, and every skill remains directly user-invokable. The shared package uses the portable Agent Skills subset (`name`, `description`, Markdown instructions, templates, references, and scripts). Provider-specific enhancements are optional and must be isolated within that package; the core workflow cannot depend on them.

`.agents-config/rules/` is distinct from the wiki and from skills: it is the canonical source for short, normative, implementation-time rule cards. A card declares applicable repository globs, concise required/prohibited practices, required checks, and authoritative style/lint configuration; explanation, tradeoffs, and architecture rationale link to the wiki instead of being copied into a rule. The `.agents/rules` and `.claude/rules` directory symlinks expose the same cards to both providers without duplicate bodies. Codex uses `AGENTS.md` to route to the matching canonical card before it changes or reviews a file. Codex’s experimental `.codex/rules/*.rules` mechanism is a separate command-approval control and must not be used as the source-style/routing layer.

### 5.2 Execution adapters

The framework defines provider-neutral contracts; thin adapters map them to native features:

| Concern                     | Claude Code adapter                                                       | Codex adapter                                                                                                       |
| --------------------------- | ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| Durable repo guidance       | `CLAUDE.md` plus project configuration                                    | Layered `AGENTS.md` guidance                                                                                        |
| Scoped implementation rules | `.claude/rules` symlink exposes matching shared cards                     | `AGENTS.md` routes to matching `.agents-config/rules/` card through `.agents/rules`                                 |
| User entry point            | Flat project symlink under `.claude/skills/`, invoked as `/skill-name`    | Flat project symlink under `.agents/skills/`; portable explicit invocation is `$skill-name` or `/skills` in CLI/IDE |
| Bounded parallel work       | Named subagent with constrained tools and worktree isolation when writing | Scoped subagent or separate review task; separate implementation chats run in Git worktrees                         |
| Mechanical enforcement      | Lifecycle hook, reviewed and allowlisted                                  | CI/policy checks; hooks only when appropriate to the active Codex surface                                           |
| Handoff                     | Structured GitHub issue/PR comment plus optional ephemeral JSON digest    | Same GitHub handoff and digest; no conversation transcript required                                                 |

Provider adapters may translate invocation syntax but may not change the GitHub record structure, evidence requirements, handoff contract, or approval policy. The framework calls these **skills**, not a separate command layer: Claude Code merges custom commands with skills, while Codex exposes skills through provider-specific explicit invocation and UI menus.

## 6. Detailed functional requirements

### FR-1: GitHub-backed feature record and ephemeral staging

GitHub Issues and Projects shall be the durable record for feature intent, requirements, decisions, story breakdown, acceptance criteria, dependencies, workflow status, review outcomes, and handoff. A local `.agent-work/<feature-id>/` folder is optional, gitignored, and provisional. It may contain unpublished drafts, short-lived workflow state, generated previews, and machine-readable digests while a planning run is active. It must not become a parallel authoritative archive of feature documents, and no skill may delete it automatically. After approval, the publisher writes issue/story definitions to GitHub issue bodies and writes approved stage artifacts and handoffs as immutable, idempotently keyed comments included in the exact approved preview. The publisher re-reads each record and captures its URL plus source and published-body digests before the workflow claims durable completion. Later cleanup requires explicit human direction; a later agent resumes from GitHub plus targeted wiki retrieval.

### FR-2: Self-contained skills and commands

Each canonical package shall live under `.agents-config/skills/<type>/` and include everything it needs inside its own folder: `SKILL.md`, templates, examples, scripts, and skill-local references. It shall not depend on external instruction files. Stage sequencing belongs in the orchestration skill; specialist workflow material and deterministic helper scripts belong in the relevant specialist skill, not a standalone workflows/scripts tree. A package may receive repository evidence, GitHub issue content, and retrieved wiki concepts as declared inputs, but its instructions must be portable and self-contained.

Each capability shall be independently invokable. Required initial catalog:

| Command                   | Skill responsibility                                                                               | Required output                                                                                  |
| ------------------------- | -------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `plan-feature`            | Thin orchestration: stage order, ephemeral resume state, approvals                                 | GitHub draft/checklist update and next-stage request                                             |
| `feature-research`        | Find analogous code, tests, GitHub history, and relevant wiki concepts                             | GitHub planning comment or draft issue section                                                   |
| `requirements-interview`  | Convert intent into testable requirements and decisions                                            | Feature issue body/decision comment                                                              |
| `architecture-impact`     | Identify affected boundaries, contracts, ADR needs, compatibility                                  | Feature issue architecture section and wiki/ADR links                                            |
| `find-edge-cases`         | Tie edge cases to requirements and dispositions                                                    | Feature issue risk/test section                                                                  |
| `decompose-stories`       | Produce smallest valuable vertical stories                                                         | Draft child issues/sub-issues                                                                    |
| `critique-plan`           | Independently challenge scope, gaps, dependencies, and tests                                       | Structured review comment                                                                        |
| `preview-issues`          | Render proposed GitHub changes without mutation                                                    | Ephemeral preview or GitHub draft                                                                |
| `publish-issues`          | Publish only approved preview; create relationships idempotently                                   | Created issue IDs/URLs and audit comment                                                         |
| `handoff`                 | Produce a provider-neutral checkpoint/resume packet for planning or implementation                 | Structured GitHub handoff comment plus evidence links                                            |
| `adversarial-review`      | Challenge plan, design, diff, tests, and controls from a clean, hostile-but-authorized perspective | Structured findings with evidence, exploit/precondition, severity, and disposition               |
| `parallel-implementation` | Create a bounded worktree/ownership plan for disjoint implementation slices                        | GitHub coordination comment: workers, path budgets, base ref, merge order, and integration owner |
| `wiki-init`               | Create and bootstrap a conformant wiki from repository evidence                                    | Initial `wiki/` structure, indexes, log, draft concepts, validation report                       |
| `wiki-update`             | Safely add, refresh, deprecate, or correct durable knowledge                                       | Reviewed concept/index/log updates and validation report                                         |
| `wiki-audit`              | Validate conformance, stale concepts, sources, and link integrity                                  | Read-only audit report; no silent mutations                                                      |
| `wiki-visualize`          | Generate a self-contained relationship viewer from the wiki                                        | `wiki/viz.html` and a generation manifest                                                        |
| `record-adr`              | Convert an approved, durable architectural decision into an ADR concept                            | Reviewed `wiki/adr/ADR-<id>-<slug>.md`, index/log updates, and GitHub cross-link                 |
| `rules-audit`             | Validate rule-card scope, conflicts, adapters, and automated enforcement mapping                   | Read-only rule coverage/conflict report; no silent mutations                                     |

### FR-3: Thin orchestration

`plan-feature` shall not contain detailed research, interview, decomposition, or critique instructions. It shall inspect the GitHub feature record and any current ephemeral state, validate declared outputs, invoke or direct the next skill, stop at approval gates, and record the stage transition on the feature issue. It shall never publish issues or code by default.

### FR-4: Research and knowledge retrieval

The research skill shall search the repository, relevant GitHub history, and the OKF bundle at runtime. Its GitHub output shall identify the evidence path, commit or version, retrieval query, source trust/freshness metadata, applicable rules, analogous implementation, tests, gaps, and uncertainty. Downstream stages consume the approved issue record and targeted evidence links rather than raw search transcripts.

### FR-5: Requirements and decisions

Requirements shall have stable identifiers, actors, observable expected behavior, authorization behavior, failure behavior, acceptance criteria, non-goals, and open decisions. The skill shall ask a human only questions whose answer materially changes scope, authorization, data ownership, compatibility, operational behavior, or cost/risk.

### FR-6: Architecture and security analysis

For the target stack, impact analysis shall explicitly consider React route/UI, React Router loader/action BFF boundary, Express contract and authorization, Keycloak identity/roles/session behavior, Traefik routing/headers/TLS, persistence, tests, audit events, and telemetry. It shall require an ADR when a decision changes a documented architectural constraint or has material, long-lived tradeoffs.

### FR-7: Edge-case analysis

Edge cases shall be relevant to a requirement or affected boundary and receive a disposition: acceptance criterion, story, test, operational control, or accepted risk. At minimum, the matrix shall consider identity, authorization, tenant/data ownership, malformed/duplicate/stale/concurrent data, browser behavior, dependency failure, deployment/configuration drift, observability, and abuse cases.

### FR-8: Story decomposition

A story shall represent one observable outcome, include acceptance and test requirements, and normally be a coherent vertical slice. The story tool shall identify dependencies and split only where the smaller unit retains independent value or sequencing is truly necessary. It shall reject horizontal UI-only/API-only/database-only decomposition unless called out as an enabling task with clear rationale.

### FR-9: GitHub preview and publication

The preview skill shall render issue title, type, parent, dependencies, scope, acceptance criteria, test/security/observability requirements, and definition of ready/done. The publisher shall use the approved preview as its only semantic input; it shall publish idempotently, record returned issue IDs/URLs on the parent issue, establish sub-issue and dependency relationships, assign allowed metadata, and never silently overwrite existing issue prose.

### FR-10: Implementation and evidence

Implementation workflows shall require an approved story packet and a pre-change baseline. They shall encourage TDD or characterization-first work for legacy/risky changes, then run required checks. Completion evidence shall contain tool name, command category, result, timestamp, repository revision, and relevant test/report location. Secrets, tokens, and sensitive production data shall be excluded.

### FR-11: Independent review

For defined risk levels, a separate model, person, or clean task shall review the diff. The reviewer receives the story, relevant rules, changed diff, test evidence, and known risks—not the implementer's private reasoning. Findings shall use a structured severity, evidence, and remediation format.

### FR-12: Handoff and recovery

Every completed planning or implementation stage shall generate enough persisted context to resume with either provider. A handoff shall name the feature/story, source revision, completed stage, current decision status, inputs/outputs, exact verification evidence, unresolved risks, next action, and retrieval references. It shall not rely on a copy of the conversation.

### FR-13: Governance and improvement

The framework shall version skills, templates, and wiki concepts. Proposed changes to policy, schemas, or skills must pass deterministic validation and required review before adoption. Production incidents, escaped defects, and significant agent failures shall be considered for conversion into redacted regression cases; a formal evaluation suite is a later decision, not a pilot prerequisite.

### FR-14: OKF wiki lifecycle

The framework shall provide explicit `wiki-init`, `wiki-update`, and `wiki-audit` skills. The wiki must be a conformant OKF v0.2 bundle with generated indexes, a reviewed log, traceable sources, and clearly surfaced trust/freshness state. Only durable reusable knowledge may enter the wiki. The update skill must be scoped and reviewable; the audit must be read-only and deterministic.

### FR-15: Static wiki relationship viewer

The framework shall provide `wiki-visualize`, which deterministically produces a self-contained `wiki/viz.html` and generation manifest from the committed bundle. It shall render standard Markdown links as a directed graph, surface concept trust/freshness/provenance, provide an accessible non-graph fallback, and operate without a backend or external network access at viewing time.

### FR-16: ADR lifecycle

The framework shall provide `record-adr` to create or update a durable ADR only after the associated GitHub decision is approved. Each ADR shall be a `Decision` concept in `wiki/adr/` with an immutable `ADR-<id>` identifier, context, decision, alternatives and consequences, decision status, approver/decision date, supporting evidence, and Markdown links to superseded or superseding ADRs. The linked GitHub issue or pull request retains the active discussion, options, approvals, and delivery context; the ADR records the reusable outcome and rationale. Superseded ADRs remain in the bundle with an explicit lifecycle/supersession link—never silently rewritten or deleted.

### FR-17: Scoped implementation rules

The framework shall maintain a separate `.agents-config/rules/` catalog of concise, versioned rule cards. Each card shall declare repository path globs, intent, required and prohibited practices, mandatory checks, and links to the authoritative formatter, linter, test configuration, or wiki rationale. Initial cards shall cover global engineering conventions, React Router/UI, Express/API, tests, security, and infrastructure as applicable. Before modifying or reviewing scoped files, an agent shall load only the matching cards and record material rule use in the pull request or GitHub handoff. `rules-audit` shall detect unmatched protected paths, overlapping/conflicting rules, provider symlink drift, stale wiki links, and rule claims that lack an automated enforcement mapping where one is feasible.

### FR-18: Human-in-the-loop decision gates

The framework shall route decisions to an authorized human through a GitHub issue, pull request, or approved change-management record; agent prose, reaction emojis, and inferred silence are not approval. Required human gates are: product owner approval before feature/story publication; staff engineer or architecture owner approval before a durable ADR becomes accepted; security owner approval before an identity, authorization, secrets, externally reachable edge, or material data-classification change proceeds; code owner review before merge; and release/change authority approval before production deployment. A human may accept a documented risk or policy exception only with owner, rationale, compensating controls, and expiry. The agent must stop and request a decision when the gate owner, scope, risk classification, or evidence is ambiguous.

### FR-19: Adversarial review

The framework shall provide `adversarial-review` for high-risk plans and changes. It runs in a clean context with a reviewer independent of the implementer and receives the approved requirements, threat model where applicable, relevant rules and wiki concepts, diff or design, and verification evidence—not private reasoning traces. The review shall test negative paths: authorization and tenant-boundary bypass, injection from repository/issue content, input/contract abuse, stale or concurrent state, secret/telemetry leakage, unsafe proxy/header assumptions, dependency failure, and rollback/operability gaps. Every finding records severity, preconditions, evidence or a reproducible test, recommended remediation, and disposition. Critical findings block publication, merge, or release until remediated or formally accepted by the designated human risk owner.

### FR-20: Session checkpoints and provider-neutral handoff

The framework shall use provider session history only as a convenience. It shall create a `handoff` checkpoint after every completed stage, before a human gate, before context compaction/provider switch, before an implementation worktree changes owner, and whenever a session is intentionally stopped. A local or copy/paste checkpoint is provisional. It becomes durable only as a structured GitHub issue/PR comment whose stable key, exact body, URL, digests, and read-back time have been verified; a small optional `.agent-work/` JSON digest may accompany it. The durable checkpoint is sufficient for a clean Claude Code or Codex session to resume without transcript access. Required fields are objective and scope; feature/story and GitHub links; base/current revision; branch/worktree identity; owned paths; completed work; applied rules and retrieved wiki IDs; decisions/gate status; exact check results; risks/blockers; persistence status; and one exact next action.

### FR-21: Parallel implementation and worktrees

The framework shall permit parallel implementation only after `parallel-implementation` publishes an approved coordination record. Each writing worker receives a separate Git worktree/branch, a bounded story or task, an explicit path ownership budget, a base revision, required interfaces/contracts, and an integration owner. The pilot limits concurrent writers to two and forbids parallel edits to the same files, package lockfiles, schema migrations, generated shared artifacts, deployment configuration, or release state. Read-only research, test analysis, and independent review may run in parallel without a worktree when they make no writes. Each worker posts its own evidence and handoff; the integration owner alone resolves conflicts, runs full cross-slice verification, and submits the merge-ready pull request. Worktree setup must not copy secrets by default, and worktrees are retained until their branch, evidence, and cleanup disposition are recorded.

## 7. Nonfunctional requirements

| ID     | Requirement                                                                                                                                                                                                                                    |
| ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| NFR-1  | Durable repository knowledge is version-controlled; durable feature planning, decisions, status, and handoffs are reviewable and traceable in GitHub; evidence links identify the relevant commit, check run, or immutable external reference. |
| NFR-2  | Skills have declared inputs/outputs, version IDs, and deterministic validation where possible.                                                                                                                                                 |
| NFR-3  | Routine planning stages must avoid loading unrelated files; retrieval evidence must permit audit of context used.                                                                                                                              |
| NFR-4  | No production change may be marked complete solely from an agent claim.                                                                                                                                                                        |
| NFR-5  | Publication and other external mutation require explicit authorization and idempotency keys/checks.                                                                                                                                            |
| NFR-6  | Framework execution must support least-privilege roles and secrets isolation.                                                                                                                                                                  |
| NFR-7  | The same artifact contract must be usable by Claude Code and Codex without translation of meaning.                                                                                                                                             |
| NFR-8  | When the team adopts formal evaluations, their results must be reproducible from pinned commits, fixture versions, prompts, model/provider, and policy version.                                                                                |
| NFR-9  | Telemetry must correlate a feature/story, revision, deploy, and runtime trace without including sensitive prompts, tokens, or PII by default.                                                                                                  |
| NFR-10 | The pilot must add no mandatory third-party planning SaaS or custom agent harness.                                                                                                                                                             |
| NFR-11 | Wiki concepts must expose provenance, trust, lifecycle, and freshness signals without treating them as authorization controls.                                                                                                                 |
| NFR-12 | The static wiki viewer must be reproducible from a known source revision and usable without network access at viewing time.                                                                                                                    |
| NFR-13 | Scoped rules must remain concise, path-specific, version-controlled, traceable to automated enforcement or an explicit exception, and separate from narrative wiki knowledge.                                                                  |
| NFR-14 | Human approvals and risk acceptances must be attributable, role-authorized, durable, and linked to the relevant artifact/revision.                                                                                                             |
| NFR-15 | Parallel writers must be isolated by worktree and path ownership; integration verification must run from a declared combined revision.                                                                                                         |

## 8. Workflow and gates

| Stage                  | Owner / mode                               | Input                                                  | Output                                          | Gate                                        |
| ---------------------- | ------------------------------------------ | ------------------------------------------------------ | ----------------------------------------------- | ------------------------------------------- |
| Intake                 | Product + planner                          | Raw request                                            | Draft parent feature issue                      | Feature ID assigned                         |
| Research               | Read-only skill                            | Request, runtime retrieval                             | Evidence-backed issue comment/section           | Evidence links valid                        |
| Requirements           | Planner + product                          | Request, research                                      | Feature issue requirements and decisions        | Decisions identified/answered               |
| Architecture impact    | Staff/security review                      | Requirements, research                                 | Feature issue impact section and wiki/ADR links | ADR/security review if triggered            |
| ADR record             | `record-adr` + architecture owner          | Approved durable decision                              | `wiki/adr/` ADR and GitHub cross-link           | Human approval; index/log/audit pass        |
| Edge cases             | Analyst                                    | Requirements, architecture                             | Feature issue risk/test section                 | Every material case disposed                |
| Story map              | Decomposer                                 | Approved feature record                                | Draft child issues/sub-issues                   | Verticality and testability checks pass     |
| Critique               | Clean-context reviewer                     | Feature issue and linked evidence                      | Structured review comment                       | Critical findings resolved or accepted      |
| Feature approval       | Product owner                              | GitHub feature and draft story preview                 | Attributable approval record in GitHub          | No implicit approval                        |
| GitHub preview/publish | Deterministic publisher                    | Approved issue draft/preview                           | Published IDs/relationships                     | Preview approved; idempotency pass          |
| Implement              | Single code owner                          | Story packet                                           | Diff + evidence                                 | Tests/policy gates pass                     |
| Adversarial review     | Independent clean-context reviewer         | Plan/design/diff/evidence                              | Findings and dispositions                       | Critical findings resolved or risk-accepted |
| Merge approval         | Code owner + security owner when triggered | Diff, evidence, reviews                                | PR approval                                     | Required checks and approvals pass          |
| Release approval       | Release/change authority                   | Merge-ready revision, rollout and operational evidence | Authorized deployment/change record             | Release controls satisfied                  |
| Learn                  | Owners                                     | Delivery/production evidence                           | Knowledge/eval update proposal                  | Normal review process                       |

### 8.1 Implementation patterns

- **Standard vertical slice:** research -> plan -> tests -> implementation -> independent verification.
- **Characterization-first:** capture current behavior with tests before changing risky legacy code.
- **Contract-first:** define BFF/Express request-response and authorization behavior before implementation.
- **Spike then discard:** time-box an experiment; record findings; do not merge spike code as production by default.
- **Security-sensitive:** threat analysis -> abuse/authorization tests -> implementation -> adversarial review.
- **Long-session checkpoint:** handoff -> `/compact` or a new provider session -> retrieve only referenced evidence -> continue from the exact next action.
- **Parallel research:** multiple read-only investigators may work independently; one synthesizer reconciles results.
- **Parallel implementation:** only disjoint, contract-bounded slices receive separate worktrees and path ownership; an integration owner merges and verifies the combined result. One agent owns any overlapping or shared artifact.

### 8.2 Human authority and intervention model

| Decision or transition                                      | Required human                                  | Agent role                                                  | Durable record                                                 |
| ----------------------------------------------------------- | ----------------------------------------------- | ----------------------------------------------------------- | -------------------------------------------------------------- |
| Feature scope, priorities, non-goals, and issue publication | Product owner or delegated delivery owner       | Prepare options, identify ambiguity, preview only           | Approved GitHub feature/preview                                |
| Reusable architecture decision / ADR                        | Architecture owner; security owner if triggered | Analyze alternatives and consequences; never self-accept    | Approved GitHub decision linked to ADR                         |
| Security-sensitive design, exception, or risk acceptance    | Designated security/risk owner                  | Produce evidence, threat/abuse cases, and mitigations       | Signed-off issue/PR/change record with expiry where applicable |
| Merge to protected branch                                   | Required code owner(s) and reviewers            | Implement, test, summarize, remediate findings              | Pull-request approvals and required checks                     |
| Production release, rollback, or emergency change           | Release/change authority                        | Provide rollout/rollback evidence; do not deploy by default | Change/deployment record                                       |
| Unclear authority, evidence, requirements, or conflict      | Named decision owner                            | Stop safely and ask a bounded question                      | GitHub blocker/comment or handoff                              |

### 8.2.1 Risk-triggered specialist checkpoints

These are proposed checkpoints, invoked only when their trigger is present; they are not a blanket committee for ordinary changes.

| Trigger                                                           | Specialist checkpoint               | Minimum decision evidence                                                                           |
| ----------------------------------------------------------------- | ----------------------------------- | --------------------------------------------------------------------------------------------------- |
| Public API, event, or cross-service contract change               | Architecture/API owner              | Compatibility plan, versioning/deprecation decision, consumer test evidence                         |
| Schema migration, backfill, deletion, or data ownership change    | Data owner + operations owner       | Migration/rollback plan, data validation, capacity/locking impact, recovery evidence                |
| Personal, regulated, or newly classified data                     | Privacy/security owner              | Data-flow/classification review, retention/access decision, redaction/logging controls              |
| New dependency, privileged integration, or supply-chain exception | Platform/security owner             | Provenance/license/vulnerability review, least-privilege configuration, owner and update plan       |
| Material user journey or accessibility impact                     | Product/design/accessibility owner  | User acceptance evidence, accessibility checks, rollout/support plan                                |
| SLO, capacity, cost, or operational resilience impact             | SRE/service owner                   | Load/failure evidence, telemetry/alerting changes, error budget/cost decision, rollback readiness   |
| Emergency production change or active incident                    | Incident commander/change authority | Time-bound scope, compensating controls, communications, post-change verification, follow-up record |

### 8.3 Session continuity and handoff protocol

Use the same provider session while it remains focused and the context is healthy. Before it becomes noisy or approaches compaction, invoke `handoff`; post the durable checkpoint; then compact, resume later, or begin a fresh Claude Code/Codex session. A fresh session starts from the GitHub artifact and only the listed wiki/rule references, verifies the declared revision/worktree, and performs the recorded next action. Do not rely on exported transcripts, private agent memory, or a hidden conversation summary as a release-critical record.

This protocol complements—not replaces—native facilities. Claude Code can resume/compact stored sessions; Codex supports long-running goals, context compaction, and app handoff between Local and Worktree. Those facilities improve usability, but the framework remains resumable even if a session is unavailable, compacted, provider-switched, or inspected by a human reviewer.

### 8.4 Parallel worktree policy

| Work type                                                                                | Parallel?       | Isolation and ownership                                                               |
| ---------------------------------------------------------------------------------------- | --------------- | ------------------------------------------------------------------------------------- |
| Repository/wiki/GitHub research, log analysis, test-gap discovery                        | Yes             | Read-only agents; summarized findings; no worktree required                           |
| Design critique or adversarial review                                                    | Yes             | Clean context and read-only checkout; no implementation ownership                     |
| Disjoint implementation stories                                                          | Conditionally   | One worktree and branch per writer; non-overlapping path budget and integration owner |
| Shared contracts, migrations, lockfiles, generators, CI, Traefik/Keycloak, release state | No during pilot | Single owner; other agents may review read-only                                       |
| Final integration, merge, and deployment                                                 | No              | Designated integration/release owner; protected-branch and release gates              |

## 9. Artifact standards

### 9.1 Markdown-first templates

Human- and agent-facing material shall be Markdown: OKF wiki concepts, GitHub issue bodies, issue comments, pull-request descriptions, and pre-publication drafts. YAML frontmatter is used only where lightweight metadata aids wiki discovery or a skill requires it. Required headings make content machine-checkable without turning GitHub planning into dense configuration.

```markdown
---
artifact: story-plan
schema-version: 1
feature-id: FEAT-104
status: draft
---

# STORY-001: Grant delegated access

## User outcome

An authorized account administrator grants a scoped delegated role to an eligible active user.

## Acceptance criteria

- [ ] Only authorized administrators may grant access.
- [ ] The operation is idempotent and auditable.
- [ ] The BFF and API reject an expired or unauthorized session.

## Test requirements

- Authorization integration test
- Duplicate-request test
- React Router action test
```

### 9.2 JSON-only uses

JSON shall be used for state, contracts, schemas, deterministic grader output, tool invocation payloads, and evidence. Example state:

```json
{
  "featureId": "FEAT-104",
  "workflowVersion": "1.0.0",
  "currentStage": "edge-case-analysis",
  "stages": {
    "research": "complete",
    "requirements": "complete",
    "architectureImpact": "complete",
    "edgeCases": "in_progress"
  },
  "approved": false,
  "github": { "parentIssue": "https://github.com/org/repo/issues/104" },
  "draftDigest": "sha256:..."
}
```

### 9.3 Provider-neutral handoff

The handoff shall be a structured GitHub issue or pull-request comment, not a separate feature document. It shall include: objective and scope; feature/story IDs; provider/session as optional provenance only; base/current revision; branch/worktree identity; owned paths; completed work; applied rule IDs; retrieved wiki IDs; checks and evidence links; decisions/assumptions and human gate status; remaining risks/blockers; persistence status and digests; exact next action; and the minimum retrieval references. During an active local run, a small JSON state/digest may sit in `.agent-work/`; it remains provisional until the exact comment is published and re-read successfully. No workflow deletes the local copy automatically, and any later cleanup requires explicit human direction. Handoff checkpoints are required at the boundaries in FR-20, not only at the end of a planning run.

### 9.4 Parallel-work coordination record

When parallel writing is approved, the parent GitHub issue carries one coordination comment. It lists each worker, worktree/branch, base revision, bounded outcome, owned and excluded paths, required contract/ADR/rule inputs, expected evidence, status, merge order, and the named integration owner. It is a coordination contract, not a task queue: workers may not expand their path budget or change a shared contract without returning to the parent issue and obtaining direction.

## 10. OKF-compatible wiki

The repository wiki shall target Google OKF v0.2: a self-contained directory tree of small Markdown concepts with YAML frontmatter. It shall use OKF’s progressive-disclosure indexes, standard Markdown cross-links, provenance, trust, freshness, and lifecycle signals. The wiki is for durable, reusable engineering knowledge—not feature-specific planning that belongs in GitHub. The framework treats the published specification as evolving and will record the targeted OKF version in the root index rather than maintaining a private fork.

```text
wiki/
├── index.md                           # root navigator; declares okf_version: "0.2"
├── log.md                             # dated, newest-first change history
├── architecture/
│   ├── index.md
│   ├── bff-boundary.md
│   ├── authorization.md
│   └── telemetry.md
├── domain/
│   └── index.md
├── adr/
│   ├── index.md
│   └── ADR-0042-bff-boundary.md
├── constitution/
│   └── index.md                       # enduring engineering tenets and decision rights
├── policy/
│   └── index.md
├── schemas/
│   └── index.md
├── conventions/
│   └── index.md
├── testing/
│   └── index.md
├── operations/
│   └── index.md
├── integrations/
│   └── index.md                       # React Router, Express, Keycloak, Traefik, OTel
├── references/                        # optional immutable source snapshots/attesters
└── viz.html                            # generated static viewer; never edited by hand
```

### 10.1 Bundle, concept, and navigation requirements

- The `wiki/` root is one OKF bundle. `index.md` and `log.md` are reserved navigation/history files, not concepts. The root index shall declare `okf_version: "0.2"`; nested indexes shall have no frontmatter.
- Every other Markdown file is a concept and shall have parseable YAML frontmatter with a non-empty `type`. The pilot taxonomy is `Architecture`, `Domain Model`, `Decision`, `Policy`, `Schema`, `Convention`, `Runbook`, `Integration`, `Test Strategy`, and `Reference`; these are local types, not changes to OKF. `wiki/constitution/` uses the `Policy` type for enduring engineering tenets, decision rights, and non-negotiable principles; it is not loaded wholesale into agent context.
- Every `index.md` lists its immediate concepts and subdirectories with one-sentence descriptions. Indexes are generated or updated by the wiki skills and are the default agent navigation path.
- `log.md` records reviewed changes newest-first under ISO 8601 date headings. Git history is authoritative for file-level diffs; the log explains meaningful knowledge changes.
- Concepts use bundle-relative Markdown links (for example `/architecture/bff-boundary.md`) for durable internal references. These links define the basic directed relationship graph. Broken links are reported by audit, but do not make the bundle invalid.
- A concept belongs in the wiki only when it is reusable beyond one active GitHub feature. Feature scope, acceptance criteria, delivery decisions, work status, and handoffs remain in GitHub; the wiki may be updated after delivery when reusable knowledge changed.

### 10.2 Concept metadata, trust, and freshness

Every new or materially updated concept shall include the recommended discovery fields `type`, `title`, `description`, and `tags`, plus `resource` when it describes a concrete system asset. The following OKF v0.2 fields are required by this framework for agent-generated or materially edited concepts unless genuinely inapplicable:

```yaml
---
type: Architecture
title: React Router BFF boundary
description: Browser-facing composition boundary between React Router and the Express API.
tags: [react-router, bff, authorization]
status: stable # draft | stable | deprecated
generated: { by: codex/<version>, at: 2026-08-02T00:00:00Z }
verified: { by: human:<id>, at: 2026-08-02T00:00:00Z }
stale_after: 2027-02-02
sources:
  - id: route-source
    resource: /apps/web/app/routes.ts
    title: Route configuration
    author: human:<id>
    last_modified: 2026-08-01
---
```

`generated` records authorship; `verified` records independent confirmation. The viewer and retrieval layer derive trust from the OKF signals: no verification is unverified, machine-only verification is machine-confirmed, and `human:<id>` verification is human-reviewed. These trust tiers are advisory, never authorization controls. A concept due at `stale_after` is surfaced as stale and is not used as the sole authority for a high-risk decision until refreshed or explicitly accepted. Policies, authorization designs, public API contracts, and production runbooks require a human verifier before `status: stable`.

### 10.3 ADRs as decision concepts

`wiki/adr/` is the canonical, repository-versioned ADR register. An ADR is a durable decision concept, not a duplicate issue template and not an all-purpose meeting record. It is created when a GitHub decision has been approved and the result changes an architectural constraint, establishes a reusable cross-team convention, or carries material, long-lived tradeoffs. A feature-level choice that affects only that delivery remains in GitHub.

```yaml
---
type: Decision
title: ADR-0042: React Router BFF boundary
description: Preserve Express as the domain API while using React Router server loaders/actions for browser-specific composition.
tags: [adr, react-router, bff]
adr_id: ADR-0042
decision_status: accepted                # proposed | accepted | superseded | deprecated
decided_on: 2026-08-02
approved_by: human:architecture-owner
status: stable
sources:
  - id: decision-record
    resource: https://github.com/org/repo/issues/104
    title: Approved feature decision
---
```

Its Markdown body shall use fixed headings: **Context**, **Decision**, **Alternatives considered**, **Consequences**, **Evidence and implementation links**, and, when applicable, **Supersedes** or **Superseded by**. The `decision_status` preserves ADR meaning while OKF `status` records concept lifecycle; an accepted ADR is normally `stable`. The decision index is generated/updated by the wiki skills and links active ADRs first, then superseded/deprecated records. A material architecture change must update or supersede the relevant ADR in the same approved change set, or explicitly state why it does not.

### 10.4 Skills for the wiki lifecycle

**`wiki-init`** shall create the structure above, root and child indexes, root log, `.gitignore` treatment for generated working files, and a baseline set of draft concepts from repository evidence. It shall record sources, avoid inferred facts without evidence, leave uncertain concepts as `draft`/unverified, and create no feature backlog. It runs only on explicit request and produces a reviewable initialization report.

**`wiki-update`** shall take a scoped trigger such as a merged pull request, approved architecture change, incident learning, or explicit correction. It shall retrieve only affected concepts, validate changed claims against code/configuration and sources, update `generated`, `verified` only when an actual verifier confirmed content, `status`, `stale_after`, applicable indexes, and the local `log.md`. It shall never rewrite unrelated concepts, fabricate verification, or turn a feature issue into a wiki page.

**`wiki-audit`** shall be read-only and deterministic. It checks the OKF conformance baseline, reserved-file rules, `type`, YAML parsing, index coverage, link graph, sources, actor format, trust/freshness status, generated-file freshness, and accidental active feature-planning content in the wiki. It reports broken links and stale concepts separately from hard conformance failures.

**`record-adr`** shall receive an approved GitHub decision and targeted supporting evidence, retrieve the affected ADR/index concepts, and create or update the smallest valid ADR record. It must allocate an immutable identifier, add required body sections and cross-links, preserve history, update the ADR index and root log, and post the resulting commit/path on the originating GitHub issue or pull request. It shall stop for human direction if approval, ownership, or the decision outcome is ambiguous.

### 10.5 Relationship visualization

**`wiki-visualize`** shall deterministically generate `wiki/viz.html` from the committed wiki. It shall require no backend, credentials, or network access at viewing time and shall embed only repository-approved data. The generated viewer shall:

- Render every concept as a node and every standard Markdown cross-link as a directed edge.
- Show hierarchy separately from cross-links; treat standard OKF links as untyped `references` edges because OKF v0.2 does not prescribe typed link edges.
- Display concept ID, type, tags, status, trust tier, `stale_after`, sources, and backlinks in a detail panel.
- Provide search by title/concept ID/tag; filters for type, status, trust, and stale state; and an accessible non-graph list fallback.
- Emit a manifest with source revision, generation time, generator version, concept count, edge count, and content digest.
- Be committed only when the team elects to version generated artifacts; otherwise CI publishes it as a build artifact. In either case, it is regenerated, never hand-edited.

If typed relationships are needed later, the framework may add a documented local frontmatter extension (for example `x_relationships`) without treating it as an OKF v0.2 field. The visualizer must continue to derive the canonical graph from normal Markdown links so it remains portable to other OKF consumers.

Knowledge ingestion is reviewed, attributable, and freshness-aware. Runtime retrieval starts with `wiki/index.md` or a search index generated from the bundle, then returns only directly relevant concepts. Agents validate claims against code/configuration where possible and state uncertainty where evidence is incomplete.

## 11. Scoped implementation rules

Rules are the implementation-time complement to the wiki: they tell an agent exactly how to work in a bounded area, while the wiki explains why the architecture or convention exists. They are not skills, architecture documents, or an alternative policy engine. A global card provides small universal defaults; every other card is path-scoped. Rule text must be short, imperative, testable, and non-duplicative. It must point to the repository’s actual formatter/linter/test configuration rather than restating it.

| Rule card              | Illustrative scope                                             | Required content                                                                                        |
| ---------------------- | -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `global.md`            | All repository changes                                         | Repository hygiene, evidence, accessibility/security baseline, required check discovery                 |
| `react-router.md`      | `apps/web/**/*.{ts,tsx,css}`                                   | Route/module conventions, loader/action BFF boundary, accessibility, component/style guidance, UI tests |
| `express.md`           | `services/api/**/*.ts`                                         | Input validation, authentication/authorization, error contract, idempotency/audit behavior, API tests   |
| `testing.md`           | Test files and changes that add behavior                       | Test level and fixtures, deterministic isolation, coverage/evidence expectations                        |
| `security.md`          | Identity, authorization, secrets, dependency, and edge changes | Threat/authorization checks, secrets handling, reviewer/escalation triggers                             |
| Infrastructure card(s) | `infra/**`, Traefik/Keycloak configuration                     | Approved topology, config validation, observability, rollback and security review triggers              |

The canonical card format is Markdown with a small YAML header. `paths` supports Claude’s native conditional loading; `applies_to` supports the provider-neutral catalog and Codex routing. `checks` names repository commands/configuration by category, not copied command strings that may drift.

```yaml
---
id: react-router
paths: ["apps/web/**/*.{ts,tsx,css}"]
applies_to: ["apps/web/**/*.{ts,tsx,css}"]
owner: frontend-platform
enforcement: [eslint, prettier, typecheck, route-tests]
wiki: [/architecture/bff-boundary.md, /conventions/frontend.md]
---
```

`AGENTS.md` routes Codex to `.agents-config/rules/index.md` and the matching card(s); it must instruct the agent to apply them before it reads or changes scoped implementation files. `CLAUDE.md` remains a short common router. The `.agents/rules` and `.claude/rules` directory symlinks expose the same path-scoped cards without imports or copied bodies. The audit verifies that both links resolve to the canonical catalog and are tracked as symlinks.

Rules govern agent behavior but do not guarantee correctness. Formatters, linters, type checks, tests, architecture tests, policy-as-code, branch protection, and human review remain the enforcement layers. Codex’s `.codex/rules/*.rules` is retained only if needed to govern out-of-sandbox command approval; it is not a replacement for this path-scoped engineering rules layer.

## 12. GitHub integration

GitHub Issues is the execution backlog; GitHub Projects supplies views, field-based tracking, and constrained automation. The recommended hierarchy is intentionally shallow:

```text
Initiative (optional)
└── Feature (parent issue)
    └── Story (sub-issue)
        └── Enabling task or defect (only when needed)
```

Use organization issue types such as Initiative, Feature, Story, Task, Bug, Spike, and Security. Use issue dependencies for blocking relationships, not prose alone. Use Projects fields for priority, risk, target milestone, owner, workflow state, and effort only when a decision needs them. Configure built-in auto-add narrowly and do not use it as an authorization bypass. GitHub issue forms standardize intake; the publisher populates body content from approved artifacts and uses supported API/CLI paths for fields and relationships.

For the pilot, capture approval state in immutable issue/PR comments or the approved change record, with the approver identity and artifact revision in the text. Do not rely on a Project status field, assignee, or reaction as evidence of human authorization. Add an optional `Implementation mode` field (`single-owner`, `parallel-worktrees`, `blocked`) only after the organization confirms it can be maintained reliably.

### Definition of ready

- Stable user outcome and scope/non-scope.
- Acceptance criteria, test strategy, dependencies, affected boundaries, and security/observability implications.
- Relevant decisions resolved or explicitly deferred.
- Story packet validated and approved.

### Definition of done

- Implemented behavior and tests satisfy approved acceptance criteria.
- Required lint/type/unit/integration/e2e/security/architecture checks pass with captured evidence.
- Independent review and risk sign-offs are complete where required.
- Operational instrumentation, docs, and rollout evidence are complete where applicable.

## 13. Context management

The framework shall treat context as a controlled input budget.

- Bootstrap guidance stays short; deeper knowledge is retrieved only when needed.
- For an implementation or review task, the agent first identifies affected paths and retrieves only matching scoped rule cards; it does not preload the full rules catalog.
- A skill accepts declared artifact inputs rather than the full prior chat transcript.
- Read-only subagents are used for bounded research, security analysis, test-gap discovery, and critique when their output can be summarized.
- The main orchestrator owns stage sequencing, decision recording, and final synthesis; agents do not approve their own work.
- Separate contexts are preferred for independent review to reduce anchoring.
- A handoff checkpoint is posted before compaction, provider switching, worktree transfer, or a voluntary session stop; native transcript/session storage is never the only recovery path.
- Each run records the artifact/revision inputs and retrieved knowledge IDs. Token metrics may be collected as operational data, but prompts and sensitive code are not exported by default.

## 14. Evaluation strategy

Quality is evaluated per skill, not only end-to-end. Formal evaluation infrastructure is intentionally deferred until the pilot skills and their GitHub-based delivery evidence are stable. In the pilot, retain a small, reviewed set of scenario cases and observed failures with the relevant skill, record model/provider, skill version, source revision, environment, duration, outcome, and evidence. Promote only proven cases into a formal evaluation suite later; do not create a central `evals/` directory as an initial prerequisite.

| Area               | Deterministic measures                                                           | Review/rubric measures                                              |
| ------------------ | -------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| Feature research   | Evidence paths exist; relevant tests/rules found                                 | Precision, useful coverage, uncertainty calibration                 |
| Requirements       | Required headings/IDs; criteria are present                                      | Clarity, ambiguity removal, decision quality                        |
| Decomposition      | Dependencies resolve; stories have tests                                         | Verticality, sizing, absence of hidden work                         |
| Critique           | Seeded defects found; output schema valid                                        | Recall, precision, severity calibration                             |
| Adversarial review | Findings include evidence/preconditions/disposition; critical-gate rule enforced | Realism, threat coverage, severity calibration, false-positive rate |
| Handoff            | Clean agent can resume using artifacts                                           | Sufficiency, context efficiency, no hidden assumptions              |
| Implementation     | CI/policy/test results; worker path budget respected                             | Maintainability, scope discipline, integration friction, no AI slop |

Seeded-defect fixtures, redacted incident regressions, adversarial repository-content cases, and contract/security cases are required. The framework shall measure false positives as well as defect recall. No model or rule change is promoted on anecdotal success alone.

## 15. Observability

The framework has two related telemetry planes:

1. **Application plane:** browser/BFF, Traefik, Express, Keycloak-adjacent authentication events, and infrastructure emit traces, metrics, and logs through OpenTelemetry-compatible instrumentation and a controlled collector.
2. **Engineering-control plane:** planning stage durations, validation outcomes, published issue IDs, evaluation scores, review findings, and release-to-story correlation are captured as minimal structured events.

Required correlation attributes include service name, deployment revision, environment, feature/story ID where safe, and trace/request identifiers. Treat trace headers arriving from untrusted clients as a security decision: validate/replace them at the trusted edge as appropriate. Never place authorization tokens, secrets, raw prompts, or sensitive business data in telemetry attributes.

Traefik provides logs, access logs, metrics, and tracing; its metrics can be exported through OTLP. The pilot must define route/service cardinality budgets, sampling, retention, redaction, and alert ownership before broad rollout.

## 16. Security and governance

- Enforce least privilege by stage: research is read-only; publishing requires a scoped GitHub identity; code changes use a single editor owner; production actions remain separately authorized.
- Require reviewed, allowlisted lifecycle hooks. Hooks can run with a user’s full permissions; they are not a substitute for CI or policy enforcement.
- Treat repository content, issue text, web pages, and model output as untrusted data. Skills must ignore instructions embedded in those inputs unless they are explicitly accepted requirements.
- Keep secrets in approved secret stores; do not place credentials in skills, handoffs, artifacts, prompts, or eval fixtures.
- Require threat modeling and explicit authorization-test coverage for identity, role, tenant, ownership, or payment changes.
- Treat adversarial review as a required independent gate for high-risk paths; a review finding does not itself authorize a risk acceptance.
- Do not let two writing agents edit a shared checkout or shared high-contention artifact; worktree isolation and protected-branch review remain mandatory.
- Use code owners/branch protection/required checks for skill, policy, schema, and knowledge changes.
- Retain audit evidence of publication, approvals, policy outcomes, and high-risk reviews consistent with enterprise retention policy.

### 16.1 Stack-specific boundary controls

**React Router BFF / Express.** The BFF is the browser-facing composition layer. It may call the Express API from server loaders/actions, but must not become an uncontrolled duplicate of domain logic. Contracts, error mapping, authorization propagation, CSRF/session policy, and retry/idempotency behavior are explicit and tested.

**Keycloak / Traefik.** For reverse-proxy deployment, adopt a documented TLS mode. If using re-encryption, restrict Keycloak to proxy traffic, configure trusted proxy addresses, and overwrite forwarded identity headers at Traefik. Do not expose Keycloak management metrics/health or administrative paths publicly. If TLS passthrough is used, do not configure proxy headers; use PROXY protocol only with the corresponding trust/network controls. These choices are configuration-specific and require a security review before release.

**Traefik.** Enforce TLS, explicitly configure trusted forwarding sources, set security response headers appropriate to the application, and keep dynamic routing/middleware configuration reviewed. Do not enable insecure forwarded-header trust in production.

## 17. Phased roadmap and milestones

| Phase                                                    | Scope                                                                                                                                                                                            | Milestone / exit criteria                                                                                                                                                        |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0. Baseline (2 weeks)                                    | Inventory current rules, CI, issue patterns, architecture, risks; select one pilot feature                                                                                                       | Baseline report, pilot owner, initial rule map and enforcement inventory                                                                                                         |
| 1. Foundations (2-3 weeks)                               | Bootstrap routers, shared skills location/symlinks, canonical/adapted scoped rules, `wiki-init`, `wiki-audit`, OKF root/child indexes and log, GitHub issue templates, lightweight staging state | One planning run publishes a complete, reviewable parent feature record; baseline wiki and rule catalog pass audit without a parallel feature-document archive                   |
| 2. Planning and wiki skills (3-4 weeks)                  | Research, requirements, architecture, edge cases, stories, critic, thin orchestrator, `wiki-update`, `record-adr`, `wiki-visualize`, `rules-audit`                                               | Two planned features pass review; each command independently usable; accepted architecture decision creates a valid ADR; `wiki/viz.html` renders the baseline relationship graph |
| 3. GitHub, handoff, and human gates (2-3 weeks)          | Preview/publisher, issue forms/types/project fields, `handoff`, authority matrix, approval evidence                                                                                              | Approved preview publishes idempotently; clean provider/session switch demonstrated without a transcript                                                                         |
| 4. Implementation controls (3-4 weeks)                   | Story packet gate, TDD/characterization workflows, adversarial-review packet, worktree coordination, policy checks                                                                               | Pilot story reaches done with complete evidence; two disjoint writers integrate safely in separate worktrees                                                                     |
| 5. Evaluation decision and security resilience (ongoing) | Review pilot evidence; decide whether a formal suite is warranted; add prompt injection and regression cases first                                                                               | Approved evaluation design or an explicit decision to continue with lightweight evidence collection                                                                              |
| 6. Observability and scale (ongoing)                     | OTel correlation, dashboards, governance cadence, portfolio rollout                                                                                                                              | Measurable trend improvement with reviewed telemetry controls                                                                                                                    |

## 18. Acceptance criteria for the pilot

- A product owner can explicitly start a feature with `/plan-feature` in Claude or `$plan-feature` in Codex, or independently invoke any listed planning skill. Implementation and publication workflow anchors also require explicit invocation; contextual specialist skills remain available through progressive disclosure.
- The orchestrator resumes correctly after a stopped stage using the GitHub feature record, targeted wiki retrieval, and any available ephemeral state.
- Every skill package is portable and self-contained; package lint verifies it has no external instruction-file dependency.
- `wiki-init` creates a valid `wiki/` bundle with root/child indexes and log; `wiki-audit` reports conformance, stale concepts, sources, and links without mutation.
- `wiki-update` refreshes only scoped, reusable concepts with sources and trust/freshness metadata; it does not turn a feature issue into a wiki page.
- An approved, reusable architectural decision produces a valid ADR in `wiki/adr/`, linked to its GitHub approval; a supersession preserves the original ADR and the relationship.
- `wiki-visualize` deterministically produces an accessible, self-contained `wiki/viz.html` with nodes, directed cross-link edges, detail metadata, filters, and a generation manifest.
- The canonical React Router and Express rule cards load only for their scoped files, identify their automated checks, and are consistent with their Claude adapters; `rules-audit` finds no unresolved conflict or protected-path gap.
- A feature produces a complete GitHub record, linked CI/PR evidence, and a provider-neutral GitHub handoff without creating a permanent parallel feature-document archive.
- The same feature can be handed from Claude Code to Codex, or the reverse, with a clean agent completing the declared next action without the original conversation.
- A product owner, architecture/security owner where triggered, code owner, and release authority each have an attributable approval record at their required gate; no agent approval is accepted.
- A high-risk change receives an adversarial review in a clean context, and every critical finding is remediated or explicitly risk-accepted by the designated human.
- A long-running session can compact or stop after posting a checkpoint; a fresh provider session resumes from the checkpoint and completes the declared next action without a transcript.
- Two disjoint implementation workers operate in separate worktrees with non-overlapping path budgets; the integration owner verifies the combined revision before merge.
- Story issues created during the pilot are vertical, approved, linked as sub-issues/dependencies when applicable, and visible in the selected GitHub Project view.
- GitHub preview is non-mutating; publisher requires approval and is idempotent.
- At least one BFF-to-Express story proves authorization, error behavior, tests, and telemetry across the defined path.
- Keycloak/Traefik configuration review covers trusted forwarding, exposed paths, TLS mode, and observability-header handling.
- Skill and workflow changes have evaluation evidence; no material promotion relies only on subjective claims.
- Security review finds no unmanaged secrets, unrestricted hook, or unapproved external mutation path in the pilot.

## 19. Risks and mitigations

| Risk                                                      | Mitigation                                                                                                                       |
| --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| Process overhead outpaces benefit                         | Pilot on one vertical slice; require each artifact to earn its place; track cycle time and rework                                |
| Skill duplication/drift across providers                  | Provider-neutral schemas/templates; thin adapters; contract tests for both paths                                                 |
| False confidence from agent reviews                       | Independent review plus deterministic gates and seeded-defect measurement                                                        |
| Context bloat                                             | Runtime retrieval, normalized artifacts, clean handoffs, and retrieval/audit logs                                                |
| Session loss or misleading compaction summary             | Durable GitHub handoff checkpoints at defined boundaries; clean-session resume drill                                             |
| Parallel work creates conflicting or unintegrated changes | Worktree/branch isolation, path budgets, shared-artifact serial ownership, integration owner, and combined-revision verification |
| Humans become a bottleneck or rubber-stamp approvals      | Risk-based authority matrix, concise evidence packets, explicit decision questions, and approval-cycle metrics                   |
| Prompt injection from repo/issue content                  | Treat all content as data; least-privilege tools; explicit policy and adversarial evals                                          |
| GitHub automation creates undesirable mutation            | Preview-first, approval, scoped token, idempotency, and audit evidence                                                           |
| Proxy/header misconfiguration affects security            | Platform-specific review checklist, trusted network topology, configuration tests, staged rollout                                |
| Knowledge becomes stale                                   | Source/freshness metadata, review owners, link checks, and incident-driven updates                                               |
| ADRs become duplicated or ignored                         | GitHub holds live decision work; `record-adr` writes only approved, reusable outcomes and preserves supersession history         |
| Rules become vague, duplicated, or context-heavy          | Small path-scoped cards, canonical source plus adapter checks, rule audit, and automated enforcement mappings                    |
| Generated graph diverges from the wiki                    | Generate from the committed bundle in CI; include source revision/digest in the manifest; prohibit hand edits to `viz.html`      |
| Metrics leak sensitive data or cost too much              | Attribute allowlist, redaction, cardinality budget, sampling, retention controls                                                 |

## 20. Open questions

1. Which organization issue types and project fields are already available in the target GitHub Enterprise configuration?
2. Which changes require human approval: plan, issue publication, pull request, deployment, or all high-risk categories?
3. What is the desired retention and access model for control-plane evidence and telemetry?
4. Which identity/session design is used between browser, React Router BFF, Express, and Keycloak (cookie, token exchange, or another approved pattern)?
5. Which Traefik/Keycloak TLS topology is approved for the target environments?
6. What CI environments and test levels are feasible for the initial pilot?
7. Which evaluation thresholds (recall, false-positive rate, cycle time, rework) qualify a skill/rule change for promotion?
8. What data classification rules govern code, prompts, logs, traces, and generated artifacts?
9. Which teams own the initial React Router, Express, testing, security, and infrastructure rule cards, and which checks are authoritative for each?
10. Which decision thresholds require an ADR rather than a feature-level GitHub decision, and who is authorized to approve each ADR class?
11. Which issue/PR mechanism is authoritative for approval evidence in the target GitHub Enterprise configuration, and how will delegation be recorded?
12. Which artifact categories are high-contention in this repository (migrations, lockfiles, generated code, environment config), and therefore serial during the pilot?
13. What maximum concurrent-writer count, worktree provisioning method, and local-environment setup are supportable for the pilot?

## 21. 2026 verification notes

The following are verified external-platform facts used by this PRD as of 2026-08-02. Architecture choices and policy requirements in this document are recommendations, not claims that the platforms enforce automatically.

| Area                              | Verified fact and implication                                                                                                                                                                                                                                                                                       | Source                          |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------- |
| Claude Code subagents             | Custom subagents have separate contexts, configurable tool access/permissions, and project scope. Use them for bounded research and independent review, not overlapping production edits.                                                                                                                           | [S1]                            |
| Claude Code skills/commands       | A project skill directory under `.claude/skills/` exposes a slash command based on its directory name; skills support arguments and isolated forked context. This supports directly invokable capabilities and a thin orchestration skill.                                                                          | [S2]                            |
| Claude Code hooks                 | Hooks can execute shell commands, HTTP endpoints, or LLM prompts during lifecycle events; command hooks run with the user’s full permissions. Treat hooks as high-risk reviewed automation.                                                                                                                         | [S3]                            |
| Claude Code scoped rules          | Claude Code discovers Markdown rules under `.claude/rules/`; rules with `paths` frontmatter load when matching files are read, while unscoped rules load at launch. Use path-scoped adapters to keep React/Express guidance out of unrelated context.                                                               | [S23]                           |
| Codex guidance                    | Codex reads layered `AGENTS.md` files from global/project scopes; closer files override earlier guidance and the combined project guidance has a configured size limit. Keep bootstrap instructions concise and scoped.                                                                                             | [S4]                            |
| Codex command rules               | Codex `.rules` files control which commands run outside the sandbox and are experimental; they are not file-type style or engineering-practice rules. Keep command approval separate from the shared implementation rule-card layer.                                                                                | [S24]                           |
| Skill invocation semantics        | Claude Code invokes project skills as `/skill-name`. In Codex CLI/IDE, direct skill invocation uses `$skill-name` or `/skills`; in the desktop app enabled skills also appear in the slash menu. Treat the shared capability as a skill, not as a portable literal slash command.                                   | [S2], [S20], [S25]              |
| Sessions, compaction, and handoff | Claude Code can resume/compact local sessions; Codex offers long-running goals, context compaction, and desktop handoff between Local and Worktree. These are useful ergonomics, but the durable GitHub checkpoint remains the cross-provider recovery record.                                                      | [S26]-[S28]                     |
| Parallel subagents and worktrees  | Both providers support bounded parallel work and Git worktrees. Codex explicitly advises against two concurrent chats writing the same files; Claude documents worktree isolation for parallel sessions/subagents. Use the framework’s worktree and path-ownership policy for all parallel writes.                  | [S1], [S21], [S27], [S29]-[S30] |
| Shared skills                     | Codex discovers repository skills from `.agents/skills`; Claude Code discovers project skills from `.claude/skills`, and both support symlinked packages. The PRD therefore keeps typed canonical packages in `.agents-config/skills` and exposes flat provider-specific discovery symlinks.                        | [S2], [S20]                     |
| GitHub Issues/Projects            | GitHub supports sub-issues, issue types, dependencies, Projects fields/views, and constrained project auto-add workflows. Use a shallow hierarchy and preview-first publication.                                                                                                                                    | [S5]-[S8]                       |
| OKF                               | Google’s OKF v0.2 specification defines a directory of Markdown concepts with YAML frontmatter, progressive-disclosure indexes, logs, cross-links, provenance, trust, freshness, and lifecycle signals. Google’s reference repository also includes a static interactive graph viewer generated from an OKF bundle. | [S9]-[S10], [S22]               |
| React Router 7                    | Framework Mode adds framework capabilities around React Router’s data features, and React Router documents the BFF pattern where loaders/actions call an existing backend API. Preserve the Express domain API and keep BFF logic browser-specific.                                                                 | [S11]-[S12]                     |
| Keycloak behind proxy             | Keycloak documents re-encryption, edge, and passthrough TLS modes; its guidance requires trustworthy forwarded headers/network restrictions and says management port 9000 should not be proxied publicly.                                                                                                           | [S13]                           |
| Traefik                           | Traefik documents security headers, trusted forwarded-header configuration, logs/access logs/metrics/tracing, and OTLP metrics. Avoid insecure forwarded-header trust in production.                                                                                                                                | [S14]-[S17]                     |
| OpenTelemetry                     | OpenTelemetry is a vendor-neutral observability framework for traces, metrics, and logs, with a tracing API/specification. Use a collector and governance controls rather than embedding a vendor coupling in application code.                                                                                     | [S18]-[S19]                     |

### Sources

- [S1] Anthropic, “Create custom subagents,” https://code.claude.com/docs/en/sub-agents
- [S2] Anthropic, “Extend Claude with skills,” https://code.claude.com/docs/en/skills
- [S3] Anthropic, “Hooks reference,” https://code.claude.com/docs/en/hooks
- [S4] OpenAI, “Custom instructions with AGENTS.md,” https://learn.chatgpt.com/docs/agent-configuration/agents-md
- [S5] GitHub Docs, “About issues,” https://docs.github.com/en/issues/tracking-your-work-with-issues/learning-about-issues/about-issues
- [S6] GitHub Docs, “Adding sub-issues,” https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/adding-sub-issues
- [S7] GitHub Docs, “Adding items automatically,” https://docs.github.com/en/enterprise-cloud@latest/issues/planning-and-tracking-with-projects/automating-your-project/adding-items-automatically
- [S8] GitHub Docs, “Adding and managing issue fields,” https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/adding-and-managing-issue-fields
- [S9] Google Cloud Blog, “Open Knowledge Format v0.2 tackles agentic trust,” https://cloud.google.com/blog/products/data-analytics/okf-v0-2-adds-trust-signals/
- [S10] GoogleCloudPlatform, “Open Knowledge Format specification,” https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md
- [S11] React Router, “Picking a mode,” https://reactrouter.com/start/modes
- [S12] React Router, “Backend For Frontend,” https://reactrouter.com/explanation/backend-for-frontend
- [S13] Keycloak, “Configuring a reverse proxy,” https://www.keycloak.org/server/reverseproxy
- [S14] Traefik, “Headers,” https://doc.traefik.io/traefik/reference/routing-configuration/http/middlewares/headers/
- [S15] Traefik, “EntryPoints,” https://doc.traefik.io/traefik/reference/install-configuration/entrypoints/
- [S16] Traefik, “Observability overview,” https://doc.traefik.io/traefik/v3.4/observability/overview/
- [S17] Traefik, “Metrics,” https://doc.traefik.io/traefik/reference/install-configuration/observability/metrics/
- [S18] OpenTelemetry, “What is OpenTelemetry?” https://opentelemetry.io/docs/what-is-opentelemetry/
- [S19] OpenTelemetry, “Tracing API,” https://opentelemetry.io/docs/specs/otel/trace/api/
- [S20] OpenAI, “Build skills,” https://learn.chatgpt.com/docs/build-skills
- [S21] OpenAI, “Subagents,” https://learn.chatgpt.com/docs/agent-configuration/subagents
- [S22] GoogleCloudPlatform, “Open Knowledge Format README and visualizer reference,” https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/README.md
- [S23] Anthropic, “How Claude remembers your project,” https://code.claude.com/docs/en/memory
- [S24] OpenAI, “Rules,” https://learn.chatgpt.com/docs/agent-configuration/rules
- [S25] OpenAI, “Slash commands,” https://learn.chatgpt.com/docs/reference/slash-commands
- [S26] Anthropic, “Manage sessions,” https://code.claude.com/docs/en/sessions
- [S27] OpenAI, “Worktrees,” https://learn.chatgpt.com/docs/environments/git-worktrees
- [S28] OpenAI, “Long-running work,” https://learn.chatgpt.com/docs/long-running-work
- [S29] Anthropic, “Run parallel sessions with worktrees,” https://code.claude.com/docs/en/worktrees
- [S30] Anthropic, “Run agents in parallel,” https://code.claude.com/docs/en/agents
