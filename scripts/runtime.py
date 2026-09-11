"""Shared worktree, process and environment primitives. Never print environment values."""
from __future__ import annotations
import contextlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
def git(*args, root=ROOT):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()
def executable(name):
    path = shutil.which(name)
    if not path:
        raise RuntimeError(f"Required executable unavailable: {name}")
    return path
def run(args, **kwargs):
    return subprocess.run([executable(args[0]), *map(str, args[1:])], check=True, **kwargs)
def keycloak_module():
    path = ROOT / ".agents-config/skills/ops/keycloak-admin/scripts/keycloak.py"
    spec = importlib.util.spec_from_file_location("keycloak_admin", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module
def env_path(explicit=None):
    value = explicit or os.environ.get("AUTOMATION_ENV_FILE")
    reference = ROOT / ".agent-work/environment-path"
    if not value and reference.exists():
        value = reference.read_text(encoding="utf-8").strip()
    if not value or not Path(value).is_absolute():
        raise RuntimeError("Select an absolute environment path with --env-file or AUTOMATION_ENV_FILE; run agent:setup.")
    path = Path(value).resolve()
    if not path.is_file():
        raise RuntimeError("Selected environment file does not exist.")
    return path
def environment(explicit=None):
    path = env_path(explicit)
    values = keycloak_module().read_env(path)
    return {**os.environ, **values, "AUTOMATION_ENV_FILE": str(path)}
def common_dir(root=ROOT):
    return Path(git("rev-parse", "--path-format=absolute", "--git-common-dir", root=root))
def require_worktree(root=ROOT):
    location = Path(root).resolve()
    gitdir = Path(git("rev-parse", "--absolute-git-dir", root=location))
    if gitdir == common_dir(location):
        raise RuntimeError("Writing agents must use a linked worktree, not the primary checkout.")
    branch = git("branch", "--show-current", root=location)
    if not branch or branch in {"main", "master"}:
        raise RuntimeError("A named feature branch is required.")
    return branch
@contextlib.contextmanager
def exclusive_lock(path, label):
    """Kernel lock releases after a crash. File remains; its existence is not ownership."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = path.open("a+b")
    if path.stat().st_size == 0:
        handle.write(b"0")
        handle.flush()
    handle.seek(0)
    try:
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        handle.close()
        raise RuntimeError(f"{label} is in use by another process; retry after it finishes.") from None
    try:
        yield
    finally:
        handle.seek(0)
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle, fcntl.LOCK_UN)
        handle.close()
def atomic_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".new")
    temp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)

