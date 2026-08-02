# Wiki audit contract

The bundled script is read-only, runs through `uv`, and uses only Python standard-library modules.

## Exit codes

- `0`: no hard conformance errors; warnings may remain.
- `1`: one or more hard conformance errors.
- `2`: invocation or target-directory error.

## Hard errors

- Missing root `index.md` or `log.md`.
- Invalid root version declaration or frontmatter on a nested index/log.
- Missing or malformed concept frontmatter.
- Empty `type`, invalid lifecycle value, malformed actor/timestamp/date, or malformed source entry.
- A non-ISO or non-newest-first log date heading.

## Warnings

- Missing recommended discovery, provenance, generated, or freshness fields.
- Missing index entries, broken internal concept links, stale concepts, or unverified stable concepts.
- Headings that suggest active feature plans or handoffs were copied into durable knowledge.

The parser accepts the repository profile's block mappings/lists and simple flow arrays/maps. YAML features outside that profile should be checked with an independently approved full YAML parser before claiming full syntax coverage.
