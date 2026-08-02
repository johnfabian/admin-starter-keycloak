# Test strategy: `<feature/story>`

- Skill version: `<full Git commit containing this package>`

## Baseline and risks

- Current evidence: `<commands/results>`
- Characterization required: `<yes/no; behavior>`
- Highest risks: `<requirements/edge IDs>`

## Coverage matrix

| Behavior/risk | Level                                          | Fixture/services | Positive case | Negative/failure case | Command/evidence |
| ------------- | ---------------------------------------------- | ---------------- | ------------- | --------------------- | ---------------- |
| `<REQ/EDGE>`  | `<unit/browser/integration/e2e/config/manual>` | `<fixture>`      | `<case>`      | `<case>`              | `<command/path>` |

## CI and coverage ratchet

- Fast required gate: `<checks>`
- Conditional integration gate: `<paths and explicit N/A behavior>`
- Ratchet: `<risk-owned files/branches and no-regression rule>`

## Data, cleanup, and uncertainties

- `<production-data exclusion, cleanup, unresolved feasibility>`
