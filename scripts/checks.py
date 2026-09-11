# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Fast validation and complete local story verification."""
import argparse
from runtime import ROOT, run
p = argparse.ArgumentParser()
p.add_argument("mode", choices=["fast", "story"])
a = p.parse_args()
commands = [
    ["corepack", "pnpm", "check"],
    ["uv", "run", "--no-project", "python", "-m", "unittest", "discover", "-s", "tests/tooling", "-v"],
    ["corepack", "pnpm", "--dir", "tests/browser", "typecheck"],
]
if a.mode == "story":
    commands += [
        ["corepack", "pnpm", "web:build"],
        ["corepack", "pnpm", "graph:update"],
        ["corepack", "pnpm", "graph:check"],
        ["corepack", "pnpm", "test:e2e"],
        ["corepack", "pnpm", "test:e2e"],
    ]
try:
    for command in commands:
        run(command, cwd=ROOT)
except Exception:
    raise SystemExit(1)

