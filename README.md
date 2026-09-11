# Admin Starter Keycloak

A pnpm workspace with an implemented React Router 7 server-rendered web/BFF, local Keycloak identity, shared Postgres state, Mailpit email capture, and an optional local Traefik gateway.

## What exists

| Area                   | State                      | Evidence and limits                                                                                                                                                     |
| ---------------------- | -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| React Router web/BFF   | Implemented                | Authorization code + PKCE, server-side token validation/refresh, opaque HttpOnly cookie, encrypted Postgres session records, and loader-based role guards under `web/`. |
| Keycloak               | Implemented local service  | Direct and gateway Compose files build a Keycloak 26.0 image with the registration-approval SPI. The realm and client are configured manually; no realm import exists.  |
| Postgres               | Implemented local service  | One instance per mode stores both Keycloak and `web_bff_sessions`. Init SQL runs only for an empty volume; no migration framework exists.                               |
| Mailpit                | Implemented local service  | SMTP capture on port 1025 with the inbox at `http://localhost:8025`.                                                                                                    |
| Traefik                | Implemented for local HTTP | Routes `app.localhost` and `auth.localhost`; the dashboard is intentionally insecure at `http://localhost:8081`. No production TLS edge exists.                         |
| Express resource API   | Placeholder                | `api-express/` contains a README only: no manifest, source, runtime, Compose service, or tests.                                                                         |
| Automated tests and CI | Local automation           | Local Chromium and Python tooling tests are configured. Hosted CI is deferred.                                                                                          |
| Production deployment  | Gap                        | TLS, secret management, migrations, observability, health checks, scheduled/offsite backups, and a provider design are not implemented.                                 |

## Architecture

```text
Browser
  -> React Router BFF (web/)
       -> Keycloak (identity and OIDC)
       -> Postgres (opaque BFF sessions)

Keycloak
  -> Postgres (realm, clients, roles, and users)
```

The browser never receives Keycloak access or refresh tokens. The BFF performs the OIDC exchange, verifies tokens with the realm JWKS, stores encrypted token state in Postgres, refreshes server-side, and applies exact-case `Users`/`Admins` role guards. The future Express seam is not part of the running architecture.

## Repository map

```text
.agents-config/     canonical shared skills and scoped rule cards
.agents/            flat Codex discovery symlinks
.claude/            flat Claude discovery symlinks
.agent-work/        optional ignored planning drafts and resumable state
api-express/        documentation-only resource API placeholder
api-gateway/        local Traefik Compose configuration
auth-server/        Keycloak image, Compose files, and custom provider
local-mail-server/  Mailpit Compose configuration
postgres/           direct/gateway Postgres and first-boot SQL
scripts/            backup, restore, and repository automation
specs/features/     dated feature specifications
specs/implementation-plans/  vertical stories and dependencies
web/                React Router application and BFF
wiki/               draft, evidence-backed durable repository knowledge
```

## Quick start

Install from the repository root:

```bash
corepack pnpm install
```

For direct mode, copy `.env.example` to `.env.development`, replace the placeholder secrets, then run the package scripts in dependency order:

```bash
corepack pnpm mail:up
corepack pnpm db:up
corepack pnpm auth:up
corepack pnpm dev
```

Open the app at `http://localhost:5173` and Keycloak at `http://localhost:8080`. `dev` starts only the web development server. Stop Keycloak and Postgres with `corepack pnpm stop-app`; stop Mailpit separately with `corepack pnpm mail:down`.

For gateway mode, copy `.env.traefik.example` to `.env.traefik`, replace placeholders, then run:

```bash
corepack pnpm dev:gateway
corepack pnpm dev:gateway:down
```

Open `http://app.localhost`, `http://auth.localhost`, and the local Traefik dashboard at `http://localhost:8081`.

## Verification

```bash
corepack pnpm check
```

The gate runs repository-wide Prettier checking, web ESLint, React Router type generation, and TypeScript. This command remains a static gate. Run test:fast for tooling tests and test:e2e for browser/identity characterization; hosted CI is deferred. Use `corepack pnpm web:build` when changing a build or server/client boundary, run `corepack pnpm verify:story` for build, graph, tooling and two consecutive browser passes. Subjective visual judgments remain a human limitation.

## Repository-native AI SDLC

The framework separates four kinds of information:

- [Shared skills](.agents-config/skills/) define reusable procedures. `.agents/skills/` and `.claude/skills/` are flat discovery symlinks to these canonical packages.
- [Scoped rules](.agents-config/rules/index.md) are short, imperative constraints selected by the files being changed.
- [The wiki](wiki/index.md) holds reusable architecture, policy, schema, convention, integration, and operational knowledge. Retrieve only relevant concepts.
- `.agent-work/<feature>/` holds ignored drafts, generated previews, digests, and resumable state. It is provisional working material, is never deleted automatically, and is not the durable feature record.

Versioned feature specifications live in `specs/features/YYYY-MM-DD-feature-slug.md`; implementation plans live in `specs/implementation-plans/YYYY-MM-DD-feature-slug.md`. GitHub issues/PRs hold approval, delivery evidence and handoffs tied to those revisions. The wiki explains maintained architecture; Graphify indexes source relationships.

### Three flows

1. **Plan feature** (`plan-feature`): brief interview, specification, independent critique and revision.
2. **Plan implementation** (`plan-implementation`): vertical stories, dependencies, independent critique and one scoped human approval.
3. **Implement feature** (`implement-feature`): isolated agents, tests, adversarial review/fixes, integration, wiki/graph updates, audits, commit/push and PR.

Say "plan this feature" or "implement this approved feature", or invoke the skill directly using `$skill-name` in Codex or `/skill-name` in Claude. Specialist steps run internally. Small features can use one story. Review the implementation in the same integration worktree and PR; a preliminary spec-only PR is optional.

Each writer uses a linked worktree. At most two writers work on disjoint dependency-ready slices; shared migrations, lockfiles and infrastructure have one integration owner. Use actual harness delegation and a separate reviewer, with serial fallback where parallel writing is unavailable. One feature-level review budget permits at most five rounds including final integration. Missing capabilities and unresolved blockers are reported, never marked passed.

`corepack pnpm workflow --help` exposes specification/plan validation, atomic claims, revision-bound checks/reviews, resume and PR publication checks. See the [execution contract](.agents-config/skills/dev/implement-feature/references/execution.md) and [wiki workflow](wiki/conventions/agent-development-workflow.md). The helper coordinates evidence; it does not itself spawn agents or authenticate approval.

The plan approval covers the exact specification/plan and named repository, branch, base and actions through PR submission. Already authorized routine steps do not ask again; changed scope/target needs resolution. Human merge and deployment remain separate. Checkpoints persist in authorized PRs/issues after exact read-back; ignored execution files remain provisional and are never deleted automatically.

Discovery policy comes from paired Claude/Codex package metadata. Project adapters are checked by default; global adapter installation requires `--global-adapters`. ORCA-specific integration is unverified.

### Skill catalog

`Explicit` means direct invocation or a required specialist step of the authorized flow. `On demand` means an agent may select it when the metadata clearly matches, and the user may still invoke it directly.

<!-- skills-catalog:start -->

| Skill                                                                                                                                                           | Invocation | Purpose                                                                                                                                                                                                               |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [adversarial-review](C:/1CodexApps/admin-starter-keycloak-worktrees/agent-automation/.agents-config/skills/dev/adversarial-review/SKILL.md)                     | On demand  | Independently challenge a plan, design, diff, tests, and controls from clean, read-only context, emphasizing negative and abuse paths.                                                                                |
| [architecture-impact](C:/1CodexApps/admin-starter-keycloak-worktrees/agent-automation/.agents-config/skills/dev/architecture-impact/SKILL.md)                   | On demand  | Assess feature impact across implemented application, identity, proxy, persistence, testing, operations, security, and compatibility boundaries.                                                                      |
| [critique-feature-spec](C:/1CodexApps/admin-starter-keycloak-worktrees/agent-automation/.agents-config/skills/dev/critique-feature-spec/SKILL.md)               | On demand  | Independently critique a feature specification for complete behavior, scope, evidence and acceptance criteria.                                                                                                        |
| [critique-implementation-plan](C:/1CodexApps/admin-starter-keycloak-worktrees/agent-automation/.agents-config/skills/dev/critique-implementation-plan/SKILL.md) | On demand  | Independently challenge vertical stories, dependencies, ownership and verification before scoped delivery approval.                                                                                                   |
| [evaluate-sdlc-pilot](C:/1CodexApps/admin-starter-keycloak-worktrees/agent-automation/.agents-config/skills/dev/evaluate-sdlc-pilot/SKILL.md)                   | On demand  | Review versioned skill-local scenarios, pilot failures, cycle evidence, security regressions, false positives, and clean-session results to recommend whether a formal evaluation framework is warranted.             |
| [feature-research](C:/1CodexApps/admin-starter-keycloak-worktrees/agent-automation/.agents-config/skills/dev/feature-research/SKILL.md)                         | On demand  | Produce read-only, evidence-backed feature research from repository code, Git history, relevant GitHub records, scoped rules, and targeted wiki concepts.                                                             |
| [find-edge-cases](C:/1CodexApps/admin-starter-keycloak-worktrees/agent-automation/.agents-config/skills/dev/find-edge-cases/SKILL.md)                           | On demand  | Identify material edge and abuse cases tied to approved requirements and affected boundaries, then assign each an acceptance, story, test, operational control, or accepted-risk disposition.                         |
| [graphify](C:/1CodexApps/admin-starter-keycloak-worktrees/agent-automation/.agents-config/skills/dev/graphify/SKILL.md)                                         | On demand  | Query and refresh this repository's local code graph for dependency tracing, change impact, and code discovery. Keep durable explanations and decisions in the OKF wiki.                                              |
| [handoff](C:/1CodexApps/admin-starter-keycloak-worktrees/agent-automation/.agents-config/skills/dev/handoff/SKILL.md)                                           | On demand  | Create a provider-neutral checkpoint that a clean session can resume without conversation history.                                                                                                                    |
| [implement-feature](C:/1CodexApps/admin-starter-keycloak-worktrees/agent-automation/.agents-config/skills/dev/implement-feature/SKILL.md)                       | On demand  | Deliver an approved feature through isolated stories, testing, independent review and a verified pull request.                                                                                                        |
| [implement-story](C:/1CodexApps/admin-starter-keycloak-worktrees/agent-automation/.agents-config/skills/dev/implement-story/SKILL.md)                           | On demand  | Implement one approved story with scoped worktree ownership, tests, independent review, and revision-bound evidence.                                                                                                  |
| [parallel-implementation](C:/1CodexApps/admin-starter-keycloak-worktrees/agent-automation/.agents-config/skills/dev/parallel-implementation/SKILL.md)           | On demand  | Coordinate bounded ownership, linked worktrees, merge order, and integration evidence for independent implementation slices.                                                                                          |
| [plan-feature](C:/1CodexApps/admin-starter-keycloak-worktrees/agent-automation/.agents-config/skills/dev/plan-feature/SKILL.md)                                 | On demand  | Create a dated feature specification with a brief interview and independent critique.                                                                                                                                 |
| [plan-implementation](C:/1CodexApps/admin-starter-keycloak-worktrees/agent-automation/.agents-config/skills/dev/plan-implementation/SKILL.md)                   | On demand  | Create vertical stories and a dependency plan, critique it independently, and obtain one scoped delivery approval.                                                                                                    |
| [preview-issues](C:/1CodexApps/admin-starter-keycloak-worktrees/agent-automation/.agents-config/skills/dev/preview-issues/SKILL.md)                             | On demand  | Render exact, non-mutating Markdown previews for proposed GitHub parent issues, child stories, dependencies, metadata, approval records, and comments.                                                                |
| [publish-issues](C:/1CodexApps/admin-starter-keycloak-worktrees/agent-automation/.agents-config/skills/dev/publish-issues/SKILL.md)                             | Explicit   | Publish only an exact, human-approved issue-and-comment preview to a named GitHub repository, preserving stable keys, relationships, metadata, approval evidence, read-back persistence, and idempotency.             |
| [react-pattern-review](C:/1CodexApps/admin-starter-keycloak-worktrees/agent-automation/.agents-config/skills/dev/react-pattern-review/SKILL.md)                 | On demand  | Perform a clean-context, read-only React and React Router pattern review that separates proven defects from maintainability opportunities and specifies characterization coverage before refactoring.                 |
| [record-adr](C:/1CodexApps/admin-starter-keycloak-worktrees/agent-automation/.agents-config/skills/dev/record-adr/SKILL.md)                                     | On demand  | Convert an attributable, human-approved, reusable architectural decision into an immutable OKF decision concept and update its index/log links.                                                                       |
| [repo-inventory](C:/1CodexApps/admin-starter-keycloak-worktrees/agent-automation/.agents-config/skills/dev/repo-inventory/SKILL.md)                             | On demand  | Produce a read-only, evidence-backed inventory of a repository's structure, Git state, application boundaries, agent guidance, package tooling, CI, tests, rules, and material uncertainties.                         |
| [requirements-interview](C:/1CodexApps/admin-starter-keycloak-worktrees/agent-automation/.agents-config/skills/dev/requirements-interview/SKILL.md)             | On demand  | Convert approved intent and research into stable, testable requirements, non-goals, decisions, and acceptance criteria.                                                                                               |
| [test-strategy](C:/1CodexApps/admin-starter-keycloak-worktrees/agent-automation/.agents-config/skills/dev/test-strategy/SKILL.md)                               | On demand  | Design a risk-based, layered test and verification strategy for a feature, refactor, or legacy characterization effort.                                                                                               |
| [wiki-audit](C:/1CodexApps/admin-starter-keycloak-worktrees/agent-automation/.agents-config/skills/dev/wiki-audit/SKILL.md)                                     | On demand  | Run a deterministic, read-only audit of an OKF v0.2 repository wiki for reserved-file structure, concept frontmatter, indexes, internal links, provenance, actors, lifecycle, freshness, and active planning leakage. |
| [wiki-init](C:/1CodexApps/admin-starter-keycloak-worktrees/agent-automation/.agents-config/skills/dev/wiki-init/SKILL.md)                                       | On demand  | Initialize or minimally bootstrap an OKF v0.2-compatible repository wiki from clear repository evidence.                                                                                                              |
| [wiki-update](C:/1CodexApps/admin-starter-keycloak-worktrees/agent-automation/.agents-config/skills/dev/wiki-update/SKILL.md)                                   | On demand  | Add, refresh, deprecate, or correct a small set of durable OKF v0.2 repository concepts from verified evidence.                                                                                                       |
| [wiki-visualize](C:/1CodexApps/admin-starter-keycloak-worktrees/agent-automation/.agents-config/skills/dev/wiki-visualize/SKILL.md)                             | On demand  | Deterministically generate and validate a self-contained, accessible offline HTML relationship viewer and manifest from an OKF v0.2 wiki bundle.                                                                      |
| [rules-audit](C:/1CodexApps/admin-starter-keycloak-worktrees/agent-automation/.agents-config/skills/meta/rules-audit/SKILL.md)                                  | Explicit   | Run a deterministic, read-only audit of centralized rule cards, provider rule symlinks, path scopes, enforcement/wiki links, conflicts, and the AI workflow invocation framework.                                     |
| [skills-audit](C:/1CodexApps/admin-starter-keycloak-worktrees/agent-automation/.agents-config/skills/meta/skills-audit/SKILL.md)                                | Explicit   | Audit and repair the typed shared skill catalog, README catalog, portable Python/uv automation, project discovery adapters, and optionally flat Claude/Codex global symlinks.                                         |
| [keycloak-admin](C:/1CodexApps/admin-starter-keycloak-worktrees/agent-automation/.agents-config/skills/ops/keycloak-admin/SKILL.md)                             | On demand  | Inspect and administer a configured Keycloak realm through its Admin CLI, and provision owned accounts for browser tests.                                                                                             |
| [prune-deleted-branches](C:/1CodexApps/admin-starter-keycloak-worktrees/agent-automation/.agents-config/skills/ops/prune-deleted-branches/SKILL.md)             | Explicit   | Find local branches whose upstream disappeared, verify each against a merged pull request, and delete only branches the user explicitly selects.                                                                      |
| [start-project](C:/1CodexApps/admin-starter-keycloak-worktrees/agent-automation/.agents-config/skills/ops/start-project/SKILL.md)                               | Explicit   | Start this repository's local development stack in dependency order, verify the containers and React Router development server, and report service URLs.                                                              |
| [stop-project](C:/1CodexApps/admin-starter-keycloak-worktrees/agent-automation/.agents-config/skills/ops/stop-project/SKILL.md)                                 | Explicit   | Stop this repository's local React Router development server and Docker development containers while preserving database volumes.                                                                                     |

<!-- skills-catalog:end -->

After adding, moving, renaming, or reviewing a skill, explicitly run `$skills-audit --fix`, then run its read-only audit. After changing rule cards or invocation policy, explicitly run `$rules-audit`.

### Project knowledge

- [Local stack runbook](wiki/operations/local-stack.md) and [environment variables](wiki/operations/environment-variables.md).
- [Keycloak realm/client facts](wiki/integrations/keycloak/realm-and-client-facts.md), [email verification](wiki/operations/verify-email-flows.md), and [admin-user workflow](wiki/operations/create-admin-user.md).
- [Local backup](wiki/operations/local-backup.md), [restore drill](wiki/operations/backup-restore-drill.md), and [known production gaps](wiki/architecture/known-production-gaps.md).

Newly migrated wiki knowledge remains draft and unverified until a human checks it against the running realm and intended operating model. Agent-framework automation under skill-local `scripts/` is portable Python invoked through `uv`. Existing operational backup/restore runbooks remain POSIX shell scripts; JavaScript `.mjs` files are tool configuration only.

## Automated agent setup

Use a linked worktree on a feature branch. Run corepack pnpm agent:setup -- --env-file <absolute-path>
to prepare locked dependencies, Chromium, hooks, and a local source graph without copying secrets.
Use test:fast before commits, test:e2e for real local Keycloak journeys, and verify:story for the full
build/graph/two-run verification. verify:commit checks staged graph input without changing the index.

The standalone tests/browser package has its own locked dependency policy. This avoids re-resolving
the existing application lockfile when installing browser tooling. No provenance/age controls are disabled.

See [worktree setup](wiki/operations/agent-worktrees.md), [Keycloak CLI](wiki/operations/keycloak-cli.md),
[local tests](wiki/testing/automated-local-verification.md), [graph ownership](wiki/conventions/code-graph.md),
and [ADRs](wiki/adr/index.md). Existing realm/client configuration repairs are proposed before applying them.
