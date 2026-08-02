#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Audit centralized rule cards, provider symlinks, and workflow policy."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

CANONICAL_RULES = Path(".agents.config/rules")
PROVIDER_RULE_LINKS = (Path(".agents/rules"), Path(".claude/rules"))
LOCKED_SKILL_TYPES = {"meta", "ops"}
SKILL_TYPES = ("meta", "ops", "dev")
REQUIRED_EXPLICIT_DEV_SKILLS = {"feature-plan", "implement-story", "publish-issues"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit centralized rules and AI workflow invocation policy."
    )
    parser.add_argument("root", type=Path, help="Git repository root")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    return parser.parse_args()


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


def comparable_path(path: str | Path) -> str:
    return os.path.normcase(os.path.abspath(os.path.normpath(path)))


def sidecar_implicit_policy(content: str) -> str | None:
    match = re.search(
        r"^policy:\s*$[\s\S]*?^\s+allow_implicit_invocation:\s*(true|false)\s*$",
        content,
        re.MULTILINE,
    )
    return match.group(1) if match else None


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    canonical_root = root / CANONICAL_RULES
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    def relative(path: Path) -> str:
        try:
            return path.relative_to(root).as_posix() or "."
        except ValueError:
            return path.as_posix()

    def issue(items: list[dict[str, str]], code: str, path: Path, message: str) -> None:
        items.append({"code": code, "path": relative(path), "message": message})

    def run_git(*git_args: str) -> str:
        result = subprocess.run(
            ["git", *git_args],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    def tracked_mode(repository_path: str) -> str | None:
        try:
            output = run_git("ls-files", "-s", "--", repository_path)
        except (OSError, subprocess.CalledProcessError):
            return None
        for line in output.splitlines():
            if "\t" not in line:
                continue
            metadata, path = line.split("\t", 1)
            if path.replace("\\", "/") == repository_path:
                return metadata.split()[0]
        return None

    try:
        git_root = run_git("rev-parse", "--show-toplevel")
        revision = run_git("rev-parse", "HEAD")
        dirty = bool(run_git("status", "--porcelain"))
    except (OSError, subprocess.CalledProcessError):
        print(f"Repository root is not a Git worktree: {root}", file=sys.stderr)
        return 2
    if comparable_path(git_root) != comparable_path(root):
        print(f"Expected repository root {git_root}, received {root}.", file=sys.stderr)
        return 2

    if canonical_root.is_symlink() or not canonical_root.is_dir():
        print(
            f"Canonical rules directory is missing or not a real directory: {canonical_root}",
            file=sys.stderr,
        )
        return 2

    valid_provider_links = 0
    untracked_provider_links = 0
    for provider_relative in PROVIDER_RULE_LINKS:
        provider_link = root / provider_relative
        if not provider_link.is_symlink():
            issue(
                errors,
                "invalid-provider-rule-link",
                provider_link,
                "Provider rules path must be a directory symlink to .agents.config/rules.",
            )
            continue
        target = os.readlink(provider_link)
        if os.path.isabs(target):
            issue(
                errors,
                "absolute-provider-rule-link",
                provider_link,
                "Project rule symlinks must use repository-relative targets.",
            )
            continue
        try:
            resolved = provider_link.resolve(strict=True)
        except OSError:
            issue(
                errors,
                "broken-provider-rule-link",
                provider_link,
                "Provider rules symlink target does not resolve.",
            )
            continue
        if comparable_path(resolved) != comparable_path(canonical_root):
            issue(
                errors,
                "provider-rule-link-drift",
                provider_link,
                "Provider rules symlink resolves outside .agents.config/rules.",
            )
            continue
        mode = tracked_mode(relative(provider_link))
        if mode and mode != "120000":
            issue(
                errors,
                "invalid-provider-rule-mode",
                provider_link,
                f"Tracked provider link mode is {mode}; expected 120000.",
            )
            continue
        if not mode:
            untracked_provider_links += 1
        valid_provider_links += 1

    card_paths = sorted(
        path for path in canonical_root.glob("*.md") if path.name != "index.md"
    )
    cards: list[dict[str, Any]] = []
    identifiers: dict[str, Path] = {}

    for path in card_paths:
        content = path.read_text(encoding="utf-8")
        for stale in (".agent-config/", ".agents-config/"):
            if stale in content:
                issue(
                    errors,
                    "stale-central-path",
                    path,
                    f"Rule card still references the rejected path {stale}.",
                )
        parsed = frontmatter(content)
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

    global_path = canonical_root / "global.md"
    global_content = (
        global_path.read_text(encoding="utf-8") if global_path.is_file() else ""
    )
    required_workflow_markers = (
        "## AI Workflow & Invocation Decision Framework",
        "### Slash command workflows",
        "`.agents.config/skills/meta/`",
        "`.agents.config/skills/ops/`",
        "`disable-model-invocation: true`",
        "`allow_implicit_invocation: false`",
        "### Progressive disclosure skills",
        "`.agents.config/skills/dev/`",
    )
    for marker in required_workflow_markers:
        if marker not in global_content:
            issue(
                errors,
                "missing-workflow-framework",
                global_path,
                f"Global rule is missing required workflow marker: {marker}",
            )

    skills_card = next((card for card in cards if card["id"] == "skills"), None)
    required_skill_scopes = {
        ".agents.config/skills/**/*",
        ".agents/skills/*",
        ".claude/skills/*",
    }
    if skills_card is None:
        issue(
            errors,
            "missing-skills-rule",
            canonical_root / "skills.md",
            "The centralized skills rule card is missing.",
        )
    elif not required_skill_scopes.issubset(set(skills_card["paths"])):
        issue(
            errors,
            "incomplete-skills-scope",
            skills_card["path"],
            "Skills rule must cover canonical packages and both provider adapter roots.",
        )

    skills_root = root / ".agents.config" / "skills"
    seen_skill_names: dict[str, Path] = {}
    for skill_type in SKILL_TYPES:
        type_root = skills_root / skill_type
        if type_root.is_symlink() or not type_root.is_dir():
            issue(
                errors,
                "missing-skill-type",
                type_root,
                "Workflow framework requires real meta, ops, and dev skill directories.",
            )
            continue
        for skill_path in sorted(type_root.iterdir(), key=lambda path: path.name):
            if skill_path.is_symlink() or not skill_path.is_dir():
                continue
            if skill_path.name in seen_skill_names:
                issue(
                    errors,
                    "duplicate-skill-name",
                    skill_path,
                    f"Flat provider discovery would collide with {relative(seen_skill_names[skill_path.name])}.",
                )
            else:
                seen_skill_names[skill_path.name] = skill_path
            skill_file = skill_path / "SKILL.md"
            if not skill_file.is_file():
                continue
            parsed = frontmatter(skill_file.read_text(encoding="utf-8"))
            raw = parsed[0] if parsed and parsed[0] is not None else None
            disable_model = top_value(raw, "disable-model-invocation")
            sidecar = skill_path / "agents" / "openai.yaml"
            implicit_policy = (
                sidecar_implicit_policy(sidecar.read_text(encoding="utf-8"))
                if sidecar.is_file()
                else None
            )
            requires_explicit = (
                skill_type in LOCKED_SKILL_TYPES
                or skill_path.name in REQUIRED_EXPLICIT_DEV_SKILLS
            )
            if disable_model not in (None, "true"):
                issue(
                    errors,
                    "invalid-claude-invocation-lock",
                    skill_file,
                    "disable-model-invocation must be omitted or set to true.",
                )
            if requires_explicit:
                if disable_model != "true":
                    issue(
                        errors,
                        "missing-claude-invocation-lock",
                        skill_file,
                        "Explicit-only skills require disable-model-invocation: true.",
                    )
                if implicit_policy != "false":
                    issue(
                        errors,
                        "missing-openai-invocation-lock",
                        sidecar,
                        "Explicit-only skills require policy.allow_implicit_invocation: false.",
                    )
            if skill_type == "dev" and (disable_model == "true") != (
                implicit_policy == "false"
            ):
                issue(
                    errors,
                    "provider-invocation-lock-mismatch",
                    skill_path,
                    "Dev skills must use both provider invocation locks or neither lock.",
                )

    result = {
        "root": str(root),
        "revision": revision,
        "dirtyAtStart": dirty,
        "summary": {
            "cards": len(cards),
            "providerRuleLinks": valid_provider_links,
            "untrackedProviderRuleLinks": untracked_provider_links,
            "skills": len(seen_skill_names),
            "errors": len(errors),
            "warnings": len(warnings),
        },
        "errors": errors,
        "warnings": warnings,
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("# Rules audit\n")
        print(f"- Root: `{root}`")
        print(f"- Revision: `{revision}`")
        print(f"- Dirty at start: `{str(dirty).lower()}`")
        print(f"- Cards: {len(cards)}")
        print(f"- Provider rule links: {valid_provider_links}")
        print(f"- Untracked provider rule links: {untracked_provider_links}")
        print(f"- Skills checked for invocation policy: {len(seen_skill_names)}")
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
