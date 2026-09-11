---
type: Convention
title: Dependency supply-chain hardening
description: Review convention for preserving and changing the repository's pnpm trust controls.
resource: /pnpm-workspace.yaml
tags: [pnpm, dependencies, supply-chain, security]
status: draft
generated: { by: codex/gpt-5, at: 2026-08-02T16:44:19Z }
stale_after: 2026-10-02
sources:
  - id: workspace-policy
    resource: /pnpm-workspace.yaml
    title: Canonical pnpm supply-chain settings
    last_modified: 2026-07-28
  - id: package-manager
    resource: /package.json
    title: Pinned package manager and scripts
    last_modified: 2026-08-01
---

# Current controls

The repository pins pnpm 11.1.2 and declares a seven-day minimum release age with strict/missing-time handling, blocks exotic transitive sources, requires explicit dependency-build decisions, rejects trusted-publishing downgrades, pins `qs` to 6.15.2, and denies the `esbuild` lifecycle script.[^workspace-policy][^package-manager]

# Change convention

Treat any manifest, lockfile, override, trust-policy, release-age, or build-script change as a supply-chain review. Prefer a narrow version pin or explicit per-package decision over a broad relaxation. Inspect lifecycle scripts and publishing provenance before allowing them. Keep the lockfile committed and use frozen installs in build environments.

Document why an exception is needed, who approved the trust change, its intended expiry/review point, and the verification performed. Never store registry credentials in repository files or handoffs.

# Related concepts

- [Dependency install failures](/operations/dependency-install-failures.md)
- [Repository tooling](/conventions/repository-tooling.md)

[^workspace-policy]: Canonical pnpm supply-chain settings

[^package-manager]: Pinned package manager and scripts

# Related decision records

These proposals record the decision and tradeoffs; this page retains the current behavior or operational procedure.

- [ADR-0010: Gate dependency adoption with explicit trust controls (proposed)](/adr/ADR-0010-dependency-trust-controls.md)
