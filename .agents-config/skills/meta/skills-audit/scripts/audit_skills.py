#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Audit, categorize, and link shared repository skill packages."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

CATEGORIES = ("meta", "ops", "dev")
META_SKILLS = {"rules-audit", "skills-audit"}
OPS_SKILLS = {
    "prune-deleted-branches",
    "start-project",
    "start-server",
    "stop-project",
    "stop-server",
}
REQUIRED_EXPLICIT_SKILLS = (
    META_SKILLS
    | OPS_SKILLS
    | {
        "publish-issues",
    }
)
PROJECT_ADAPTERS = (Path(".agents/skills"), Path(".claude/skills"))
RENAMED_SKILLS = {
    "critique-plan": "critique-feature-spec",
    "decompose-stories": "plan-implementation",
}
GLOBAL_ADAPTERS = (Path(".claude/skills"), Path(".codex/skills"))
README_CATALOG_START = "<!-- skills-catalog:start -->"
README_CATALOG_END = "<!-- skills-catalog:end -->"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit typed shared skills and their flat provider symlinks."
    )
    parser.add_argument("root", type=Path, help="Git repository root")
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Categorize flat packages and repair safe symlink drift.",
    )
    parser.add_argument(
        "--global-adapters",
        action="store_true",
        help="Also audit or repair user-global adapters; omitted by default for worktree isolation.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument(
        "--home",
        type=Path,
        help="Override the home directory used for global adapters (useful for validation).",
    )
    return parser.parse_args()


def frontmatter(content: str) -> tuple[str | None, str | None] | None:
    normalized = content.lstrip("\ufeff").replace("\r\n", "\n")
    if not normalized.startswith("---\n"):
        return None
    end = normalized.find("\n---\n", 4)
    if end < 0:
        return None, None
    return normalized[4:end], normalized[end + 5 :]


def top_value(raw: str | None, key: str) -> str | None:
    if not raw:
        return None
    match = re.search(rf"^{re.escape(key)}:\s*(.*)$", raw, re.MULTILINE)
    if not match:
        return None
    value = match.group(1).strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def markdown_links(content: str) -> list[str]:
    return [
        match.group(1)
        for match in re.finditer(r'\[[^\]]+\]\(([^)\s]+)(?:\s+"[^"]*")?\)', content)
    ]


def comparable_path(path: str | Path) -> str:
    return os.path.normcase(os.path.abspath(os.path.normpath(path)))


def lexists(path: Path) -> bool:
    return os.path.lexists(path)


def category_for(name: str) -> str:
    if name in META_SKILLS:
        return "meta"
    if name in OPS_SKILLS or name == "keycloak-admin":
        return "ops"
    return "dev"


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
    home = (args.home or Path.home()).expanduser().resolve() if args.global_adapters else None
    canonical_root = root / ".agents-config" / "skills"
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    fixes: list[dict[str, str]] = []
    skills: list[dict[str, object]] = []

    def relative(path: Path) -> str:
        try:
            return path.relative_to(root).as_posix() or "."
        except ValueError:
            return path.as_posix()

    def issue(items: list[dict[str, str]], code: str, path: Path, message: str) -> None:
        items.append({"code": code, "path": relative(path), "message": message})

    def fixed(code: str, path: Path, target: str | None = None) -> None:
        item = {"code": code, "path": relative(path)}
        if target is not None:
            item["target"] = target
        fixes.append(item)

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

    for legacy_name in (".agents.config", ".agent-config", ".agent.config"):
        legacy_root = root / legacy_name
        if lexists(legacy_root):
            issue(
                errors,
                "legacy-canonical-root",
                legacy_root,
                "Canonical shared configuration must use .agents-config/.",
            )

    if not canonical_root.exists():
        if args.fix:
            canonical_root.mkdir(parents=True)
            fixed("created-canonical-root", canonical_root)
        else:
            issue(
                errors,
                "missing-canonical-root",
                canonical_root,
                "Shared skill root is missing; run the explicit audit with --fix.",
            )
    elif canonical_root.is_symlink() or not canonical_root.is_dir():
        issue(
            errors,
            "invalid-canonical-root",
            canonical_root,
            "The canonical shared skill root must be a real directory.",
        )

    if canonical_root.is_dir():
        for category in CATEGORIES:
            category_path = canonical_root / category
            if category_path.is_dir() and not category_path.is_symlink():
                continue
            if args.fix and not lexists(category_path):
                category_path.mkdir()
                fixed("created-category", category_path)
            else:
                issue(
                    errors,
                    "missing-category",
                    category_path,
                    "Required type directory is missing or is not a real directory.",
                )

    def migrate_flat_packages(source_root: Path, source_name: str) -> None:
        if not source_root.is_dir() or source_root.is_symlink():
            return
        for source in sorted(source_root.iterdir(), key=lambda path: path.name):
            if source.is_symlink() or not source.is_dir():
                continue
            if not (source / "SKILL.md").is_file():
                if source_root == canonical_root and source.name not in CATEGORIES:
                    issue(
                        errors,
                        "unexpected-flat-entry",
                        source,
                        "The canonical root may contain only type directories or flat skill packages awaiting migration.",
                    )
                continue
            replacement = RENAMED_SKILLS.get(source.name)
            if source_root != canonical_root and replacement and any(
                (canonical_root / kind / replacement).is_dir() for kind in CATEGORIES
            ):
                issue(
                    errors,
                    "project-adapter-collision",
                    source,
                    "Obsolete adapter is a real package directory; preserve it for explicit resolution.",
                )
                continue
            category = category_for(source.name)
            destination = canonical_root / category / source.name
            if not args.fix:
                issue(
                    errors,
                    "uncategorized-skill",
                    source,
                    f"Move this {source_name} package to {relative(destination)}.",
                )
                continue
            if lexists(destination):
                issue(
                    errors,
                    "skill-move-conflict",
                    source,
                    f"Cannot move package because {relative(destination)} already exists.",
                )
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            source.rename(destination)
            fixed("categorized-skill", destination, category)

    if canonical_root.is_dir():
        migrate_flat_packages(canonical_root, "canonical")
        # The built-in creator may place a new real package in Codex's discovery
        # root. Move only real packages; provider symlinks are left in place.
        migrate_flat_packages(root / ".agents" / "skills", "Codex discovery")

    if canonical_root.is_dir():
        for entry in sorted(canonical_root.iterdir(), key=lambda path: path.name):
            if entry.name not in CATEGORIES:
                issue(
                    errors,
                    "unexpected-type",
                    entry,
                    "Only meta, ops, and dev type directories are allowed.",
                )
            elif entry.is_symlink() or not entry.is_dir():
                issue(
                    errors,
                    "invalid-type-directory",
                    entry,
                    "Skill type entries must be real directories.",
                )

    seen_names: dict[str, Path] = {}
    for category in CATEGORIES:
        category_path = canonical_root / category
        if not category_path.is_dir() or category_path.is_symlink():
            continue
        for skill_path in sorted(category_path.iterdir(), key=lambda path: path.name):
            if skill_path.is_symlink() or not skill_path.is_dir():
                issue(
                    errors,
                    "invalid-skill-entry",
                    skill_path,
                    "Canonical skill packages must be real directories.",
                )
                continue
            if skill_path.name in seen_names:
                issue(
                    errors,
                    "duplicate-skill-name",
                    skill_path,
                    f"Skill name is already used by {relative(seen_names[skill_path.name])}.",
                )
            else:
                seen_names[skill_path.name] = skill_path
            if category_for(skill_path.name) != category and skill_path.name in (
                META_SKILLS | OPS_SKILLS
            ):
                issue(
                    errors,
                    "wrong-skill-category",
                    skill_path,
                    f"Known package belongs under {category_for(skill_path.name)}/.",
                )

            skills.append(
                {"name": skill_path.name, "path": skill_path, "category": category}
            )
            if (
                not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", skill_path.name)
                or len(skill_path.name) > 64
            ):
                issue(
                    errors,
                    "invalid-skill-name",
                    skill_path,
                    "Skill folder must be lowercase hyphen-case and at most 64 characters.",
                )

            skill_file = skill_path / "SKILL.md"
            if not skill_file.is_file():
                issue(
                    errors,
                    "missing-skill-file",
                    skill_path,
                    "Canonical package is missing SKILL.md.",
                )
                continue
            parsed = frontmatter(skill_file.read_text(encoding="utf-8"))
            if not parsed or parsed[0] is None:
                issue(
                    errors,
                    "invalid-frontmatter",
                    skill_file,
                    "SKILL.md must start with closed YAML frontmatter.",
                )
                continue
            raw, body = parsed
            declared_name = top_value(raw, "name")
            description = top_value(raw, "description")
            disable_model = top_value(raw, "disable-model-invocation")
            if declared_name != skill_path.name:
                issue(
                    errors,
                    "skill-name-mismatch",
                    skill_file,
                    f"Frontmatter name must be {skill_path.name}.",
                )
            if not description or re.search(r"\bTODO\b", description, re.IGNORECASE):
                issue(
                    errors,
                    "missing-description",
                    skill_file,
                    "Frontmatter description must be complete and non-placeholder.",
                )
            if disable_model not in (None, "true"):
                issue(
                    errors,
                    "invalid-claude-invocation-lock",
                    skill_file,
                    "disable-model-invocation must be omitted or set to true.",
                )
            if re.search(
                r"(?:```(?:powershell|ps1)|\b(?:powershell|pwsh)(?:\.exe)?\s+-|\.ps1\b)",
                body or "",
                re.IGNORECASE,
            ):
                issue(
                    errors,
                    "powershell-skill-instruction",
                    skill_file,
                    "Skill instructions must not depend on PowerShell or .ps1 commands.",
                )

            sidecar = skill_path / "agents" / "openai.yaml"
            implicit_policy = (
                sidecar_implicit_policy(sidecar.read_text(encoding="utf-8"))
                if sidecar.is_file()
                else None
            )
            requires_explicit = skill_path.name in REQUIRED_EXPLICIT_SKILLS
            if requires_explicit and disable_model != "true":
                issue(
                    errors,
                    "missing-claude-invocation-lock",
                    skill_file,
                    "Explicit-only skills require disable-model-invocation: true.",
                )
            if requires_explicit and implicit_policy != "false":
                issue(
                    errors,
                    "missing-openai-invocation-lock",
                    sidecar,
                    "Explicit-only skills require policy.allow_implicit_invocation: false.",
                )
            if (disable_model == "true") != (implicit_policy == "false"):
                issue(
                    errors,
                    "provider-invocation-lock-mismatch",
                    skill_path,
                    "Every skill must use both provider invocation locks or neither lock.",
                )

            for target in markdown_links(body or ""):
                without_anchor = unquote(target.split("#", 1)[0])
                if not without_anchor or re.match(
                    r"^[a-z][a-z0-9+.-]*:", without_anchor, re.IGNORECASE
                ):
                    continue
                resolved = (skill_file.parent / without_anchor).resolve()
                if not resolved.is_relative_to(skill_path.resolve()):
                    issue(
                        errors,
                        "external-skill-link",
                        skill_file,
                        f"Skill instruction link leaves its package: {target}.",
                    )
                elif not resolved.exists():
                    issue(
                        errors,
                        "broken-skill-link",
                        skill_file,
                        f"Skill instruction link does not resolve: {target}.",
                    )

            scripts_directory = skill_path / "scripts"
            if scripts_directory.exists() and not scripts_directory.is_dir():
                issue(
                    errors,
                    "invalid-scripts-directory",
                    scripts_directory,
                    "Skill scripts path must be a directory.",
                )
            elif scripts_directory.is_dir():
                script_files = sorted(
                    path
                    for path in scripts_directory.rglob("*")
                    if path.is_file() and "__pycache__" not in path.parts
                )
                if script_files and "uv run" not in (body or ""):
                    issue(
                        errors,
                        "missing-uv-invocation",
                        skill_file,
                        "Skills with scripts must document invocation through uv run.",
                    )
                for script_file in script_files:
                    if script_file.suffix.lower() != ".py":
                        issue(
                            errors,
                            "non-python-skill-script",
                            script_file,
                            "Skill automation must be a Python .py script executed through uv.",
                        )
                        continue
                    script_content = script_file.read_text(encoding="utf-8")
                    metadata = re.search(
                        r"^# /// script\s*$([\s\S]*?)^# ///\s*$",
                        script_content,
                        re.MULTILINE,
                    )
                    if not metadata or not re.search(
                        r'^# requires-python\s*=\s*["\'][^"\']+["\']\s*$',
                        metadata.group(1),
                        re.MULTILINE,
                    ):
                        issue(
                            errors,
                            "missing-uv-script-metadata",
                            script_file,
                            "Python skill scripts must declare requires-python in uv script metadata.",
                        )

    readme_path = root / "README.md"
    readme_catalog_entries = 0
    if not readme_path.is_file():
        issue(
            errors,
            "missing-readme",
            readme_path,
            "README.md must document the canonical skill catalog.",
        )
    else:
        readme = readme_path.read_text(encoding="utf-8")
        if (
            readme.count(README_CATALOG_START) != 1
            or readme.count(README_CATALOG_END) != 1
        ):
            issue(
                errors,
                "invalid-readme-skill-catalog-markers",
                readme_path,
                "README.md must contain one ordered skills-catalog marker pair.",
            )
        else:
            start = readme.index(README_CATALOG_START) + len(README_CATALOG_START)
            end = readme.index(README_CATALOG_END)
            if start > end:
                issue(
                    errors,
                    "invalid-readme-skill-catalog-order",
                    readme_path,
                    "README.md skill catalog end marker precedes its start marker.",
                )
            else:
                catalog = readme[start:end]
                expected_links = {
                    f".agents-config/skills/{skill['category']}/{skill['name']}/SKILL.md"
                    for skill in skills
                }
                actual_links = re.findall(
                    r"\.agents-config/skills/(?:meta|ops|dev)/[a-z0-9-]+/SKILL\.md",
                    catalog,
                )
                readme_catalog_entries = len(actual_links)
                for expected in sorted(expected_links):
                    count = actual_links.count(expected)
                    if count == 0:
                        issue(
                            errors,
                            "missing-readme-skill",
                            readme_path,
                            f"README.md skill catalog is missing {expected}.",
                        )
                    elif count > 1:
                        issue(
                            errors,
                            "duplicate-readme-skill",
                            readme_path,
                            f"README.md skill catalog lists {expected} {count} times.",
                        )
                for actual in sorted(set(actual_links) - expected_links):
                    issue(
                        errors,
                        "stale-readme-skill",
                        readme_path,
                        f"README.md skill catalog links to non-canonical package {actual}.",
                    )

    def create_symlink(link: Path, target: str, code: str) -> bool:
        try:
            os.symlink(target, link, target_is_directory=True)
        except OSError as error:
            issue(
                errors,
                "symlink-create-failed",
                link,
                f"Could not create symbolic link: {error}",
            )
            return False
        fixed(code, link, target.replace("\\", "/"))
        return True

    valid_project_adapters = 0
    untracked_project_adapters = 0
    canonical_by_name = {str(skill["name"]): Path(skill["path"]) for skill in skills}
    for adapter_relative in PROJECT_ADAPTERS:
        adapter_root = root / adapter_relative
        if not adapter_root.exists():
            if args.fix and not lexists(adapter_root):
                adapter_root.mkdir(parents=True)
                fixed("created-project-adapter-root", adapter_root)
            else:
                issue(
                    errors,
                    "missing-project-adapter-root",
                    adapter_root,
                    "Provider skill discovery directory is missing.",
                )
                continue
        if adapter_root.is_symlink() or not adapter_root.is_dir():
            issue(
                errors,
                "invalid-project-adapter-root",
                adapter_root,
                "Provider skill discovery must be a real directory of flat skill symlinks.",
            )
            continue

        for entry in sorted(adapter_root.iterdir(), key=lambda path: path.name):
            if entry.name not in canonical_by_name:
                replacement = RENAMED_SKILLS.get(entry.name)
                if replacement in canonical_by_name and entry.is_symlink() and args.fix:
                    # Only remove adapters to this worktree's former package;
                    # a same-named link to another destination is a collision.
                    old_target = canonical_root / category_for(entry.name) / entry.name
                    link_target = entry.parent / os.readlink(entry)
                    if comparable_path(link_target) == comparable_path(old_target):
                        entry.unlink()
                        fixed("removed-renamed-project-adapter", entry)
                        continue
                issue(
                    errors,
                    "extra-project-adapter",
                    entry,
                    "Provider adapter has no canonical shared package.",
                )

        for name, skill_path in canonical_by_name.items():
            link = adapter_root / name
            target = os.path.relpath(skill_path, adapter_root)
            if lexists(link) and not link.is_symlink():
                issue(
                    errors,
                    "project-adapter-collision",
                    link,
                    "Provider adapter path is a real file or directory; move it explicitly before repair.",
                )
                continue
            if link.is_symlink():
                try:
                    resolves_correctly = comparable_path(
                        link.resolve(strict=True)
                    ) == comparable_path(skill_path)
                except OSError:
                    resolves_correctly = False
                relative_target = not os.path.isabs(os.readlink(link))
                if (not resolves_correctly or not relative_target) and args.fix:
                    link.unlink()
                    if not create_symlink(link, target, "relinked-project-adapter"):
                        continue
                elif not resolves_correctly or not relative_target:
                    issue(
                        errors,
                        "project-adapter-drift",
                        link,
                        "Provider adapter must be a relative symlink to its matching canonical package.",
                    )
                    continue
            elif args.fix:
                if not create_symlink(link, target, "created-project-adapter"):
                    continue
            else:
                issue(
                    errors,
                    "missing-project-adapter",
                    link,
                    "Provider adapter is missing; run the explicit audit with --fix.",
                )
                continue

            mode = tracked_mode(relative(link))
            if mode and mode != "120000":
                issue(
                    errors,
                    "invalid-project-adapter-mode",
                    link,
                    f"Tracked adapter mode is {mode}; expected 120000.",
                )
                continue
            if not mode:
                untracked_project_adapters += 1
            valid_project_adapters += 1

    valid_global_adapters = 0
    for global_relative in GLOBAL_ADAPTERS if args.global_adapters else ():
        global_root = home / global_relative
        if not global_root.exists():
            if args.fix and not lexists(global_root):
                global_root.mkdir(parents=True)
                fixed("created-global-adapter-root", global_root)
            else:
                issue(
                    errors,
                    "missing-global-adapter-root",
                    global_root,
                    "Global provider skill directory is missing; run the explicit audit with --fix.",
                )
                continue
        if global_root.is_symlink() or not global_root.is_dir():
            issue(
                errors,
                "invalid-global-adapter-root",
                global_root,
                "Global provider skill root must be a real directory.",
            )
            continue

        for entry in sorted(global_root.iterdir(), key=lambda path: path.name):
            if entry.is_symlink() and not entry.exists():
                if args.fix:
                    entry.unlink()
                    fixed("removed-broken-global-link", entry)
                else:
                    issue(
                        errors,
                        "broken-global-link",
                        entry,
                        "Broken global symlink must be removed by the explicit repair run.",
                    )

        for name, skill_path in canonical_by_name.items():
            link = global_root / name
            absolute_target = str(skill_path.resolve(strict=True))
            if lexists(link) and not link.is_symlink():
                issue(
                    errors,
                    "global-adapter-collision",
                    link,
                    "Global adapter path is a real file or directory and will not be overwritten.",
                )
                continue
            if link.is_symlink():
                try:
                    resolves_correctly = comparable_path(
                        link.resolve(strict=True)
                    ) == comparable_path(skill_path)
                except OSError:
                    resolves_correctly = False
                absolute_link = os.path.isabs(os.readlink(link))
                if (not resolves_correctly or not absolute_link) and args.fix:
                    link.unlink()
                    if not create_symlink(
                        link, absolute_target, "relinked-global-adapter"
                    ):
                        continue
                elif not resolves_correctly or not absolute_link:
                    issue(
                        errors,
                        "global-adapter-drift",
                        link,
                        "Global adapter must be an absolute symlink to the canonical package.",
                    )
                    continue
            elif args.fix:
                if not create_symlink(link, absolute_target, "created-global-adapter"):
                    continue
            else:
                issue(
                    errors,
                    "missing-global-adapter",
                    link,
                    "Global flat adapter is missing; run the explicit audit with --fix.",
                )
                continue
            valid_global_adapters += 1

    result = {
        "root": str(root),
        "home": str(home) if home is not None else None,
        "adapterScope": "project-and-global" if args.global_adapters else "project",
        "revision": revision,
        "dirtyAtStart": dirty,
        "mode": "repair" if args.fix else "read-only",
        "summary": {
            "skills": len(skills),
            "meta": sum(skill["category"] == "meta" for skill in skills),
            "ops": sum(skill["category"] == "ops" for skill in skills),
            "dev": sum(skill["category"] == "dev" for skill in skills),
            "projectAdapters": valid_project_adapters,
            "globalAdapters": valid_global_adapters,
            "readmeCatalogEntries": readme_catalog_entries,
            "untrackedProjectAdapters": untracked_project_adapters,
            "fixes": len(fixes),
            "errors": len(errors),
            "warnings": len(warnings),
        },
        "fixes": fixes,
        "errors": errors,
        "warnings": warnings,
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("# Skills audit\n")
        print(f"- Root: `{root}`")
        print(f"- Adapter scope: {result['adapterScope']}")
        if home is not None:
            print(f"- Home: `{home}`")
        print(f"- Revision: `{revision}`")
        print(f"- Dirty at start: `{str(dirty).lower()}`")
        print(f"- Mode: {result['mode']}")
        print(
            f"- Canonical skills: {len(skills)} "
            f"(meta {result['summary']['meta']}, ops {result['summary']['ops']}, dev {result['summary']['dev']})"
        )
        print(f"- Valid project adapters: {valid_project_adapters}")
        print(f"- Valid global adapters: {valid_global_adapters}")
        print(f"- README catalog entries: {readme_catalog_entries}")
        print(f"- Untracked project adapters: {untracked_project_adapters}")
        print(f"- Fixes: {len(fixes)}")
        print(f"- Errors: {len(errors)}")
        print(f"- Warnings: {len(warnings)}\n")
        if fixes:
            print("## Changes\n")
            for change in fixes:
                target = f" -> {change['target']}" if "target" in change else ""
                print(f"- **{change['code']}** `{change['path']}`{target}")
            print()
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
