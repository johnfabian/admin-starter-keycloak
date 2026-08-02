#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Generate a read-only Markdown inventory of a Git repository."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path, PurePosixPath


def run_git(root: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"
    return result.stdout.strip()


def repository_files(root: Path) -> list[str]:
    output = run_git(
        root,
        "ls-files",
        "-z",
        "--cached",
        "--others",
        "--exclude-standard",
    )
    if output == "unavailable":
        return []
    return sorted(path for path in output.split("\0") if path)


def selected(files: list[str], predicate: Callable[[str], bool]) -> list[str]:
    return [path for path in files if predicate(path)]


def markdown_list(values: list[str], empty: str = "None found") -> list[str]:
    return [f"- `{value}`" for value in values] if values else [f"- {empty}"]


def package_summary(root: Path, manifest: str) -> str:
    try:
        package = json.loads((root / manifest).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return f"{manifest} (unreadable JSON)"
    scripts = package.get("scripts", {})
    names = sorted(scripts) if isinstance(scripts, dict) else []
    suffix = f"; scripts: {', '.join(names)}" if names else ""
    return f"{manifest}{suffix}"


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    if not root.is_dir():
        print(f"Repository root does not exist: {root}", file=sys.stderr)
        return 2

    files = repository_files(root)
    top_level = sorted({path.split("/", 1)[0] for path in files})
    manifests = selected(files, lambda path: PurePosixPath(path).name == "package.json")
    ci_files = selected(
        files,
        lambda path: (
            path.startswith(".github/workflows/")
            or PurePosixPath(path).name
            in {
                ".gitlab-ci.yml",
                "azure-pipelines.yml",
                "Jenkinsfile",
                "bitbucket-pipelines.yml",
            }
        ),
    )
    test_files = selected(
        files,
        lambda path: (
            not path.startswith("specs/plans/")
            and bool(
                re.search(
                    r"(^|/)(__tests__|tests?|spec)(/|$)|\.(test|spec)\.[^/]+$",
                    path,
                    re.IGNORECASE,
                )
            )
        ),
    )
    tooling_files = selected(
        files,
        lambda path: (
            PurePosixPath(path).name
            in {
                "biome.json",
                "biome.jsonc",
                "eslint.config.js",
                "eslint.config.mjs",
                "eslint.config.cjs",
                ".eslintrc",
                ".eslintrc.js",
                ".eslintrc.json",
                "prettier.config.js",
                "prettier.config.mjs",
                "prettier.config.cjs",
                ".prettierrc",
                ".prettierrc.json",
                "tsconfig.json",
                "pyproject.toml",
                "ruff.toml",
                "pytest.ini",
                "vitest.config.js",
                "vitest.config.ts",
                "jest.config.js",
                "jest.config.ts",
            }
        ),
    )
    agent_files = selected(
        files,
        lambda path: (
            path in {"AGENTS.md", "CLAUDE.md"}
            or path.startswith((".agents.config/", ".agents/", ".claude/"))
        ),
    )
    deployment_files = selected(
        files,
        lambda path: (
            PurePosixPath(path).name.startswith(("docker-compose", "compose."))
            or PurePosixPath(path).name in {"Dockerfile", "Containerfile"}
            or path.startswith((".devcontainer/", "k8s/", "helm/"))
        ),
    )
    schema_files = selected(
        files,
        lambda path: (
            PurePosixPath(path).suffix.lower()
            in {".sql", ".prisma", ".graphql", ".gql"}
            or "migration" in path.lower()
        ),
    )

    branch = run_git(root, "branch", "--show-current") or "detached"
    head = run_git(root, "rev-parse", "HEAD")
    status = run_git(root, "status", "--short")
    worktree = run_git(root, "rev-parse", "--show-toplevel")

    output = [
        "# Repository inventory",
        "",
        "## Git state",
        "",
        f"- Root: `{root}`",
        f"- Git top level: `{worktree}`",
        f"- Branch: `{branch}`",
        f"- Revision: `{head}`",
        f"- Worktree status: `{status or 'clean'}`",
        "",
        "## Top-level entries",
        "",
        *markdown_list(top_level),
        "",
        "## Package manifests and scripts",
        "",
        *markdown_list([package_summary(root, path) for path in manifests]),
        "",
        "## CI configuration",
        "",
        *markdown_list(ci_files),
        "",
        "## Test candidates",
        "",
        *markdown_list(test_files),
        "",
        "## Formatter, linter, type-check, and test configuration",
        "",
        *markdown_list(tooling_files),
        "",
        "## Agent configuration",
        "",
        *markdown_list(agent_files),
        "",
        "## Deployment and container configuration",
        "",
        *markdown_list(deployment_files),
        "",
        "## Schema and migration assets",
        "",
        *markdown_list(schema_files),
        "",
        "## Uncertainties",
        "",
        "- File discovery uses Git's tracked and non-ignored untracked set; ignored local assets are not inventoried.",
        "- Candidate tests are name-based and require manual confirmation before claiming test coverage.",
        "- Runtime behavior and external service state are not inferred from file presence.",
    ]
    print("\n".join(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
