#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Audit canonical skill packages and repair missing Claude symlink adapters."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote


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


def main() -> int:
    args = sys.argv[1:]
    json_output = "--json" in args
    fix_missing = "--fix" in args
    targets = [arg for arg in args if not arg.startswith("--")]
    if not targets:
        print(
            "Usage: uv run audit_skills.py <repository-root> [--fix] [--json]",
            file=sys.stderr,
        )
        return 2

    root = Path(targets[0]).resolve()
    canonical_root = root / ".agents" / "skills"
    adapter_root = root / ".claude" / "skills"
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    fixes: list[dict[str, str]] = []
    skills: list[dict[str, object]] = []
    valid_adapters = 0
    untracked_adapters = 0

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

    if not canonical_root.is_dir():
        print(
            f"Canonical skills directory is missing: {canonical_root}", file=sys.stderr
        )
        return 2

    try:
        git_root = run_git("rev-parse", "--show-toplevel")
    except (OSError, subprocess.CalledProcessError):
        print(f"Repository root is not a Git worktree: {root}", file=sys.stderr)
        return 2
    if comparable_path(git_root) != comparable_path(root):
        print(f"Expected repository root {git_root}, received {root}.", file=sys.stderr)
        return 2

    for skill_path in sorted(canonical_root.iterdir(), key=lambda path: path.name):
        if skill_path.is_symlink():
            issue(
                errors,
                "canonical-symlink",
                skill_path,
                "Canonical skill package must be a real directory.",
            )
            continue
        if not skill_path.is_dir():
            issue(
                errors,
                "unexpected-canonical-entry",
                skill_path,
                "Canonical root may contain only skill directories.",
            )
            continue

        skill = {"name": skill_path.name, "path": skill_path}
        skills.append(skill)
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
        if re.search(
            r"(?:```(?:powershell|ps1)|\b(?:powershell|pwsh)\b|\.ps1\b)",
            body or "",
            re.IGNORECASE,
        ):
            issue(
                errors,
                "powershell-skill-instruction",
                skill_file,
                "Skill instructions must not depend on PowerShell or .ps1 commands.",
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
                    "Skill packages with scripts must instruct agents to invoke them with uv run.",
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

    if not adapter_root.exists():
        if fix_missing:
            adapter_root.mkdir(parents=True)
            fixes.append(
                {"code": "created-adapter-root", "path": relative(adapter_root)}
            )
        else:
            issue(
                errors,
                "missing-adapter-root",
                adapter_root,
                "Claude skill adapter directory is missing.",
            )
    elif not adapter_root.is_dir():
        issue(
            errors,
            "invalid-adapter-root",
            adapter_root,
            "Claude skill adapter root must be a directory.",
        )

    symlink_setting: bool | None = None

    def can_create_symlinks() -> bool:
        nonlocal symlink_setting
        if symlink_setting is None:
            try:
                symlink_setting = run_git("config", "--bool", "core.symlinks") == "true"
            except (OSError, subprocess.CalledProcessError):
                symlink_setting = False
        return symlink_setting

    if adapter_root.is_dir():
        canonical_names = {str(skill["name"]) for skill in skills}
        for adapter_entry in adapter_root.iterdir():
            if adapter_entry.name not in canonical_names:
                issue(
                    errors,
                    "extra-adapter",
                    adapter_entry,
                    "Adapter has no canonical skill package.",
                )

        for skill in skills:
            skill_name = str(skill["name"])
            skill_path = Path(skill["path"])
            adapter_path = adapter_root / skill_name
            native_target = os.path.relpath(skill_path, adapter_root)
            expected_target = native_target.replace("\\", "/")
            adapter_exists = os.path.lexists(adapter_path)

            if not adapter_exists and fix_missing:
                if not can_create_symlinks():
                    issue(
                        errors,
                        "symlinks-disabled",
                        adapter_path,
                        "Cannot create adapter while git core.symlinks is not true.",
                    )
                    continue
                try:
                    os.symlink(native_target, adapter_path, target_is_directory=True)
                    fixes.append(
                        {
                            "code": "created-adapter",
                            "path": relative(adapter_path),
                            "target": expected_target,
                        }
                    )
                    adapter_exists = True
                except OSError as error:
                    issue(
                        errors,
                        "adapter-create-failed",
                        adapter_path,
                        f"Could not create symbolic link: {error}",
                    )
                    continue

            if not adapter_exists:
                issue(
                    errors,
                    "missing-adapter",
                    adapter_path,
                    f"Missing Claude adapter; run with --fix to create {expected_target}.",
                )
                continue
            if not adapter_path.is_symlink():
                issue(
                    errors,
                    "copied-adapter",
                    adapter_path,
                    "Adapter must be a directory symlink, not a copied file or directory.",
                )
                continue

            link_target = os.readlink(adapter_path).replace("\\", "/").rstrip("/")
            if link_target != expected_target:
                issue(
                    errors,
                    "wrong-adapter-target",
                    adapter_path,
                    f"Adapter target is {link_target}; expected {expected_target}.",
                )
                continue
            try:
                resolved_adapter = adapter_path.resolve(strict=True)
            except OSError:
                issue(
                    errors,
                    "broken-adapter",
                    adapter_path,
                    "Adapter target does not resolve.",
                )
                continue
            if comparable_path(resolved_adapter) != comparable_path(skill_path):
                issue(
                    errors,
                    "adapter-resolution-drift",
                    adapter_path,
                    "Adapter resolves outside its matching canonical package.",
                )
                continue

            repository_path = relative(adapter_path)
            mode = tracked_mode(repository_path)
            if mode and mode != "120000":
                issue(
                    errors,
                    "invalid-git-mode",
                    adapter_path,
                    f"Tracked adapter mode is {mode}; expected 120000.",
                )
                continue
            if not mode:
                untracked_adapters += 1
            valid_adapters += 1

    created_adapters = sum(fix["code"] == "created-adapter" for fix in fixes)
    result = {
        "root": str(root),
        "mode": "fix-missing" if fix_missing else "read-only",
        "summary": {
            "skills": len(skills),
            "adapters": valid_adapters,
            "created": created_adapters,
            "untrackedAdapters": untracked_adapters,
            "errors": len(errors),
            "warnings": len(warnings),
        },
        "fixes": fixes,
        "errors": errors,
        "warnings": warnings,
    }
    if json_output:
        print(json.dumps(result, indent=2))
    else:
        print("# Skills audit\n")
        print(f"- Root: `{root}`")
        print(f"- Mode: {result['mode']}")
        print(f"- Canonical skills: {len(skills)}")
        print(f"- Valid adapters: {valid_adapters}")
        print(f"- Created adapters: {created_adapters}")
        print(f"- Untracked adapters: {untracked_adapters}")
        print(f"- Errors: {len(errors)}")
        print(f"- Warnings: {len(warnings)}\n")
        if fixes:
            print("## Changes\n")
            for fix in fixes:
                target = f" -> {fix['target']}" if "target" in fix else ""
                print(f"- **{fix['code']}** `{fix['path']}`{target}")
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
