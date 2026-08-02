#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify an approved preview digest and its canonical source-input digest."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def require_issue(value: Any, location: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError(f"{location} must be an object")
    unknown = set(value) - {"key", "title", "type", "body", "labels", "dependsOn"}
    if unknown:
        raise ValueError(f"{location} has unsupported fields: {sorted(unknown)}")
    for field in ("key", "title", "type", "body"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            raise ValueError(f"{location}.{field} must be a non-empty string")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", value["key"]):
        raise ValueError(f"{location}.key contains unsupported characters")
    if "<!-- sdlc-key:" in value["body"].lower():
        raise ValueError(f"{location}.body must not contain an SDLC idempotency marker")
    labels = value.get("labels", [])
    if not isinstance(labels, list) or not all(
        isinstance(item, str) for item in labels
    ):
        raise ValueError(f"{location}.labels must be a string array")
    dependencies = value.get("dependsOn", [])
    if not isinstance(dependencies, list) or not all(
        isinstance(item, str) for item in dependencies
    ):
        raise ValueError(f"{location}.dependsOn must be a string array")
    return value


def validate_source(data: Any) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if not isinstance(data, dict):
        raise TypeError("input must be a JSON object")
    unknown = set(data) - {
        "repository",
        "sourceRevision",
        "skillVersion",
        "parent",
        "children",
    }
    if unknown:
        raise ValueError(f"input has unsupported fields: {sorted(unknown)}")
    if not isinstance(data.get("repository"), str) or not re.fullmatch(
        r"[^/\s]+/[^/\s]+", data["repository"]
    ):
        raise ValueError("repository must use owner/name form")
    if not isinstance(data.get("sourceRevision"), str) or not re.fullmatch(
        r"[0-9a-fA-F]{40}", data["sourceRevision"]
    ):
        raise ValueError("sourceRevision must be a full 40-character commit SHA")
    if not isinstance(data.get("skillVersion"), str) or not re.fullmatch(
        r"[0-9a-fA-F]{40}:\.agents/skills/preview-issues", data["skillVersion"]
    ):
        raise ValueError(
            "skillVersion must identify the committed preview-issues package"
        )
    parent = require_issue(data.get("parent"), "parent")
    children_value = data.get("children", [])
    if not isinstance(children_value, list):
        raise TypeError("children must be an array")
    children = [
        require_issue(value, f"children[{index}]")
        for index, value in enumerate(children_value)
    ]
    keys = [parent["key"], *(child["key"] for child in children)]
    if len(keys) != len(set(keys)):
        raise ValueError("issue keys must be unique")
    child_keys = {child["key"] for child in children}
    for child in children:
        unknown_dependencies = set(child.get("dependsOn", [])) - child_keys
        if unknown_dependencies:
            raise ValueError(
                f"{child['key']} has unknown dependencies: {sorted(unknown_dependencies)}"
            )
        if child["key"] in child.get("dependsOn", []):
            raise ValueError(f"{child['key']} cannot depend on itself")

    dependencies_by_key = {
        child["key"]: child.get("dependsOn", []) for child in children
    }
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(key: str) -> None:
        if key in visiting:
            raise ValueError(f"dependency cycle includes {key}")
        if key in visited:
            return
        visiting.add(key)
        for dependency in dependencies_by_key[key]:
            visit(dependency)
        visiting.remove(key)
        visited.add(key)

    for key in sorted(dependencies_by_key):
        visit(key)
    return parent, children


def issue_section(issue: dict[str, Any], parent_key: str | None = None) -> list[str]:
    labels = ", ".join(f"`{label}`" for label in issue.get("labels", [])) or "none"
    dependencies = ", ".join(f"`{key}`" for key in issue.get("dependsOn", [])) or "none"
    return [
        f"## {issue['key']}: {issue['title']}",
        "",
        f"- Type: `{issue['type']}`",
        f"- Parent: `{parent_key}`" if parent_key else "- Parent: none",
        f"- Dependencies: {dependencies}",
        f"- Labels: {labels}",
        "",
        "### Exact issue body",
        "",
        f"<!-- sdlc-key: {issue['key']} -->",
        issue["body"].rstrip(),
        "",
    ]


def render_expected(data: dict[str, Any]) -> bytes:
    parent, children = validate_source(data)
    input_digest = hashlib.sha256(canonical_bytes(data)).hexdigest()
    lines = [
        "# GitHub mutation preview",
        "",
        f"- Repository: `{data['repository']}`",
        f"- Source revision: `{data['sourceRevision']}`",
        f"- Skill version: `{data['skillVersion']}`",
        f"- Source input SHA-256: `{input_digest}`",
        "- Mutation status: `preview only; no GitHub changes performed`",
        "",
        *issue_section(parent),
    ]
    for child in children:
        lines.extend(issue_section(child, parent["key"]))
    lines.extend(
        [
            "## Approval boundary",
            "",
            "Approve the SHA-256 digest printed by the renderer for this exact UTF-8 file.",
            "Any edit requires a new preview and approval.",
            "",
        ]
    )
    return "\n".join(lines).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("preview", type=Path)
    parser.add_argument("approved_digest")
    parser.add_argument("source", type=Path)
    args = parser.parse_args()

    preview_bytes = args.preview.read_bytes()
    preview_digest = hashlib.sha256(preview_bytes).hexdigest()
    approved = args.approved_digest.removeprefix("sha256:").lower()
    source = json.loads(args.source.read_text(encoding="utf-8"))
    source_bytes = canonical_bytes(source)
    source_digest = hashlib.sha256(source_bytes).hexdigest()

    errors = []
    if preview_digest != approved:
        errors.append("preview digest does not match approved digest")
    try:
        expected_preview = render_expected(source)
    except (KeyError, TypeError, ValueError) as error:
        errors.append(f"source JSON is invalid: {error}")
    else:
        if preview_bytes != expected_preview:
            errors.append(
                "approved preview is not the deterministic rendering of source JSON"
            )
    result = {
        "valid": not errors,
        "previewSha256": preview_digest,
        "sourceSha256": source_digest,
        "errors": errors,
    }
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
