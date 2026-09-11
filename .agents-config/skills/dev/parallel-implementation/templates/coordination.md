# Implementation coordination

- Skill version: `<full Git commit containing this package>`
- Specification/plan and approval: `<paths, exact digests, attributable record, approved destination/actions>`
- Story IDs/optional issue links: `<IDs/links>`
- Base revision: `<full SHA>`
- Repository isolation policy: `<linked worktrees; at most two disjoint writers including an editing integration owner>`
- Integration owner: `<actual human/agent identity and editing status>`
- Native harness capabilities: `<actual delegation, independent review, serial/parallel support>`
- Active claims: `<shared state, generations, worker/branch/path reservations>`
- Feature review budget: `<current round of five; shared failed-review history>`
- Mode/gate: `<serial/parallel/blocked>`

| Worker     | Branch/checkout | Outcome            | Owned paths | Excluded/shared paths | Evidence           | Merge order |
| ---------- | --------------- | ------------------ | ----------- | --------------------- | ------------------ | ----------- |
| `<worker>` | `<identity>`    | `<bounded result>` | `<paths>`   | `<paths>`             | `<checks/handoff>` | `<order>`   |

- Contract/change escalation: `<owner and process>`
- Combined-revision verification: `<commands and owner>`

- Interrupted-worker reconciliation: `<actual stop status, preserved work, claim disposition>`
