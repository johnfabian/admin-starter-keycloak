# Planning stage contract

Stages advance in this order:

1. `research` -> `$feature-research`
2. `requirements` -> `$requirements-interview`
3. `architectureImpact` -> `$architecture-impact`
4. `edgeCases` -> `$find-edge-cases`
5. `testStrategy` -> `$test-strategy`
6. `stories` -> `$decompose-stories`
7. `critique` -> `$critique-plan`
8. `featureApproval` -> authorized human approval record
9. `preview` -> `$preview-issues`
10. `publicationApproval` -> authorized human approval of exact preview digest
11. `publication` -> `$publish-issues`

Every completed stage requires an artifact URL/path, `sha256:` artifact digest, full source revision, and gate status. Human approval stages additionally require the actor, record URL, timestamp, and digest of the exact artifact approved. The publication-approval digest must equal the completed preview-stage digest. Critical critique findings block feature approval. Publication requires both approval stages, the exact preview digest, and explicit mutation authority.

Allowed stage status values are `pending`, `in_progress`, `complete`, and `blocked`. Gate status is `pending`, `passed`, `blocked`, or `not-triggered`. State is disposable and cannot replace the GitHub record.
