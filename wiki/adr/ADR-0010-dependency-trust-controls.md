---
type: Decision
title: "ADR-0010: Gate dependency adoption with explicit trust controls"
description: Accepted architectural decision with attributable conversation approval recorded in PR 20.
tags: [adr, architecture]
adr_id: ADR-0010
decision_status: accepted
decided_on: 2026-09-11
approved_by: "human:requesting-user"
status: stable
generated: { by: "codex/gpt-6", at: "2026-09-11T20:32:36Z" }
stale_after: 2026-12-11
verified: { by: human:requesting-user, at: "2026-09-11T21:27:10.569994+00:00" }
sources:
  - id: acceptance
    resource: https://github.com/johnfabian/admin-starter-keycloak/pull/20#adr-acceptance---2026-09-11
    title: Conversation approval of the exact ADR set recorded in PR 20
    author: "human:requesting-user"
    last_modified: 2026-09-11
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

# Decision

Record the workspace's declared release-age, source, build-script and publishing-trust controls. Keep lockfiles and use frozen installs. Review any relaxation as an explicit, narrow exception with evidence rather than bypassing a failed installation generically.

# Alternatives for review

Unrestricted installs, broad allowlists, or separate external policy enforcement are comparison options. The original acceptance of the exact policy values is not established.

# Consequences and limits

New versions and dependencies may be blocked until eligible or explicitly reviewed. Exact versions, the seven-day window, overrides and per-package build decisions remain configuration details in the convention and workspace file; changing those values should not silently broaden trust.

# Approval provenance

Accepted on 2026-09-11 by the requesting human user in the Codex conversation (human:requesting-user). The user said: "lets not worrry about orca right now, but the ADRs look good to me".

The approval covers ADR-0001 through ADR-0012 as presented at commit 04e3abe09195516104180fb4f10ba23394cd1f04. It was transcribed into [PR #20](https://github.com/johnfabian/admin-starter-keycloak/pull/20#adr-acceptance---2026-09-11) and exactly reread before acceptance. This is conversation approval recorded by the assistant, not a GitHub review submitted by the human. No GitHub identity is inferred.

Acceptance confirms the architectural choice; it does not claim historical approval, independent runtime verification, production readiness, deployment or PR merge authorization. ORCA is deferred and does not block the accepted workflow.

The previous proposed record remains available at the approved Git revision. Record-ADR skill version: 04e3abe09195516104180fb4f10ba23394cd1f04.

# Evidence and related guidance

Source revision inspected: 342ec668b7848fe0200a9c317812831ca546b885. Draft documents are evidence of design intent, not implemented behavior.

- [conventions/dependency-supply-chain-hardening.md](/conventions/dependency-supply-chain-hardening.md)
- [operations/dependency-install-failures.md](/operations/dependency-install-failures.md)

# Supersession

No prior ADR is superseded. Existing records keep their identifiers.
