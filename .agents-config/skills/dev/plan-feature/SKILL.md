---
name: plan-feature
description: Thinly orchestrate repository-native feature planning by validating persisted stage artifacts, digests, approvals, and the next independently invokable skill. Use to start or resume planning from a GitHub feature record and optional disposable state; never use it to perform specialist analysis, publish issues, implement code, or infer human approval.
disable-model-invocation: true
---

# Orchestrate planning stages

Use the full Git commit containing this package as the skill version ID and record it in state/checkpoints. A dirty package is unversioned and cannot satisfy a completed gate.

1. Start from the GitHub feature record and optional disposable state. Treat conversation history as non-authoritative and local-only artifacts as provisional.
2. Read [references/stage-contract.md](references/stage-contract.md) for stage order and required evidence.
3. Run `uv run scripts/validate_state.py <state.json>` from this skill directory.
4. Verify the declared source revision, artifact links/digests, gate owner, and current GitHub state before resuming.
5. Direct the user to the one named specialist skill for the next incomplete stage. Do not reproduce or perform that skill's instructions.
6. Stop at material decisions, feature approval, publication approval, architecture/security gates, and unresolved critical findings.
7. Update only disposable state or render a GitHub checkpoint preview; do not publish, implement, delete working artifacts, or mark a stage complete from agent prose.
8. After publication, require a re-read GitHub URL plus source-artifact digest, published-body digest, and verification time for every approved planning artifact. Require the same evidence for at least one handoff. Planning is not durably complete while persistence is pending.
9. Use a handoff before a gate, provider/session switch, compaction, ownership change, or stop. Treat a local handoff as provisional until its exact approved body is posted and verified in GitHub.

Use [references/scenarios.md](references/scenarios.md) for orchestration regression checks.
