#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Audit canonical rule cards and their Claude adapters."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


def frontmatter(content: str) -> tuple[str | None, str | None] | None:
    normalized = content.lstrip("\ufeff").replace("\r\n", "\n")
    if not normalized.startswith("---\n"):
        return None
    end = normalized.find("\n---\n", 4)
    if end < 0:
        return None, None
    return normalized[4:end], normalized[end + 5 :]


def unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def top_value(raw: str | None, key: str) -> str | None:
    if not raw:
        return None
    lines = raw.splitlines()
    for index, line in enumerate(lines):
        if not re.match(rf"^{re.escape(key)}:", line):
            continue
        inline = line.split(":", 1)[1].strip()
        if inline:
            return unquote(inline)
        nested: list[str] = []
        for following in lines[index + 1 :]:
            if following and not following[0].isspace():
                break
            if following.strip():
                nested.append(following.strip())
        return unquote(" ".join(nested)) or None
    return None


def split_flow(value: str | None) -> list[str]:
    if not value or not value.startswith("[") or not value.endswith("]"):
        return []
    values: list[str] = []
    current: list[str] = []
    quote: str | None = None
    for character in value[1:-1]:
        if character in "\"'" and quote is None:
            quote = character
        elif character == quote:
            quote = None
        if character == "," and quote is None:
            item = unquote("".join(current))
            if item:
                values.append(item)
            current = []
        else:
            current.append(character)
    item = unquote("".join(current))
    if item:
        values.append(item)
    return values


def section_bullets(body: str | None, heading: str) -> set[str]:
    if not body:
        return set()
    match = re.search(
        rf"^## {re.escape(heading)}\s*$([\s\S]*?)(?=^## |\Z)",
        body,
        re.MULTILINE,
    )
    if not match:
        return set()
    return {
        item.group(1).strip().lower()
        for item in re.finditer(r"^[-*]\s+(.+)$", match.group(1), re.MULTILINE)
    }


def main() -> int:
    args = sys.argv[1:]
    json_output = "--json" in args
    targets = [arg for arg in args if arg != "--json"]
    if not targets:
        print(
            "Usage: uv run audit_rules.py <repository-root> [--json]", file=sys.stderr
        )
        return 2

    root = Path(targets[0]).resolve()
    canonical_root = root / ".agents" / "rules"
    adapter_root = root / ".claude" / "rules"
    if not canonical_root.is_dir():
        print(
            f"Canonical rules directory is missing: {canonical_root}", file=sys.stderr
        )
        return 2

    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    def relative(path: Path) -> str:
        try:
            return path.relative_to(root).as_posix() or "."
        except ValueError:
            return path.as_posix()

    def issue(items: list[dict[str, str]], code: str, path: Path, message: str) -> None:
        items.append({"code": code, "path": relative(path), "message": message})

    card_paths = sorted(
        path for path in canonical_root.glob("*.md") if path.name != "index.md"
    )
    cards: list[dict[str, Any]] = []
    identifiers: dict[str, Path] = {}

    for path in card_paths:
        parsed = frontmatter(path.read_text(encoding="utf-8"))
        if not parsed or parsed[0] is None:
            issue(
                errors,
                "missing-frontmatter",
                path,
                "Rule card must start with closed frontmatter.",
            )
            continue
        raw, body = parsed
        card: dict[str, Any] = {
            "path": path,
            "name": path.name,
            "id": top_value(raw, "id"),
            "paths": split_flow(top_value(raw, "paths")),
            "applies_to": split_flow(top_value(raw, "applies_to")),
            "owner": top_value(raw, "owner"),
            "enforcement": split_flow(top_value(raw, "enforcement")),
            "wiki": split_flow(top_value(raw, "wiki")),
            "config": split_flow(top_value(raw, "config")),
            "body": body,
        }
        cards.append(card)

        for key in ("id", "owner"):
            if not card[key]:
                issue(
                    errors, f"missing-{key}", path, f"Required field {key} is missing."
                )
        for key in ("paths", "applies_to", "enforcement", "config"):
            if not card[key]:
                issue(
                    errors,
                    f"missing-{key}",
                    path,
                    f"Required list {key} is empty or malformed.",
                )
        if card["paths"] != card["applies_to"]:
            issue(
                errors, "scope-drift", path, "paths and applies_to must match exactly."
            )
        identifier = card["id"]
        if identifier:
            if identifier in identifiers:
                issue(
                    errors,
                    "duplicate-id",
                    path,
                    f"Duplicate rule id also used by {relative(identifiers[identifier])}.",
                )
            else:
                identifiers[identifier] = path

        for config in card["config"]:
            if (
                config.startswith("/")
                and not (root / config.removeprefix("/")).exists()
            ):
                issue(
                    errors,
                    "missing-config",
                    path,
                    f"Mapped configuration does not exist: {config}.",
                )
        for wiki in card["wiki"]:
            if (
                wiki.startswith("/")
                and not (root / "wiki" / wiki.removeprefix("/")).exists()
            ):
                issue(
                    errors,
                    "missing-wiki-link",
                    path,
                    f"Mapped wiki concept does not exist: {wiki}.",
                )

        for statement in section_bullets(body, "Required") & section_bullets(
            body, "Prohibited"
        ):
            issue(
                errors,
                "self-contradiction",
                path,
                f"Directive is both required and prohibited: {statement}",
            )

        adapter_path = adapter_root / path.name
        if not adapter_path.exists():
            issue(
                errors,
                "missing-adapter",
                path,
                f"Claude adapter is missing: {relative(adapter_path)}.",
            )
            continue
        adapter = frontmatter(adapter_path.read_text(encoding="utf-8"))
        if not adapter or adapter[0] is None:
            issue(
                errors,
                "invalid-adapter",
                adapter_path,
                "Adapter must contain closed paths frontmatter.",
            )
            continue
        adapter_raw, adapter_body = adapter
        if split_flow(top_value(adapter_raw, "paths")) != card["paths"]:
            issue(
                errors,
                "adapter-path-drift",
                adapter_path,
                "Adapter paths differ from the canonical card.",
            )
        expected_import = f"@../../.agents/rules/{path.name}"
        if (adapter_body or "").strip() != expected_import:
            issue(
                errors,
                "adapter-body-drift",
                adapter_path,
                f"Adapter must contain only {expected_import}.",
            )

    index_path = canonical_root / "index.md"
    if not index_path.exists():
        issue(errors, "missing-index", index_path, "Canonical rule index is missing.")
    else:
        index_content = index_path.read_text(encoding="utf-8")
        for card in cards:
            if f"]({card['name']})" not in index_content:
                issue(
                    errors,
                    "card-not-indexed",
                    index_path,
                    f"Missing index entry for {card['name']}.",
                )

    for left_index, left in enumerate(cards):
        for right in cards[left_index + 1 :]:
            if left["id"] == "global" or right["id"] == "global":
                continue
            overlap = [path for path in left["paths"] if path in right["paths"]]
            if overlap:
                issue(
                    warnings,
                    "exact-scope-overlap",
                    right["path"],
                    f"Shares exact globs with {left['id']}: {', '.join(overlap)}. Review precedence.",
                )

    for directory_name in (
        "web",
        "api-express",
        "auth-server",
        "api-gateway",
        "postgres",
    ):
        directory = root / directory_name
        if not directory.exists():
            continue
        covered = any(
            card["id"] != "global"
            and any(
                glob == directory_name or glob.startswith(f"{directory_name}/")
                for glob in card["paths"]
            )
            for card in cards
        )
        if not covered:
            issue(
                warnings,
                "unmatched-protected-path",
                directory,
                "Implemented or protected area has only the global rule.",
            )

    result = {
        "root": str(root),
        "summary": {
            "cards": len(cards),
            "errors": len(errors),
            "warnings": len(warnings),
        },
        "errors": errors,
        "warnings": warnings,
    }
    if json_output:
        print(json.dumps(result, indent=2))
    else:
        print("# Rules audit\n")
        print(f"- Cards: {len(cards)}")
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
