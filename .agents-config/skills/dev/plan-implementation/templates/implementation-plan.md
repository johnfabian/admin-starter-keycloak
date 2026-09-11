# Implementation plan: short name

Date: YYYY-MM-DD
Status: Draft / critiqued / approved
Feature: repository-relative specification path

Explain observable stories, dependencies, affected boundaries, ownership, tests, risks and rollback. Explain inapplicable layers; keep shared migrations and dependency files with the integration owner. The JSON is the execution contract. Compute specificationDigest after formatting the final specification, then format and critique this plan.

```implementation-plan
{
  "version": 2,
  "id": "FEAT-EXAMPLE",
  "title": "Example delivery",
  "specification": "specs/features/YYYY-MM-DD-example.md",
  "specificationDigest": "sha256:replace-with-exact-file-hash",
  "integrationPaths": [
    "package.json",
    "pnpm-lock.yaml",
    "postgres/init"
  ],
  "stories": [
    {
      "id": "STORY-001",
      "title": "Deliver the outcome",
      "outcome": "Observable user result",
      "kind": "vertical",
      "requirements": [
        "REQ-001"
      ],
      "dependsOn": [],
      "ownedPaths": [
        "web/app/routes/example.tsx"
      ],
      "layers": {
        "data": "Not applicable: no persistence change",
        "service": "Validate and authorize in the BFF",
        "ui": "Expose the outcome and denial state"
      },
      "acceptance": [
        "The specified actor can complete the outcome"
      ],
      "tests": [
        "Browser success, denial and failure assertions"
      ],
      "verification": [
        "verify:story"
      ],
      "rollback": "Revert the story commit"
    }
  ]
}
```

## Approval and delivery target

Record the real human instruction, source and date; exact specification and plan digests; repository, integration branch and PR base; implementation, commit, push and PR submission scope. PR merge/deploy remain separate. One human approval covers the three-flow delivery scope; do not invent a new gate for every specialist action.
