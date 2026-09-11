---
name: plan-implementation
description: Create vertical stories and a dependency plan, critique it independently, and obtain one scoped delivery approval. Use after a stable feature specification.
---

# plan implementation

Record the package Git revision in checkpoints; identify uncommitted package changes as provisional.

1. Verify the specification and independent critique. Reuse the developer's requirements without repeating the interview.
2. Write `specs/implementation-plans/YYYY-MM-DD-feature-slug.md` using [the plan template](templates/implementation-plan.md).
3. Each story delivers an observable outcome across applicable layers: schema/model and migration, service/BFF, UI, browser tests. Explain inapplicable layers. This starter uses React Router BFF and SQL; Express is a placeholder and Drizzle is not installed. Do not add a layer simply to fill a template.
4. Map every requirement to stories; specify acceptance, failure paths, verification, rollback, dependencies and disjoint path ownership. Keep shared lockfiles, migrations and infrastructure with the integration owner. Avoid horizontal slices unless justified enabling work.
5. Run `corepack pnpm workflow check-plan <path>`. Delegate `critique-implementation-plan` to a separate read-only reviewer, resolve blocking findings and revalidate edited digests.
6. Present one concrete approval covering the exact spec/plan, repository, integration branch, base branch and implementation through commit/push/PR. Record an attributable user instruction already given when it covers these artifacts and actions. Never infer approval from a status field, silence, agent text or a tool capability.
7. Hand the approved packet to `implement-feature`. Changed material scope or destination requires resolution; already authorized routine actions do not need a second approval.

Use the repository workflow helper for v2 artifact checks and revision-bound execution records. Optional GitHub issue decomposition is useful for larger work, not a prerequisite for a one-story feature.
