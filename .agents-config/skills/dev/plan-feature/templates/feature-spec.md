# Feature: short name

Date: YYYY-MM-DD
Status: Draft / critiqued
Evidence: relevant source revisions, rules and wiki concept IDs

Describe the problem, actor journeys, scope, denied/failure behavior, constraints, non-goals and unresolved questions. Replace this sample contract; the fenced JSON is validated, and the full file digest binds subsequent planning. Do not store secrets.

```feature-spec
{
  "version": 2,
  "id": "FEAT-EXAMPLE",
  "title": "Example feature",
  "scope": [
    "One observable outcome"
  ],
  "nonGoals": [
    "Unrelated application behavior"
  ],
  "requirements": [
    {
      "id": "REQ-001",
      "actor": "Signed-in user",
      "outcome": "Describe the successful outcome",
      "denied": "Describe authorization denial",
      "failure": "Describe dependency failure",
      "acceptance": [
        "A deterministic assertion of the outcome"
      ]
    }
  ],
  "decisions": [
    {
      "question": "Which service boundary?",
      "status": "resolved",
      "disposition": "Use the implemented BFF"
    }
  ]
}
```

## Critique

Record actual author/reviewer identities, exact reviewed digest, findings and dispositions. Material edits require a new critique. Approval comes with the implementation plan.
