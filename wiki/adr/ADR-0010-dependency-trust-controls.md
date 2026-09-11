---
type: Decision
title: "ADR-0010: Gate dependency adoption with explicit trust controls"
description: Proposed decision record extracted from current wiki and source evidence.
tags: [adr, architecture]
adr_id: ADR-0010
decision_status: proposed
status: draft
generated: { by: "codex/gpt-6", at: "2026-09-11T20:32:36Z" }
stale_after: 2026-12-11
sources:
  - id: source-1
    resource: /pnpm-workspace.yaml
    title: "pnpm-workspace.yaml"
    last_modified: 2026-08-02
  - id: source-2
    resource: /package.json
    title: "package.json"
    last_modified: 2026-09-11
  - id: source-3
    resource: /.agents-config/rules/security.md
    title: ".agents-config/rules/security.md"
    last_modified: 2026-09-11
---

# Context

Dependency installation can introduce newly published code, lifecycle execution and provenance changes.

# Decision proposal

Record the workspace's declared release-age, source, build-script and publishing-trust controls. Keep lockfiles and use frozen installs. Review any relaxation as an explicit, narrow exception with evidence rather than bypassing a failed installation generically.

# Alternatives for review

Unrestricted installs, broad allowlists, or separate external policy enforcement are comparison options. The original acceptance of the exact policy values is not established.

# Consequences and limits

New versions and dependencies may be blocked until eligible or explicitly reviewed. Exact versions, the seven-day window, overrides and per-package build decisions remain configuration details in the convention and workspace file; changing those values should not silently broaden trust.

# Approval provenance

This is a proposed record of architecture observed in the cited source. The original approver, decision date and historical rationale were not established. Do not treat implemented behavior as approval or infer that the alternatives below were historically considered.
Acceptance requires an attributable record of the exact outcome and approver. This audit creates no accepted ADR and makes no application, realm, network, or tooling-policy change.

# Evidence and related guidance

Source revision inspected: 342ec668b7848fe0200a9c317812831ca546b885. Draft documents are evidence of design intent, not implemented behavior.

- [conventions/dependency-supply-chain-hardening.md](/conventions/dependency-supply-chain-hardening.md)
- [operations/dependency-install-failures.md](/operations/dependency-install-failures.md)

# Supersession

No prior ADR is superseded. Existing records keep their identifiers.
