---
name: requirements-interview
description: Convert approved intent and research into stable, testable requirements, non-goals, decisions, and acceptance criteria. Use when product intent is ambiguous or before architecture and story decomposition; ask humans only questions that materially change scope, authorization, ownership, compatibility, operations, cost, or risk.
---

# Resolve requirements

Use the full Git commit containing this package as the skill version ID and record it in every artifact. A dirty package is unversioned and cannot satisfy a completed gate.

1. Accept the request, research artifact, existing decisions, and known constraints as declared inputs.
2. Assign stable requirement IDs. For each, name the actor, observable behavior, authorization behavior, failure behavior, and acceptance evidence.
3. State scope and non-goals explicitly. Preserve unresolved conflicts rather than choosing silently.
4. Ask one bounded human question at a time only when its answer materially changes delivery.
5. Record decisions with owner, options, selected outcome, rationale, and approval status. Agent inference is never approval.
6. Reject criteria that only describe implementation tasks or subjective quality.
7. Render [templates/requirements.md](templates/requirements.md) for a GitHub feature record. Do not publish it.

Exercise [references/scenarios.md](references/scenarios.md) when revising the workflow.
