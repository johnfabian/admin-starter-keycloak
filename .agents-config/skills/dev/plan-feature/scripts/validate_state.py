#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate disposable plan-feature state and report the next bounded action."""

# Historical 1.x validator only; never use its output to authorize v2 delivery.
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

STAGES = [
    ("research", "$feature-research"),
    ("requirements", "$requirements-interview"),
    ("architectureImpact", "$architecture-impact"),
    ("edgeCases", "$find-edge-cases"),
    ("testStrategy", "$test-strategy"),
    ("stories", "$decompose-stories"),
    ("critique", "$critique-plan"),
    ("featureApproval", "obtain attributable feature approval"),
    ("preview", "$preview-issues"),
    ("publicationApproval", "obtain approval of the exact preview digest"),
    ("publication", "$publish-issues"),
]
VALID_STATUS = {"pending", "in_progress", "complete", "blocked"}
VALID_GATE_STATUS = {"pending", "passed", "blocked", "not-triggered"}
HUMAN_APPROVAL_STAGES = {"featureApproval", "publicationApproval"}
PERSISTED_STAGES = {
    "research",
    "requirements",
    "architectureImpact",
    "edgeCases",
    "testStrategy",
    "stories",
    "critique",
}
VALID_PERSISTENCE_STATUS = {"pending", "verified"}


def valid_digest(value: object) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"sha256:[0-9a-f]{64}", value))


def valid_revision(value: object) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"[0-9a-fA-F]{40}", value))


def valid_github_comment_url(value: object) -> bool:
    return isinstance(value, str) and bool(
        re.fullmatch(
            r"https://github\.com/[^/\s]+/[^/\s]+/(?:issues|pull)/\d+#issuecomment-\d+",
            value,
        )
    )


def valid_github_approval_url(value: object) -> bool:
    return isinstance(value, str) and bool(
        re.fullmatch(
            r"https://github\.com/[^/\s]+/[^/\s]+/(?:issues|pull)/\d+#(?:issuecomment|pullrequestreview)-\d+",
            value,
        )
    )


def valid_timestamp(value: object) -> bool:
    return isinstance(value, str) and bool(
        re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z", value)
    )


def valid_comment_key(value: object) -> bool:
    return isinstance(value, str) and bool(
        re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", value)
    )


def validate_persisted_record(
    record: object, location: str, errors: list[str]
) -> str | None:
    if not isinstance(record, dict):
        errors.append(f"{location} must be an object")
        return None
    unknown = set(record) - {
        "commentKey",
        "artifactDigest",
        "bodyDigest",
        "githubUrl",
        "verifiedAt",
    }
    if unknown:
        errors.append(f"{location} has unsupported fields: {sorted(unknown)}")
    if not valid_comment_key(record.get("commentKey")):
        errors.append(f"{location}.commentKey is invalid")
    if not valid_digest(record.get("artifactDigest")):
        errors.append(f"{location}.artifactDigest must be a sha256 digest")
    if not valid_digest(record.get("bodyDigest")):
        errors.append(f"{location}.bodyDigest must be a sha256 digest")
    if not valid_github_comment_url(record.get("githubUrl")):
        errors.append(
            f"{location}.githubUrl must be an immutable GitHub issue comment URL"
        )
    if not valid_timestamp(record.get("verifiedAt")):
        errors.append(f"{location}.verifiedAt must be an ISO 8601 UTC timestamp")
    return (
        record.get("commentKey") if isinstance(record.get("commentKey"), str) else None
    )


def validate_data(data: object) -> dict[str, object]:
    if not isinstance(data, dict):
        return {
            "valid": False,
            "planningComplete": False,
            "featureKey": None,
            "skillVersion": None,
            "workflowVersion": None,
            "migrationRequired": False,
            "persistenceStatus": "unknown",
            "nextAction": "$feature-research",
            "errors": ["state must be a JSON object"],
        }
    errors: list[str] = []
    workflow_version = data.get("workflowVersion")
    if workflow_version not in {"1.0.0", "1.1.0"}:
        errors.append("workflowVersion must be 1.0.0 or 1.1.0")
    skill_version = data.get("skillVersion")
    if not isinstance(skill_version, str) or not re.fullmatch(
        r"[0-9a-fA-F]{40}:\.agents-config/skills/dev/plan-feature",
        skill_version,
    ):
        errors.append("skillVersion must identify the committed plan-feature package")
    if not isinstance(data.get("featureKey"), str) or not data["featureKey"].strip():
        errors.append("featureKey must be non-empty")
    revision = data.get("sourceRevision")
    if not valid_revision(revision):
        errors.append("sourceRevision must be a full 40-character commit SHA")
    stages = data.get("stages")
    if not isinstance(stages, dict):
        errors.append("stages must be an object")
        stages = {}

    seen_incomplete = False
    next_action = "planning complete"
    for name, action in STAGES:
        stage = stages.get(name)
        if not isinstance(stage, dict):
            errors.append(f"missing stage: {name}")
            seen_incomplete = True
            if next_action == "planning complete":
                next_action = action
            continue
        status = stage.get("status")
        if status not in VALID_STATUS:
            errors.append(f"{name}.status is invalid")
            status = "pending"
        if status == "complete":
            if seen_incomplete:
                errors.append(f"{name} cannot be complete before earlier stages")
            if (
                not isinstance(stage.get("artifact"), str)
                or not stage["artifact"].strip()
            ):
                errors.append(f"{name} complete requires an artifact path or URL")
            if not valid_digest(stage.get("digest")):
                errors.append(f"{name} complete requires a sha256 digest")
            if not valid_revision(stage.get("sourceRevision")):
                errors.append(f"{name} complete requires a full sourceRevision")
            if stage.get("gateStatus") not in VALID_GATE_STATUS:
                errors.append(f"{name} complete requires a valid gateStatus")
            elif stage["gateStatus"] in {"pending", "blocked"}:
                errors.append(
                    f"{name} cannot be complete while its gate is {stage['gateStatus']}"
                )
            if name in HUMAN_APPROVAL_STAGES:
                approval = stage.get("approval")
                if not isinstance(approval, dict) or not all(
                    isinstance(approval.get(field), str) and approval[field].strip()
                    for field in ("actor", "record", "approvedAt", "artifactDigest")
                ):
                    errors.append(
                        f"{name} complete requires an attributable approval record"
                    )
                elif not valid_digest(approval["artifactDigest"]):
                    errors.append(
                        f"{name}.approval.artifactDigest must be a sha256 digest"
                    )
                if stage.get("gateStatus") != "passed":
                    errors.append(f"{name} complete requires gateStatus=passed")
        else:
            seen_incomplete = True
            if next_action == "planning complete":
                next_action = action

    publication_complete = stages.get("publication", {}).get("status") == "complete"
    if publication_complete:
        if not data.get("approved") or not valid_digest(data.get("previewDigest")):
            errors.append(
                "publication requires approved=true and a sha256 previewDigest"
            )
        preview_stage_digest = stages.get("preview", {}).get("digest")
        if data.get("previewDigest") != preview_stage_digest:
            errors.append("previewDigest must match the completed preview stage digest")

    publication_approval = stages.get("publicationApproval", {})
    if publication_approval.get("status") == "complete":
        approval = publication_approval.get("approval")
        approved_artifact_digest = (
            approval.get("artifactDigest") if isinstance(approval, dict) else None
        )
        preview_stage_digest = stages.get("preview", {}).get("digest")
        if approved_artifact_digest != preview_stage_digest:
            errors.append(
                "publicationApproval must approve the completed preview stage digest"
            )
        if data.get("previewDigest") not in {None, preview_stage_digest}:
            errors.append(
                "previewDigest cannot differ from the publication approval artifact"
            )

    persistence_status = "legacy"
    migration_required = workflow_version == "1.0.0"
    if workflow_version == "1.1.0":
        persistence = data.get("persistence")
        if not isinstance(persistence, dict):
            errors.append("persistence must be an object for workflowVersion 1.1.0")
            persistence = {}
        unknown = set(persistence) - {"status", "artifacts", "handoffs"}
        if unknown:
            errors.append(f"persistence has unsupported fields: {sorted(unknown)}")
        persistence_status = persistence.get("status")
        if persistence_status not in VALID_PERSISTENCE_STATUS:
            errors.append("persistence.status must be pending or verified")
            persistence_status = "pending"
        artifacts = persistence.get("artifacts")
        if not isinstance(artifacts, dict):
            errors.append("persistence.artifacts must be an object")
            artifacts = {}
        handoffs = persistence.get("handoffs")
        if not isinstance(handoffs, list):
            errors.append("persistence.handoffs must be an array")
            handoffs = []

        if persistence_status == "verified":
            missing = PERSISTED_STAGES - set(artifacts)
            if missing:
                errors.append(
                    f"verified persistence is missing required artifacts: {sorted(missing)}"
                )
            comment_keys: list[str] = []
            for name, record in artifacts.items():
                if not isinstance(name, str) or not re.fullmatch(
                    r"[A-Za-z][A-Za-z0-9]*", name
                ):
                    errors.append(f"persistence artifact key is invalid: {name}")
                    continue
                comment_key = validate_persisted_record(
                    record, f"persistence.artifacts.{name}", errors
                )
                if comment_key:
                    comment_keys.append(comment_key)
                if (
                    name in PERSISTED_STAGES
                    and isinstance(record, dict)
                    and record.get("artifactDigest")
                    != stages.get(name, {}).get("digest")
                ):
                    errors.append(
                        f"persistence.artifacts.{name}.artifactDigest must match the completed stage digest"
                    )
            if not handoffs:
                errors.append(
                    "verified persistence requires at least one durable handoff"
                )
            for index, record in enumerate(handoffs):
                comment_key = validate_persisted_record(
                    record, f"persistence.handoffs[{index}]", errors
                )
                if comment_key:
                    comment_keys.append(comment_key)
            if len(comment_keys) != len(set(comment_keys)):
                errors.append(
                    "persisted artifact and handoff comment keys must be unique"
                )
            for approval_stage in HUMAN_APPROVAL_STAGES:
                approval = stages.get(approval_stage, {}).get("approval")
                if not isinstance(approval, dict) or not valid_github_approval_url(
                    approval.get("record")
                ):
                    errors.append(
                        f"verified persistence requires {approval_stage}.approval.record to be an immutable GitHub comment URL"
                    )
            if not publication_complete:
                errors.append(
                    "persistence cannot be verified before publication completes"
                )

    if publication_complete:
        if workflow_version == "1.0.0":
            errors.append(
                "workflowVersion 1.0.0 cannot represent post-publication persistence; migrate to 1.1.0"
            )
        elif persistence_status != "verified" and next_action == "planning complete":
            next_action = "verify durable GitHub artifacts and handoffs"

    planning_complete = (
        not errors
        and all(
            isinstance(stages.get(name), dict)
            and stages[name].get("status") == "complete"
            for name, _ in STAGES
        )
        and workflow_version == "1.1.0"
        and persistence_status == "verified"
    )

    return {
        "valid": not errors,
        "planningComplete": planning_complete,
        "featureKey": data.get("featureKey"),
        "skillVersion": data.get("skillVersion"),
        "workflowVersion": workflow_version,
        "migrationRequired": migration_required,
        "persistenceStatus": persistence_status,
        "nextAction": next_action,
        "errors": errors,
    }


def validate(path: Path) -> dict[str, object]:
    return validate_data(json.loads(path.read_text(encoding="utf-8")))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("state", type=Path)
    args = parser.parse_args()
    result = validate(args.state)
    print(json.dumps(result, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
