# Wiki update log

## 2026-08-02

- **Automation portability**: Converted skill automation from Node `.mjs` to portable Python launched through `uv run`, removed the standalone implementation-plan generator, and kept planning capability unimplemented for a future skill/agent design. Scoped rules prohibit new PowerShell and Node automation while preserving existing POSIX backup/restore runbooks and required JavaScript tool configuration.
- **Documentation migration**: Classified all eight legacy documentation files, promoted only current durable knowledge into 28 draft/unverified concepts, updated the two affected integration concepts, and removed the legacy directory after link migration.
- **Knowledge boundaries**: Kept console baselines, runbooks, risks, and tradeoffs in the wiki; kept imperative enforcement in path-scoped rule cards; created no ADR from historical inference.
- **Initialization**: Created the OKF v0.2 directory structure, indexes, and draft/unverified baseline concepts from repository code and configuration.
- **Baseline**: Recorded the implemented repository boundaries, React Router BFF, BFF session schema, local edge/identity topology, Express placeholder, tooling, and verification gap.
