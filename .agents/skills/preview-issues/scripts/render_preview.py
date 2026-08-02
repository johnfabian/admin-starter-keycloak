#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Render a deterministic, non-mutating GitHub issue preview from JSON."""

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


def validate(data: Any) -> tuple[dict[str, Any], list[dict[str, Any]]]:
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
    repository = data.get("repository")
    if not isinstance(repository, str) or not re.fullmatch(
        r"[^/\s]+/[^/\s]+", repository
    ):
        raise ValueError("repository must use owner/name form")
    revision = data.get("sourceRevision")
    if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", revision):
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
        unknown = set(child.get("dependsOn", [])) - child_keys
        if unknown:
            raise ValueError(
                f"{child['key']} has unknown dependencies: {sorted(unknown)}"
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
    lines = [
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
    return lines


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    parent, children = validate(data)
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
    output = "\n".join(lines)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output, encoding="utf-8", newline="\n")
    digest = hashlib.sha256(output.encode("utf-8")).hexdigest()
    print(json.dumps({"preview": str(args.output), "sha256": digest}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
