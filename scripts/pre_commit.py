# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate staged graph input without staging or rewriting user files."""
from runtime import ROOT, require_worktree, run
try:
    require_worktree()
    run(["uv", "run", "--no-project", "python", "scripts/graph.py", "update", "--staged"], cwd=ROOT)
    run(["uv", "run", "--no-project", "python", "scripts/graph.py", "check", "--staged"], cwd=ROOT)
    run(["corepack", "pnpm", "test:fast"], cwd=ROOT)
except Exception as exc:
    print(f"Pre-commit verification failed ({type(exc).__name__}); no files were staged.")
    raise SystemExit(1)

