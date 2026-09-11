# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Prepare a linked worktree; never copy environment values or overwrite another hook."""
import argparse
import sys
import os
from pathlib import Path
import shlex
from runtime import ROOT, env_path, executable, git, require_worktree, run

MARKER = "# admin-starter automation hook v1"
def install_hook(root=ROOT):
    # Git resolves hooksPath and worktree/common-dir details for us.
    hooks = Path(git("rev-parse", "--path-format=absolute", "--git-path", "hooks", root=root))
    hooks.mkdir(parents=True, exist_ok=True)
    hook = hooks / "pre-commit"
    content = "#!/bin/sh\n" + MARKER + "\nexec " + shlex.quote(executable("uv").replace("\\", "/")) + " run --no-project python scripts/pre_commit.py\n"
    if hook.is_symlink() or (hook.exists() and hook.read_text(encoding="utf-8").replace("\r\n", "\n") != content):
        raise RuntimeError("Existing pre-commit hook preserved; integrate the automation command explicitly before installing.")
    hook.write_text(content, encoding="utf-8", newline="\n")
    hook.chmod(hook.stat().st_mode | 0o111)
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--skip-install", action="store_true")
    args = parser.parse_args([a for a in sys.argv[1:] if a != '--'])
    branch = require_worktree()
    selected = env_path(args.env_file)
    if args.check:
        run(["uv", "run", "--no-project", "python", "scripts/graph.py", "check"])
        print(f"Worktree preflight passed: {branch}")
        return
    reference = ROOT / ".agent-work/environment-path"
    reference.parent.mkdir(parents=True, exist_ok=True)
    reference.write_text(str(selected) + "\n", encoding="utf-8")
    install_hook()
    if not args.skip_install:
        run(["corepack", "pnpm", "install", "--frozen-lockfile"], cwd=ROOT)
        run(["corepack", "pnpm", "install", "--frozen-lockfile"], cwd=ROOT / "tests/browser")
        run(["uv", "sync", "--locked"], cwd=ROOT)
        run(["corepack", "pnpm", "exec", "playwright", "install", "chromium"], cwd=ROOT / "tests/browser")
    run(["uv", "run", "--no-project", "python", "scripts/graph.py", "build"], cwd=ROOT)
    print(f"Worktree ready: {branch}; environment referenced without copying.")
if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(str(exc))
        raise SystemExit(1)

