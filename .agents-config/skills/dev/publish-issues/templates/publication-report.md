# SDLC publication report

- Skill version: `<full Git commit containing this package>`
- Repository: `<owner/name>`
- Source revision: `<full SHA>`
- Approved preview digest: `sha256:<digest>`
- Approval record: `<human, role, immutable URL/comment>`

| Stable key | Result                       | Issue URL | Type/metadata                  | Relationships           |
| ---------- | ---------------------------- | --------- | ------------------------------ | ----------------------- |
| `<key>`    | `<created/existing/blocked>` | `<URL>`   | `<type/labels/project fields>` | `<parent/dependencies>` |

| Comment key | Target issue  | Stage     | Result                       | Comment URL | Source artifact digest | Published body digest | Read-back verified at |
| ----------- | ------------- | --------- | ---------------------------- | ----------- | ---------------------- | --------------------- | --------------------- |
| `<key>`     | `<issue key>` | `<stage>` | `<created/existing/blocked>` | `<URL>`     | `sha256:<digest>`      | `sha256:<digest>`     | `<ISO 8601>`          |

- Idempotency re-check: `<pass/fail>`
- Publication report marker: `<!-- sdlc-publication-report: <approved-preview-digest> -->`
- Partial failures/recovery action: `<none or one exact action>`
