# Wiki update log

## 2026-09-11

- Added local automation runbooks, code-graph ownership, and proposed ADRs; renamed the live ADR directory from decisions to adr. Historical records retain their original paths. Browser evidence remains conditional on successful live execution.

## 2026-08-02

- **Shared agent configuration**: Moved canonical skills and rule cards into `.agents-config/`, organized skills by `meta`, `ops`, and `dev`, and exposed the shared source through flat Codex/Claude skill symlinks and provider rule-directory symlinks.
- **Automation portability**: Converted skill automation from Node `.mjs` to portable Python launched through `uv run`, removed the standalone implementation-plan generator, and kept planning capability unimplemented for a future skill/agent design. Scoped rules prohibit new PowerShell and Node automation while preserving existing POSIX backup/restore runbooks and required JavaScript tool configuration.
- **Documentation migration**: Classified all eight legacy documentation files, promoted only current durable knowledge into 28 draft/unverified concepts, updated the two affected integration concepts, and removed the legacy directory after link migration.
- **Knowledge boundaries**: Kept console baselines, runbooks, risks, and tradeoffs in the wiki; kept imperative enforcement in path-scoped rule cards; created no ADR from historical inference.
- **Initialization**: Created the OKF v0.2 directory structure, indexes, and draft/unverified baseline concepts from repository code and configuration.
- **Baseline**: Recorded the implemented repository boundaries, React Router BFF, BFF session schema, local edge/identity topology, Express placeholder, tooling, and verification gap.
