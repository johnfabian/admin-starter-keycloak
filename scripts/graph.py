# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build branch-local Graphify indexes from an explicit, secret-free source inventory."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import tempfile
from runtime import ROOT, atomic_json, exclusive_lock, run

def digest(data):
    return hashlib.sha256(data).hexdigest()
def control(root, name, staged=False):
    if staged:
        return subprocess.check_output(["git", "-C", str(root), "show", ":" + name], stderr=subprocess.DEVNULL)
    return (root / name).read_bytes()
def config(root, staged=False):
    return json.loads(control(root, "graphify.config.json", staged))
def allowed(name, settings):
    path = PurePosixPath(name)
    return (not path.is_absolute() and ".." not in path.parts
        and not any(p in settings["excludeDirectories"] or p.startswith(".env") for p in path.parts)
        and path.name not in settings["excludeFiles"]
        and path.suffix in settings["extensions"])
def inventory(root=ROOT, staged=False):
    settings = config(root, staged)
    if staged:
        raw = subprocess.check_output(["git", "-C", str(root), "ls-files", "--stage", "-z"])
        entries = {}
        for item in raw.split(b"\0"):
            if not item:
                continue
            header, rawname = item.split(b"\t", 1)
            mode, blob, stage = header.decode().split()
            name = rawname.decode("utf-8")
            if stage != "0":
                raise RuntimeError("Resolve index conflicts before building the staged graph.")
            if mode in {"100644", "100755"} and allowed(name, settings):
                entries[name] = subprocess.check_output(["git", "-C", str(root), "cat-file", "blob", blob])
    else:
        raw = subprocess.check_output(["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard"])
        entries = {}
        for name in sorted(set(raw.decode("utf-8").split("\0")) - {""}):
            if not allowed(name, settings):
                continue
            path = root / name
            if not path.is_file():
                continue
            if any(p.is_symlink() for p in [path, *path.parents] if p != root.parent):
                continue
            if not path.resolve().is_relative_to(root.resolve()):
                continue
            entries[name] = path.read_bytes()
    oversized = [name for name, data in entries.items() if len(data) > settings["maxFileBytes"]]
    if oversized:
        raise RuntimeError("Graph source exceeds configured size limit: " + ", ".join(oversized))
    return entries
def signature(entries, root=ROOT, staged=False):
    controls = {}
    for name in ["graphify.config.json", "pyproject.toml", "uv.lock", "scripts/graph.py"]:
        controls[name] = digest(control(root, name, staged))
    return {"schema": 1, "tool": "graphifyy==0.9.58", "controls": controls,
            "sources": {name: digest(data) for name, data in sorted(entries.items())}}
def destination(root, staged):
    return root / (".agent-work/graph-index" if staged else "graphify-out")
def fresh(out, expected):
    try:
        record = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
        return record["input"] == expected and record["graphSha256"] == digest((out / "graph.json").read_bytes())
    except (OSError, ValueError, KeyError):
        return False
def build(root=ROOT, staged=False, force=False):
    entries = inventory(root, staged)
    if staged:
        for name in ["graphify.config.json", "pyproject.toml", "uv.lock", "scripts/graph.py"]:
            if control(root, name, True) != control(root, name):
                raise RuntimeError("Stage the tooling configuration changes fully before the graph gate: " + name)
    expected = signature(entries, root, staged)
    out = destination(root, staged)
    if not force and fresh(out, expected):
        print(f"Graph current ({len(entries)} sources).")
        return
    if not entries:
        raise RuntimeError("No supported source files; refusing to publish an empty graph.")
    scratch = root / ".agent-work"
    scratch.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="graph-build-", dir=scratch) as folder:
        base = Path(folder)
        corpus, generated = base / "source", base / "output"
        corpus.mkdir()
        for name, data in entries.items():
            target = corpus / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        # Only the explicit corpus is visible to Graphify; no inherited API backend keys.
        env = {k: v for k, v in os.environ.items() if not any(s in k for s in ("API_KEY", "TOKEN", "PASSWORD", "SECRET"))}
        env.update(GRAPHIFY_OUT=str(generated), GRAPHIFY_NO_TIPS="1", PYTHONUTF8="1")
        run(["uv", "run", "--locked", "graphify", "update", str(corpus), "--force", "--no-cluster"], cwd=root, env=env)
        graph_file = generated / "graph.json"
        graph = json.loads(graph_file.read_text(encoding="utf-8"))
        if not graph.get("nodes"):
            raise RuntimeError("Graphify produced no nodes; previous graph preserved.")
        covered = {str(n.get("source_file", n.get("file", ""))).replace("\\", "/") for n in graph["nodes"]}
        unsupported = sorted(name for name in entries if name not in covered)
        if signature(inventory(root, staged), root, staged) != expected:
            raise RuntimeError("Sources changed during extraction; retry before publishing.")
        out.mkdir(parents=True, exist_ok=True)
        for name in ["graph.json", "graph.html", "GRAPH_REPORT.md"]:
            source = generated / name
            if source.exists():
                os.replace(source, out / name)
        atomic_json(out / "coverage.json", {"inputFiles": len(entries), "filesWithoutNodes": unsupported, "note": "No node does not prove no behavior; inspect these sources directly."})
        atomic_json(out / "manifest.json", {"input": expected, "graphSha256": digest((out / "graph.json").read_bytes())})
        print(f"Graph built: {len(entries)} source files, {len(graph['nodes'])} nodes; coverage.json lists extraction gaps.")
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["build", "update", "check", "query"])
    parser.add_argument("question", nargs="?")
    parser.add_argument("--staged", action="store_true")
    args = parser.parse_args()
    with exclusive_lock(ROOT / ".agent-work/graph.lock", "This worktree's graph"):
        out = destination(ROOT, args.staged)
        if args.action == "check":
            if not fresh(out, signature(inventory(ROOT, args.staged), ROOT, args.staged)):
                raise RuntimeError("Graph missing or stale. Run graph:update.")
            print("Graph freshness verified.")
        else:
            build(staged=args.staged, force=args.action == "build")
            if args.action == "query":
                if not args.question:
                    parser.error("query requires a question")
                run(["uv", "run", "--locked", "graphify", "query", args.question], cwd=ROOT,
                    env={**os.environ, "GRAPHIFY_OUT": str(out)})
                # Query resolution may enrich inferred edges in the pinned engine.
                current = signature(inventory(ROOT, args.staged), ROOT, args.staged)
                previous = json.loads((out / "manifest.json").read_text(encoding="utf-8"))["input"]
                if current != previous:
                    raise RuntimeError("Sources changed during query; refresh before using its result.")
                atomic_json(out / "manifest.json", {"input": current, "graphSha256": digest((out / "graph.json").read_bytes())})
if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Graph operation failed: {exc}")
        raise SystemExit(1)

