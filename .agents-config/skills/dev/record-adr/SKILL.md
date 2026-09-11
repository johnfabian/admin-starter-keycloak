---
name: record-adr
description: Convert an attributable, human-approved, reusable architectural decision into an immutable OKF decision concept and update its index/log links. Use only after the GitHub issue or pull request records the exact accepted outcome, approver, and decision date; stop when approval or ownership is ambiguous.
---

# Record an approved ADR

Use the full Git commit containing this package as the skill version ID and record it with the originating GitHub evidence. A dirty package is unversioned and cannot satisfy a completed gate.

1. Verify the approval record, approver authority, exact artifact revision, decision outcome, and decision date.
2. Confirm the choice is reusable and long-lived; leave feature-local decisions in GitHub.
3. Allocate the next unused `ADR-####` identifier by inspecting the decision register. Never reuse an ID.
4. Create the smallest decision concept using [templates/adr.md](templates/adr.md) at `wiki/adr/ADR-####-<kebab-case-slug>.md`; the filename and `adr_id` must use the same immutable identifier.
5. Preserve earlier ADRs. Supersede with explicit bidirectional links instead of rewriting or deleting history.
6. Update the ADR index and root log, run the wiki audit, and prepare the repository path/commit cross-link for GitHub.
7. Do not mark an ADR accepted or stable from agent inference.

Use [references/scenarios.md](references/scenarios.md) for lifecycle checks.
