# Scenario cases

1. Current policy: two disjoint writers require separate linked worktrees and feature branches; overlapping ownership produces a serial plan.
2. Path conflict: shared lockfile, schema, CI, or infrastructure changes force single ownership.
3. Safe exception: require explicit human policy evidence before any isolated parallel checkout is created.
4. Scope creep: a worker must stop before editing paths outside its approved budget.
