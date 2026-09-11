# OKF v0.2 repository profile

Use this self-contained profile when initializing a wiki.

## Bundle rules

- Treat the target directory as one bundle.
- Reserve `index.md` for navigation and `log.md` for history; neither is a concept.
- Give only the root `index.md` frontmatter, containing `okf_version: "0.2"`.
- Give every other non-reserved Markdown file parseable YAML frontmatter with a non-empty `type`.
- Give nested indexes no frontmatter.
- List immediate concepts and subdirectories in each index.
- Group log entries beneath ISO `YYYY-MM-DD` headings, newest first.

## Concept profile

Use these fields for agent-created or materially edited concepts:

```yaml
---
type: Architecture
title: Short display title
description: One-sentence summary.
tags: [tag-one, tag-two]
status: draft
generated: { by: codex/gpt-5, at: 2026-08-02T00:00:00Z }
stale_after: 2027-02-02
sources:
  - id: source-key
    resource: /repository/path
    title: Source title
    last_modified: 2026-08-01
---
```

- Use `draft`, `stable`, or `deprecated` for `status`. Keep new inferred knowledge draft.
- Use `<producer>/<version>`, `human:<id>`, or `process:<id>` for actors.
- Use `verified` only for an actual verification event. Its absence means unverified.
- Require every `sources` entry to contain `resource`; add stable `id` values when claims cite sources.
- Use `stale_after` as an absolute date when freshness matters.
- Use standard Markdown links for relationships. A leading `/` in a concept link is relative to the bundle root.

## Local concept types

Use only a type that describes the content. The initial repository taxonomy may include `Architecture`, `Domain Model`, `Decision`, `Policy`, `Schema`, `Convention`, `Runbook`, `Integration`, `Test Strategy`, and `Reference`. Consumers must tolerate future types.

## Content boundary

Include reusable engineering knowledge. Exclude active feature scope, acceptance criteria, delivery status, approval requests, handoffs, and raw session transcripts. GitHub remains the durable record for active decisions and delivery; accepted reusable architectural decisions later become `Decision` concepts in `adr/`.
