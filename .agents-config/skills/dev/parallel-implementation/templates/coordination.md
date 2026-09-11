# Implementation coordination

- Skill version: `<full Git commit containing this package>`
- Parent/story links: `<links>`
- Base revision: `<full SHA>`
- Repository isolation policy: `<linked worktrees; at most two disjoint writers>`
- Integration owner: `<human/agent role>`
- Mode/gate: `<serial/parallel/blocked>`

| Worker     | Branch/checkout | Outcome            | Owned paths | Excluded/shared paths | Evidence           | Merge order |
| ---------- | --------------- | ------------------ | ----------- | --------------------- | ------------------ | ----------- |
| `<worker>` | `<identity>`    | `<bounded result>` | `<paths>`   | `<paths>`             | `<checks/handoff>` | `<order>`   |

- Contract/change escalation: `<owner and process>`
- Combined-revision verification: `<commands and owner>`
