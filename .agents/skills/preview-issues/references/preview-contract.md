# Preview input contract

Provide UTF-8 JSON with this shape:

```json
{
  "repository": "owner/name",
  "sourceRevision": "full commit SHA",
  "skillVersion": "full commit SHA:.agents/skills/preview-issues",
  "parent": {
    "key": "STABILITY",
    "title": "Establish the existing-application stability baseline",
    "type": "Feature",
    "body": "Exact Markdown issue body",
    "labels": ["sdlc"]
  },
  "children": [
    {
      "key": "STABILITY-001",
      "title": "Characterize the web authorization boundary",
      "type": "Story",
      "body": "Exact Markdown issue body",
      "labels": ["testing"],
      "dependsOn": []
    }
  ]
}
```

Keys are stable idempotency identifiers. Bodies must already contain approved scope, criteria, evidence, and gates; the renderer does not reinterpret them.
