> Historical v1.x contract: retained for read-only recovery. Its stage names and publication rules do not authorize the current v2 workflow. Use plan-feature and the repository workflow helper for new features.

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

State schema `1.1.0` adds a persistence gate after publication. Record each approved planning artifact with its stable comment key, source-artifact digest, published-body digest, immutable GitHub URL, and read-back verification time. Preserve any additional approved feature-specific artifact, such as a manual runtime baseline, in the same map. Record verified handoffs separately because more than one may exist. Required planning artifacts are research, requirements, architecture impact, edge cases, test strategy, stories, and critique.

Schema `1.0.0` remains readable only as pre-publication legacy state and reports that migration is required. It cannot represent durable completion. A local path or `.agent-work` file is provisional evidence; never delete it automatically. Even after persistence is verified, cleanup requires explicit human direction.

Allowed stage status values are `pending`, `in_progress`, `complete`, and `blocked`. Gate status is `pending`, `passed`, `blocked`, or `not-triggered`. Persistence status is `pending` or `verified`. State is disposable and cannot replace the GitHub record.
