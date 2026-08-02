#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate disposable feature-plan state and report the next bounded action."""

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


def valid_digest(value: object) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"sha256:[0-9a-f]{64}", value))


def valid_revision(value: object) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"[0-9a-fA-F]{40}", value))


def validate(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    if data.get("workflowVersion") != "1.0.0":
        errors.append("workflowVersion must be 1.0.0")
    if not isinstance(data.get("skillVersion"), str) or not re.fullmatch(
        r"[0-9a-fA-F]{40}:\.agents/skills/feature-plan", data["skillVersion"]
    ):
        errors.append("skillVersion must identify the committed feature-plan package")
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

    if stages.get("publication", {}).get("status") == "complete":
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

    return {
        "valid": not errors,
        "featureKey": data.get("featureKey"),
        "skillVersion": data.get("skillVersion"),
        "nextAction": next_action,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("state", type=Path)
    args = parser.parse_args()
    result = validate(args.state)
    print(json.dumps(result, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
