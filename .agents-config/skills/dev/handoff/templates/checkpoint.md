## AI SDLC checkpoint

- Handoff skill version: `<full Git commit containing this package>`

### Persistence

- Checkpoint status: `<provisional/durable>`
- Stable feature/checkpoint or optional comment key: `<feature-or-story-key:handoff-stage>`
- Approved specification/plan digests: `<sha256:digests>`
- Source-artifact digest: `sha256:<digest>`
- Exact published-payload digest (separate from approval scope): `<sha256:digest or pending>`
- Persisted location: `<PR body / optional issue comment / provisional local copy>`
- GitHub record: `<PR URL or immutable comment URL, or pending>`
- Verified PR head/base: `<exact revision/base, or not applicable>`
- Read-back verified at: `<ISO 8601 UTC timestamp or pending>`
- Local retention: `never delete automatically; cleanup requires explicit human direction`

### Objective and scope

- Objective: `<observable outcome>`
- In scope: `<bounded scope>`
- Out of scope: `<explicit exclusions>`
- Feature/story: `<IDs; optional GitHub issue links>`
- Delivery authority: `<attributable flow-2 approval; repository, branch, base, actions>`

### Revision and ownership

- Base revision: `<full commit SHA>`
- Current revision: `<full commit SHA>`
- Branch: `<branch>`
- Worktree: `<absolute path or stable worktree identifier>`
- Isolation policy: `<linked worktree and feature branch; max two writers including editing coordinator>`
- Active claims/reconciliation: `<worker identity, branch, paths, generation, actual stop status>`
- Owned paths: `<paths>`
- Excluded/shared paths: `<paths>`

### Completed work

- `<artifact or outcome with path/link>`

### Context applied

- Rules: `<rule IDs, or none>`
- Wiki concepts: `<bundle-relative concept IDs, or none>`
- Minimum retrieval references: `<paths/links required to resume>`

### Verification evidence

| Check/category            | Result                | Timestamp    | Revision | Evidence                    |
| ------------------------- | --------------------- | ------------ | -------- | --------------------------- |
| `<exact command or gate>` | `<pass/fail/not-run>` | `<ISO 8601>` | `<SHA>`  | `<path/URL/reason not run>` |

### Decisions and gates

- Decisions/assumptions: `<durable record links or explicit unknown>`
- Approved artifact digests: `<digest + attributable approval record, or none>`
- Independent reviewer: `<identity/context and artifact revision, or not-triggered>`
- Shared review budget: `<current round of five; failed history and evidence; never reset on resume>`
- Material unresolved decisions: `<owner/status/evidence, or none>`
- Merge/deployment authority: `<outside routine feature-delivery scope; separate explicit authority if supplied>`

### Risks and blockers

- `<risk, impact, owner/disposition>`

### Exact next action

`<one imperative, bounded, verifiable action>`
