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
| Automated tests and CI | Gap                        | No test runner, test files, or CI workflow is configured. The current gate is static only.                                                                              |
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
specs/plans/        legacy dated implementation records awaiting pilot migration
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

The gate runs repository-wide Prettier checking, web ESLint, React Router type generation, and TypeScript. It does not run unit, integration, browser, identity-flow, Compose, or CI checks because none are configured. Use `corepack pnpm web:build` when changing a build or server/client boundary, then exercise relevant runtime flows manually.

## Repository-native AI SDLC

The framework separates four kinds of information:

- [Shared skills](.agents-config/skills/) define reusable procedures. `.agents/skills/` and `.claude/skills/` are flat discovery symlinks to these canonical packages.
- [Scoped rules](.agents-config/rules/index.md) are short, imperative constraints selected by the files being changed.
- [The wiki](wiki/index.md) holds reusable architecture, policy, schema, convention, integration, and operational knowledge. Retrieve only relevant concepts.
- `.agent-work/<feature>/` holds ignored drafts, generated previews, digests, and resumable state. It is provisional working material, is never deleted automatically, and is not the durable feature record.

Approved feature scope, stories, decisions, review evidence, stage artifacts, and handoffs belong in GitHub issues and immutable comments. Issue bodies hold the approved parent and story definitions. Stable, idempotently keyed comments hold approved planning stages and checkpoints. Publication is complete only after those records are re-read and their URLs and digests are verified.

### Invoking skills

All skills can be invoked directly. Use `$skill-name` in Codex and `/skill-name` in Claude Code. A package is explicit-only when both `disable-model-invocation: true` in `SKILL.md` and `policy.allow_implicit_invocation: false` in `agents/openai.yaml` are present. Its `meta`, `ops`, or `dev` directory describes purpose, not invocation policy.

Start or resume feature planning explicitly with `$plan-feature` or `/plan-feature`. Configuration, local-environment, destructive Git, planning-anchor, implementation, publication, and audit workflows are also explicit-only. Other skills may be selected when their metadata matches the task, but naming them directly remains the clearest way to request a particular procedure.

### Planning a new feature

1. Create a topic branch from the default branch. Do not plan or implement directly on `master`, and do not create a worktree under the current repository policy.
2. Invoke `$plan-feature`. It validates the feature record and optional `.agent-work` state, then identifies exactly one next stage; it does not perform specialist analysis itself.
3. Complete the planning stages in order:

   ```text
   feature-research
     -> requirements-interview
     -> architecture-impact
     -> find-edge-cases
     -> test-strategy
     -> decompose-stories
     -> critique-plan
   ```

4. Stop for attributable human feature approval. An agent claim, reaction, assignee, or status field is not approval.
5. Run `preview-issues` to render the exact parent issue, child issues, relationships, approved stage comments, and handoffs. Any edit changes the SHA-256 digest and requires a new preview.
6. After a human approves that exact digest and authorizes mutation, explicitly invoke `$publish-issues`. It creates or reuses exact stable markers, never silently rewrites history, and verifies every published record by reading it back.
7. Persist the returned GitHub URLs, source-artifact digests, published-body digests, and verification times. Until that persistence gate passes, local artifacts and handoffs remain provisional and planning is not durably complete.
8. Implement only an approved, independently verifiable story by explicitly invoking `$implement-story`. Characterization/TDD evidence, independent review, and a durable handoff remain story gates.

Use `handoff` after each completed stage, before a human gate, provider/session change, compaction, ownership transfer, or intentional stop. Before GitHub publication, its local Markdown is provisional. No workflow deletes `.agent-work`; later cleanup always requires explicit human direction.

### Skill catalog

`Explicit` means the user must invoke the skill. `On demand` means an agent may select it when the metadata clearly matches, and the user may still invoke it directly.

<!-- skills-catalog:start -->

| Configuration and operations skill                                                  | Invocation | Purpose                                                                                      |
| ----------------------------------------------------------------------------------- | ---------- | -------------------------------------------------------------------------------------------- |
| [rules-audit](.agents-config/skills/meta/rules-audit/SKILL.md)                      | Explicit   | Audit centralized rule scope, links, adapters, and invocation policy without mutation.       |
| [skills-audit](.agents-config/skills/meta/skills-audit/SKILL.md)                    | Explicit   | Categorize and validate packages, the README catalog, and project/global discovery symlinks. |
| [prune-deleted-branches](.agents-config/skills/ops/prune-deleted-branches/SKILL.md) | Explicit   | Verify merged upstream-deleted branches and remove only selections the user authorizes.      |
| [start-project](.agents-config/skills/ops/start-project/SKILL.md)                   | Explicit   | Start and verify the repository's local development stack.                                   |
| [stop-project](.agents-config/skills/ops/stop-project/SKILL.md)                     | Explicit   | Stop local services while preserving database volumes.                                       |

| Planning and delivery skill                                                           | Invocation | Purpose                                                                                                |
| ------------------------------------------------------------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------ |
| [plan-feature](.agents-config/skills/dev/plan-feature/SKILL.md)                       | Explicit   | Validate planning gates and direct the next specialist without duplicating its work.                   |
| [feature-research](.agents-config/skills/dev/feature-research/SKILL.md)               | On demand  | Gather read-only repository, history, GitHub, rule, and wiki evidence.                                 |
| [requirements-interview](.agents-config/skills/dev/requirements-interview/SKILL.md)   | On demand  | Convert approved intent and research into stable, testable requirements and decisions.                 |
| [architecture-impact](.agents-config/skills/dev/architecture-impact/SKILL.md)         | On demand  | Assess affected application, identity, data, proxy, security, testing, and operational boundaries.     |
| [find-edge-cases](.agents-config/skills/dev/find-edge-cases/SKILL.md)                 | On demand  | Identify edge and abuse cases and assign each a concrete disposition.                                  |
| [test-strategy](.agents-config/skills/dev/test-strategy/SKILL.md)                     | On demand  | Map risks and requirements to deterministic test and verification layers.                              |
| [decompose-stories](.agents-config/skills/dev/decompose-stories/SKILL.md)             | On demand  | Produce small, vertical, independently valuable story previews.                                        |
| [critique-plan](.agents-config/skills/dev/critique-plan/SKILL.md)                     | On demand  | Independently challenge scope, evidence, dependencies, tests, and approval readiness.                  |
| [preview-issues](.agents-config/skills/dev/preview-issues/SKILL.md)                   | On demand  | Render exact, non-mutating issue and comment Markdown with an approval digest.                         |
| [publish-issues](.agents-config/skills/dev/publish-issues/SKILL.md)                   | Explicit   | Publish only an exactly approved preview and verify idempotent GitHub persistence.                     |
| [implement-story](.agents-config/skills/dev/implement-story/SKILL.md)                 | Explicit   | Execute one approved story with bounded ownership, test-first evidence, and independent review.        |
| [parallel-implementation](.agents-config/skills/dev/parallel-implementation/SKILL.md) | On demand  | Plan disjoint ownership and integration; current policy keeps implementation serial without worktrees. |
| [handoff](.agents-config/skills/dev/handoff/SKILL.md)                                 | On demand  | Produce a provider-neutral checkpoint that becomes durable after GitHub publication and read-back.     |
| [adversarial-review](.agents-config/skills/dev/adversarial-review/SKILL.md)           | On demand  | Challenge high-risk plans or changes from clean, read-only context.                                    |
| [react-pattern-review](.agents-config/skills/dev/react-pattern-review/SKILL.md)       | On demand  | Review React/React Router patterns and require characterization before refactoring.                    |
| [evaluate-sdlc-pilot](.agents-config/skills/dev/evaluate-sdlc-pilot/SKILL.md)         | On demand  | Evaluate pilot evidence and recommend whether a formal evaluation framework is warranted.              |
| [repo-inventory](.agents-config/skills/dev/repo-inventory/SKILL.md)                   | On demand  | Inventory repository structure, boundaries, tooling, tests, CI, rules, and uncertainty.                |

| Knowledge skill                                                     | Invocation | Purpose                                                                          |
| ------------------------------------------------------------------- | ---------- | -------------------------------------------------------------------------------- |
| [wiki-init](.agents-config/skills/dev/wiki-init/SKILL.md)           | On demand  | Bootstrap an evidence-backed OKF wiki without inventing architecture.            |
| [wiki-update](.agents-config/skills/dev/wiki-update/SKILL.md)       | On demand  | Add, refresh, deprecate, or correct a small set of durable concepts.             |
| [wiki-audit](.agents-config/skills/dev/wiki-audit/SKILL.md)         | On demand  | Audit OKF structure, metadata, indexes, links, provenance, and planning leakage. |
| [wiki-visualize](.agents-config/skills/dev/wiki-visualize/SKILL.md) | On demand  | Generate and validate the offline wiki relationship viewer.                      |
| [record-adr](.agents-config/skills/dev/record-adr/SKILL.md)         | On demand  | Record an attributable, human-approved reusable architecture decision.           |

<!-- skills-catalog:end -->

After adding, moving, renaming, or reviewing a skill, explicitly run `$skills-audit --fix`, then run its read-only audit. After changing rule cards or invocation policy, explicitly run `$rules-audit`.

### Project knowledge

- [Local stack runbook](wiki/operations/local-stack.md) and [environment variables](wiki/operations/environment-variables.md).
- [Keycloak realm/client facts](wiki/integrations/keycloak/realm-and-client-facts.md), [email verification](wiki/operations/verify-email-flows.md), and [admin-user workflow](wiki/operations/create-admin-user.md).
- [Local backup](wiki/operations/local-backup.md), [restore drill](wiki/operations/backup-restore-drill.md), and [known production gaps](wiki/architecture/known-production-gaps.md).

Newly migrated wiki knowledge remains draft and unverified until a human checks it against the running realm and intended operating model. Agent-framework automation under skill-local `scripts/` is portable Python invoked through `uv`. Existing operational backup/restore runbooks remain POSIX shell scripts; JavaScript `.mjs` files are tool configuration only.
