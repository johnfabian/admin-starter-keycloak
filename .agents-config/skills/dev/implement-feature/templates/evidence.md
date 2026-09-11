# Evidence records

Write separate ignored JSON files under `.agent-work/<feature>/`. These examples describe the contract; substitute real source evidence and identities. The helper does not authenticate an actor or execute a reviewer.

## Planning review

```json
{
  "kind": "spec",
  "specDigest": "sha256:exact-full-file",
  "planDigest": "sha256:exact-full-file",
  "author": "actual-author",
  "reviewer": "actual-independent-reviewer",
  "findings": []
}
```

Use kind `plan` for the implementation critique. Findings require `severity` (critical/high/medium/low), `evidence` and `disposition` (open/fixed/accepted). Include impact, remediation and owner for useful handoffs. Critical/high must be fixed to pass; the agent cannot accept those risks automatically.

## Human delivery approval

```json
{
  "specDigest": "sha256:exact-full-file",
  "planDigest": "sha256:exact-full-file",
  "actor": "human:actual-user",
  "statement": "Verbatim authorized instruction",
  "sourceKind": "conversation",
  "source": "Actual conversation reference or GitHub URL",
  "approvedAt": "2026-09-11T12:00:00Z",
  "target": { "repository": "owner/repository", "branch": "feature/integration", "base": "master" },
  "actions": ["implement", "commit", "push", "pull-request"]
}
```

Use the actual time/source, not this sample. Do not infer a GitHub approval that was never posted.

## Implementation review

```json
{
  "kind": "implementation",
  "subject": "STORY-001",
  "revision": "exact-40-character-commit",
  "round": 1,
  "reviewer": "actual-independent-agent",
  "findings": []
}
```

Use subject `feature` for final integration review. The final reviewer must differ from every worker and the coordinator. Report reviewed paths, tests inspected, attack/failure cases and limitations alongside findings. Do not substitute a writer's self-review.

## Handoff

Record feature and plan paths/digests, package revision, integration and worker branches/HEADs, current generation, review round/history, global claims, actual approval source, checks and exact evidence, rules/wiki IDs, known limitations and one next action. Publish sanitized content in the authorized PR and record exact body digest/read-back time. Keep raw logs and credentials out of Git and Graphify.
