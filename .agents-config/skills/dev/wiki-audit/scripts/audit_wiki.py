#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Audit an OKF v0.2 repository wiki."""

from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import unquote

ACTOR_PATTERN = re.compile(r"^(?:human:\S+|process:\S+|\S+/\S+)$")


def frontmatter(content: str) -> tuple[str | None, str | None] | None:
    normalized = content.lstrip("\ufeff").replace("\r\n", "\n")
    if not normalized.startswith("---\n"):
        return None
    end = normalized.find("\n---\n", 4)
    if end < 0:
        return None, None
    return normalized[4:end], normalized[end + 5 :]


def unquote_value(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def top_value(raw: str, key: str) -> str | None:
    match = re.search(rf"^{re.escape(key)}:\s*(.*)$", raw, re.MULTILINE)
    return unquote_value(match.group(1)) if match else None


def flow_value(value: str | None, key: str) -> str | None:
    if not value:
        return None
    match = re.search(rf"(?:^|[{{,]\s*){re.escape(key)}:\s*([^,}}]+)", value)
    return unquote_value(match.group(1)) if match else None


def valid_profile_yaml(raw: str | None) -> bool:
    if not raw or "\t" in raw:
        return False
    saw_top_level = False
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        if indent % 2:
            return False
        text = line.strip()
        if indent == 0:
            if not re.match(r"^[A-Za-z_][A-Za-z0-9_-]*:\s*.*$", text):
                return False
            saw_top_level = True
        elif not re.match(r"^(?:-\s+)?[A-Za-z_][A-Za-z0-9_-]*:\s*.*$", text):
            return False
        if len(re.findall(r"[\[{]", text)) != len(re.findall(r"[\]}]", text)):
            return False
    return saw_top_level


def source_blocks(raw: str) -> list[list[str]]:
    lines = raw.splitlines()
    try:
        start = next(
            index
            for index, line in enumerate(lines)
            if re.match(r"^sources:\s*$", line)
        )
    except StopIteration:
        return []
    blocks: list[list[str]] = []
    current: list[str] | None = None
    for line in lines[start + 1 :]:
        if re.match(r"^[A-Za-z_][A-Za-z0-9_-]*:", line):
            break
        item = re.match(r"^\s{2}-\s+(.*)$", line)
        if item:
            if current:
                blocks.append(current)
            current = [item.group(1)]
        elif current is not None and re.match(r"^\s{4}\S", line):
            current.append(line.strip())
    if current:
        blocks.append(current)
    return blocks


def markdown_links(content: str) -> list[str]:
    return [
        match.group(1)
        for match in re.finditer(r'\[[^\]]+\]\(([^)\s]+)(?:\s+"[^"]*")?\)', content)
    ]


def valid_timestamp(value: str | None) -> bool:
    if not value:
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def valid_iso_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value))


def main() -> int:
    args = sys.argv[1:]
    json_output = "--json" in args
    targets = [arg for arg in args if arg != "--json"]
    if not targets:
        print("Usage: uv run audit_wiki.py <wiki-root> [--json]", file=sys.stderr)
        return 2

    root = Path(targets[0]).resolve()
    if not root.is_dir():
        print(f"Wiki root is not a directory: {root}", file=sys.stderr)
        return 2

    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    concepts: list[dict[str, str | None]] = []

    def relative(path: Path) -> str:
        try:
            return path.relative_to(root).as_posix() or "."
        except ValueError:
            return path.as_posix()

    def issue(items: list[dict[str, str]], code: str, path: Path, message: str) -> None:
        items.append({"code": code, "path": relative(path), "message": message})

    markdown_files = sorted(path for path in root.rglob("*.md") if path.is_file())
    root_index = root / "index.md"
    root_log = root / "log.md"
    if not root_index.exists():
        issue(errors, "missing-root-index", root_index, "Missing root index.md.")
    if not root_log.exists():
        issue(errors, "missing-root-log", root_log, "Missing root log.md.")

    for path in markdown_files:
        name = path.name.lower()
        content = path.read_text(encoding="utf-8")
        parsed = frontmatter(content)

        if name == "index.md":
            if path == root_index:
                if not parsed or parsed[0] is None or not valid_profile_yaml(parsed[0]):
                    issue(
                        errors,
                        "invalid-root-index-frontmatter",
                        path,
                        "Root index must have parseable profile frontmatter.",
                    )
                else:
                    raw = parsed[0]
                    if top_value(raw, "okf_version") != "0.2":
                        issue(
                            errors,
                            "invalid-okf-version",
                            path,
                            'Root index must declare okf_version: "0.2".',
                        )
                    extra_keys = [
                        line.split(":", 1)[0]
                        for line in raw.splitlines()
                        if re.match(r"^[A-Za-z_][A-Za-z0-9_-]*:", line)
                        and line.split(":", 1)[0] != "okf_version"
                    ]
                    if extra_keys:
                        issue(
                            warnings,
                            "root-index-extra-metadata",
                            path,
                            f"Unexpected root index keys: {', '.join(extra_keys)}.",
                        )
            elif parsed:
                issue(
                    errors,
                    "nested-index-frontmatter",
                    path,
                    "Nested index.md must not have frontmatter.",
                )
            continue

        if name == "log.md":
            if parsed:
                issue(
                    errors, "log-frontmatter", path, "log.md must not have frontmatter."
                )
            dates = re.findall(r"^##\s+(\d{4}-\d{2}-\d{2})\s*$", content, re.MULTILINE)
            if not dates:
                issue(
                    errors,
                    "missing-log-date",
                    path,
                    "log.md must contain an ISO date heading.",
                )
            if any(not valid_iso_date(value) for value in dates):
                issue(
                    errors,
                    "invalid-log-date",
                    path,
                    "log.md contains an invalid ISO date heading.",
                )
            if dates != sorted(dates, reverse=True):
                issue(
                    errors,
                    "log-order",
                    path,
                    "log.md date headings must be newest first.",
                )
            continue

        if not parsed or parsed[0] is None:
            issue(
                errors,
                "missing-frontmatter",
                path,
                "Concept must start with a closed YAML frontmatter block.",
            )
            continue
        raw, body = parsed
        if not valid_profile_yaml(raw):
            issue(
                errors,
                "invalid-profile-yaml",
                path,
                "Frontmatter is outside the supported OKF profile syntax.",
            )
            continue

        concept_type = top_value(raw, "type")
        status = top_value(raw, "status")
        stale_after = top_value(raw, "stale_after")
        generated = top_value(raw, "generated")
        concepts.append(
            {
                "path": relative(path),
                "type": concept_type,
                "status": status or "stable",
                "staleAfter": stale_after,
            }
        )

        if not concept_type:
            issue(errors, "missing-type", path, "Concept type must be non-empty.")
        for field in ("title", "description", "tags"):
            if not top_value(raw, field):
                issue(
                    warnings,
                    f"missing-{field}",
                    path,
                    f"Recommended field {field} is missing.",
                )
        if status and status not in {"draft", "stable", "deprecated"}:
            issue(
                errors, "invalid-status", path, f"Invalid lifecycle status: {status}."
            )

        if not generated:
            issue(warnings, "missing-generated", path, "generated metadata is missing.")
        else:
            actor = flow_value(generated, "by")
            generated_at = flow_value(generated, "at")
            if not actor or not ACTOR_PATTERN.fullmatch(actor):
                issue(
                    errors,
                    "invalid-generated-actor",
                    path,
                    "generated.by does not follow the actor convention.",
                )
            if not valid_timestamp(generated_at):
                issue(
                    errors,
                    "invalid-generated-at",
                    path,
                    "generated.at must be an ISO 8601 timestamp.",
                )

        if stale_after:
            if not valid_iso_date(stale_after):
                issue(
                    errors,
                    "invalid-stale-after",
                    path,
                    "stale_after must be an ISO date.",
                )
            elif stale_after <= datetime.now(timezone.utc).date().isoformat():
                issue(
                    warnings,
                    "stale-concept",
                    path,
                    f"Concept is stale as of {stale_after}.",
                )
        else:
            issue(warnings, "missing-stale-after", path, "stale_after is not declared.")

        sources = source_blocks(raw)
        if not sources:
            issue(
                warnings, "missing-sources", path, "No provenance sources are declared."
            )
        for block in sources:
            if not any(re.match(r"^resource:\s*\S+", line) for line in block):
                issue(
                    errors,
                    "source-without-resource",
                    path,
                    "Each source entry must have a resource.",
                )

        verified_actors = re.findall(r"\bby:\s*([^,}\s]+)", raw)
        for actor in verified_actors[1 if generated else 0 :]:
            if not ACTOR_PATTERN.fullmatch(actor):
                issue(
                    errors,
                    "invalid-verifier-actor",
                    path,
                    f"Invalid verifier actor: {actor}.",
                )
        if (status or "stable") == "stable" and not top_value(raw, "verified"):
            issue(
                warnings,
                "unverified-stable",
                path,
                "Stable concept has no verification event.",
            )
        if re.search(
            r"^#{1,3}\s+(Acceptance criteria|Exact next action|Current status|AI SDLC checkpoint)\s*$",
            body or "",
            re.IGNORECASE | re.MULTILINE,
        ):
            issue(
                warnings,
                "possible-feature-content",
                path,
                "Concept may contain active feature or handoff content.",
            )

        for target in markdown_links(body or ""):
            without_anchor = unquote(target.split("#", 1)[0])
            if not without_anchor or re.match(
                r"^[a-z][a-z0-9+.-]*:", without_anchor, re.IGNORECASE
            ):
                continue
            resolved = (
                root / without_anchor.removeprefix("/")
                if without_anchor.startswith("/")
                else path.parent / without_anchor
            ).resolve()
            if resolved.is_relative_to(root) and not resolved.exists():
                issue(
                    warnings,
                    "broken-internal-link",
                    path,
                    f"Broken wiki link: {target}.",
                )

    directories = sorted({path.parent for path in markdown_files})
    for directory in directories:
        index_path = directory / "index.md"
        if not index_path.exists():
            issue(
                warnings,
                "missing-directory-index",
                directory,
                "Directory containing Markdown has no index.md.",
            )
            continue
        listed = {
            target.removeprefix("./").rstrip("/")
            for target in markdown_links(index_path.read_text(encoding="utf-8"))
        }
        for entry in directory.iterdir():
            if (
                entry.is_file()
                and entry.suffix == ".md"
                and entry.name not in {"index.md", "log.md"}
            ):
                if entry.name not in listed:
                    issue(
                        warnings,
                        "concept-not-indexed",
                        index_path,
                        f"Missing concept entry: {entry.name}.",
                    )
            elif (
                entry.is_dir() and any(entry.rglob("*.md")) and entry.name not in listed
            ):
                issue(
                    warnings,
                    "directory-not-indexed",
                    index_path,
                    f"Missing subdirectory entry: {entry.name}/.",
                )

    result = {
        "root": str(root),
        "summary": {
            "concepts": len(concepts),
            "errors": len(errors),
            "warnings": len(warnings),
        },
        "errors": errors,
        "warnings": warnings,
    }
    if json_output:
        print(json.dumps(result, indent=2))
    else:
        print("# Wiki audit\n")
        print(f"- Root: `{root}`")
        print(f"- Concepts: {len(concepts)}")
        print(f"- Errors: {len(errors)}")
        print(f"- Warnings: {len(warnings)}\n")
        for title, items in (("Errors", errors), ("Warnings", warnings)):
            print(f"## {title}\n")
            if not items:
                print("None.\n")
            for item in items:
                print(f"- **{item['code']}** `{item['path']}`: {item['message']}")
            if items:
                print()
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
