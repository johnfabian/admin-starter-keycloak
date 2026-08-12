# Preview input contract

Provide UTF-8 JSON with this shape:

```json
{
  "repository": "owner/name",
  "sourceRevision": "full commit SHA",
  "skillVersion": "full commit SHA:.agents-config/skills/dev/preview-issues",
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
  ],
  "comments": [
    {
      "key": "STABILITY:research",
      "target": "STABILITY",
      "stage": "research",
      "artifactDigest": "sha256:<digest of the approved source artifact>",
      "body": "Exact approved Markdown comment body"
    }
  ]
}
```

Issue keys and comment keys are stable idempotency identifiers. A comment target must name the parent or one child issue key. `artifactDigest` binds the comment to the approved source artifact. Keep comments in the publication order required by the workflow; the renderer preserves that order and includes both the source-artifact digest and the SHA-256 digest of each complete marker-plus-body value that GitHub will store.

Bodies must already contain approved scope, criteria, evidence, and gates. Do not include `sdlc-key` or `sdlc-comment-key` markers in input bodies; the renderer adds them. The renderer validates and displays content but never reinterprets it.
