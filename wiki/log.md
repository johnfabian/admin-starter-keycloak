# Wiki update log

## 2026-09-11

- Recorded the requesting user's acceptance of ADR-0001 through ADR-0012 at reviewed revision 04e3abe09195516104180fb4f10ba23394cd1f04, with conversation approval transcribed and reread in PR #20. Updated lifecycle metadata and current guide backlinks; preserved proposal history and original IDs. ORCA work is deferred and does not block feature development. This is architectural approval, not a runtime/production or merge approval.

- Implemented the three-flow skills and portable contract/coordination helper, project-scoped adapter audits and dated specs layout. Updated workflow/tooling runbooks and ADR-0004/0009 implementation applicability. Removed 15 legacy plans with content preserved in Git; historical log entries remain unchanged. All ADR proposals retain their lifecycle, and ORCA-specific delegation remains unverified.

- Reconciled decision-bearing wiki guidance into ADR-0004 through ADR-0012 proposals, retaining source guides with backlinks. Clarified ADR-0002 ownership and the code-only Graphify/wiki split. All ADRs remain proposed; no historical acceptance, live verification, or production approval was inferred.

- Added the user-selected three-flow development convention: specification with critique, implementation planning with critique and one routine approval, and implementation with tests/review through PR submission. Documented current automation limits and linked the convention from the root and conventions indexes; no ADR acceptance inferred.

- Added local automation runbooks, code-graph ownership, and proposed ADRs; renamed the live ADR directory from decisions to adr. Historical records retain their original paths. Browser evidence remains conditional on successful live execution.

## 2026-08-02

- **Shared agent configuration**: Moved canonical skills and rule cards into `.agents-config/`, organized skills by `meta`, `ops`, and `dev`, and exposed the shared source through flat Codex/Claude skill symlinks and provider rule-directory symlinks.
- **Automation portability**: Converted skill automation from Node `.mjs` to portable Python launched through `uv run`, removed the standalone implementation-plan generator, and kept planning capability unimplemented for a future skill/agent design. Scoped rules prohibit new PowerShell and Node automation while preserving existing POSIX backup/restore runbooks and required JavaScript tool configuration.
- **Documentation migration**: Classified all eight legacy documentation files, promoted only current durable knowledge into 28 draft/unverified concepts, updated the two affected integration concepts, and removed the legacy directory after link migration.
- **Knowledge boundaries**: Kept console baselines, runbooks, risks, and tradeoffs in the wiki; kept imperative enforcement in path-scoped rule cards; created no ADR from historical inference.
- **Initialization**: Created the OKF v0.2 directory structure, indexes, and draft/unverified baseline concepts from repository code and configuration.
- **Baseline**: Recorded the implemented repository boundaries, React Router BFF, BFF session schema, local edge/identity topology, Express placeholder, tooling, and verification gap.
