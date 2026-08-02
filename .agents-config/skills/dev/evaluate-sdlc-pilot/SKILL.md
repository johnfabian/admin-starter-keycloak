---
name: evaluate-sdlc-pilot
description: Review versioned skill-local scenarios, pilot failures, cycle evidence, security regressions, false positives, and clean-session results to recommend whether a formal evaluation framework is warranted. Use at the Phase 5 gate; never create a central evals directory without an attributable human approval of the exact proposal.
---

# Evaluate the SDLC pilot

Use the full Git commit containing this package as the skill version ID and record it in every artifact. A dirty package is unversioned and cannot satisfy a completed gate.

1. Collect skill version, source revision, provider/model, environment, duration, outcome, false positives, failures, and evidence links for reviewed pilot runs.
2. Include prompt-injection, approval-bypass, malformed-input, provider-transfer, ownership-conflict, and security regression cases.
3. Separate deterministic results from reviewer judgment and missing evidence.
4. Compare recurring failures, severity, rework, and reproducibility with the cost and maintenance burden of formal evaluation infrastructure.
5. Render [templates/evaluation-decision.md](templates/evaluation-decision.md) with options and a recommendation.
6. Require a human owner to approve either a formal evaluation design or a time-bounded continuation of lightweight skill-local evidence.
7. Do not create `evals/` or claim Phase 5 complete before that decision is recorded.

Use [references/scenarios.md](references/scenarios.md) to check the decision gate.
