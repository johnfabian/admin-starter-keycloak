---
name: wiki-visualize
description: Deterministically generate and validate a self-contained, accessible offline HTML relationship viewer and manifest from an OKF v0.2 wiki bundle. Use after wiki relationship changes or when producing the committed/static knowledge graph; never hand-edit generated output.
---

# Generate the wiki viewer

Use the full Git commit containing this package as the skill version ID and record it in the manifest. A dirty package is unversioned and cannot satisfy a completed gate.

1. Audit the wiki before generation; stop on conformance or broken-link errors.
2. Confirm all wiki concepts/indexes are committed at the declared source revision; the generator must refuse dirty concept input. Then run `uv run scripts/generate_wiki_viz.py <repository-root>` from this skill directory.
3. Derive nodes from concept Markdown and directed edges from bundle-relative Markdown links. Keep hierarchy distinct from references.
4. Embed approved concept metadata and text only; include no credentials, ignored files, external fetches, or runtime backend.
5. Require search, type/status/trust/stale filters, a detail view with sources/provenance/backlinks, a taxonomy hierarchy separate from cross-links, and an accessible tabular fallback.
6. Verify the manifest source revision, generator version, counts, and deterministic content digest.
7. Regenerate after source changes; never hand-edit `wiki/viz.html` or `wiki/viz-manifest.json`.

Use [references/scenarios.md](references/scenarios.md) when changing the generator.
