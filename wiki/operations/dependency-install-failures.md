---
type: Runbook
title: Dependency install failures
description: Triage for pnpm age, lifecycle-script, provenance, and source-policy failures.
tags: [pnpm, dependencies, supply-chain, troubleshooting]
status: draft
generated: { by: codex/gpt-5, at: 2026-08-02T16:44:19Z }
stale_after: 2026-10-02
sources:
  - id: workspace-policy
    resource: /pnpm-workspace.yaml
    title: pnpm supply-chain controls
    last_modified: 2026-07-28
  - id: lockfile
    resource: /pnpm-lock.yaml
    title: Resolved dependency graph
    last_modified: 2026-08-01
---

# Triage

Identify the control that failed before changing policy:

- A version younger than seven days is blocked by `minimumReleaseAge` and strict age handling. Prefer waiting or a reviewed older version over an exclusion.
- A dependency lifecycle script is blocked by `strictDepBuilds`. Run `corepack pnpm ignored-builds`, inspect the exact package and script, and prefer an explicit deny when the package works without it.
- A trusted-publishing downgrade is blocked by `trustPolicy: no-downgrade`. Investigate the provenance change; do not normalize it as routine churn.
- A transitive non-registry source is blocked by `blockExoticSubdeps`. Confirm why the dependency graph left the registry.

The workspace also pins `qs` through an override and denies the `esbuild` install script.[^workspace-policy]

# Resolution evidence

Any exception or dependency change needs a focused `pnpm-lock.yaml` review, the reason for trust, the smallest scoped policy edit, and successful static/build checks.[^lockfile] Never paste registry tokens or credentials into configuration, logs, issues, or handoffs.

# Related concepts

- [Dependency supply-chain hardening](/conventions/dependency-supply-chain-hardening.md)
- [Repository tooling](/conventions/repository-tooling.md)

[^workspace-policy]: pnpm supply-chain controls

[^lockfile]: Resolved dependency graph

# Related decision records

These proposals record the decision and tradeoffs; this page retains the current behavior or operational procedure.

- [ADR-0010: Gate dependency adoption with explicit trust controls (proposed)](/adr/ADR-0010-dependency-trust-controls.md)
