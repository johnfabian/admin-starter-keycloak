"""Behavioral tests for graph inputs, hooks, ownership, and interprocess locking."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import graph
import runtime
import agent_setup

class Repository(unittest.TestCase):
    def setUp(self):
        # Hooks export repository-local Git variables. Disposable test repositories
        # must never inherit the caller's index, object directory, or worktree.
        local_keys = subprocess.check_output(
            ["git", "rev-parse", "--local-env-vars"], cwd=ROOT, text=True
        ).splitlines()
        clean_env = {key: value for key, value in os.environ.items() if key not in local_keys and not key.startswith("GIT_CONFIG_")}
        clean_env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
        isolated = patch.dict(os.environ, clean_env, clear=True)
        isolated.start()
        self.addCleanup(isolated.stop)
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        template = self.root / ".empty-template"
        template.mkdir()
        subprocess.run(["git", "init", "-q", f"--template={template}", str(self.root)], check=True)
        hooks = self.root / ".git/hooks"
        hooks.mkdir()
        subprocess.run(["git", "-C", str(self.root), "config", "core.hooksPath", str(hooks)], check=True)
        subprocess.run(["git", "-C", str(self.root), "config", "core.autocrlf", "false"], check=True)
        for name in ["graphify.config.json", "pyproject.toml", "uv.lock", "scripts/graph.py"]:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / name).read_bytes())
        (self.root / ".gitignore").write_text(".env*\n.agent-work/\ngraphify-out/\n")
    def tearDown(self):
        self.temp.cleanup()
    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args])
    def test_add_delete_rename_and_partial_stage(self):
        p = self.root / "module.py"
        p.write_text("value = 1\n", newline="\n")
        self.git("add", ".")
        p.write_text("value = 2\n", newline="\n")
        self.assertEqual(graph.inventory(self.root, True)["module.py"], b"value = 1\n")
        self.assertEqual(graph.inventory(self.root)["module.py"], b"value = 2\n")
        self.git("mv", "module.py", "renamed.py")
        self.assertNotIn("module.py", graph.inventory(self.root, True))
        self.assertIn("renamed.py", graph.inventory(self.root, True))
        self.git("rm", "-f", "renamed.py")
        self.assertNotIn("renamed.py", graph.inventory(self.root, True))
    def test_secrets_dependencies_and_symlinks_excluded(self):
        for name in [".env.local", "node_modules/pkg/secret.py", ".agent-work/fixture.py"]:
            p = self.root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("SECRET_SENTINEL")
        (self.root / "normal.py").write_text("pass")
        self.assertEqual(set(graph.inventory(self.root)) - {"scripts/graph.py"}, {"normal.py"})
    def test_exclusion_change_invalidates_signature(self):
        before = graph.signature(graph.inventory(self.root), self.root)
        cfg = json.loads((self.root / "graphify.config.json").read_text())
        cfg["extensions"].remove(".py")
        (self.root / "graphify.config.json").write_text(json.dumps(cfg))
        self.assertNotEqual(before, graph.signature(graph.inventory(self.root), self.root))
    def test_failed_extraction_preserves_previous_graph(self):
        out = self.root / "graphify-out"
        out.mkdir()
        (out / "graph.json").write_text('{"nodes":[{"id":"previous"}]}')
        original = (out / "graph.json").read_bytes()
        with patch.object(graph, "run", side_effect=RuntimeError("extract failed")):
            with self.assertRaises(RuntimeError):
                graph.build(self.root, force=True)
        self.assertEqual(original, (out / "graph.json").read_bytes())
        self.assertFalse((out / "manifest.json").exists())
    def test_customized_managed_hook_is_preserved(self):
        agent_setup.install_hook(self.root)
        hook = self.root / ".git/hooks/pre-commit"
        with hook.open("a") as handle:
            handle.write("echo custom-security-check\n")
        before = hook.read_bytes()
        with self.assertRaisesRegex(RuntimeError, "preserved"):
            agent_setup.install_hook(self.root)
        self.assertEqual(before, hook.read_bytes())

    def test_symlink_source_is_not_followed(self):
        target = self.root.parent / (self.root.name + "-private.py")
        target.write_text("PRIVATE_SENTINEL")
        try:
            (self.root / "linked.py").symlink_to(target)
            self.assertNotIn("linked.py", graph.inventory(self.root))
        finally:
            target.unlink()

    def test_linked_worktrees_keep_independent_graphs(self):
        self.git("add", ".")
        self.git("-c", "user.name=Automation Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture", "--no-verify")
        one, two = self.root / "one", self.root / "two"
        self.git("worktree", "add", "-qb", "fixture-one", str(one))
        self.git("worktree", "add", "-qb", "fixture-two", str(two))
        self.assertEqual(runtime.common_dir(one), runtime.common_dir(two))
        self.assertEqual(runtime.require_worktree(one), "fixture-one")
        def extract(args, cwd, env):
            output = Path(env["GRAPHIFY_OUT"])
            output.mkdir(parents=True)
            (output / "graph.json").write_text(json.dumps({"nodes": [{"id": str(cwd), "source_file": "scripts/graph.py"}], "edges": []}))
        with patch.object(graph, "run", side_effect=extract):
            graph.build(one)
            original = (one / "graphify-out/graph.json").read_bytes()
            self.assertFalse((two / "graphify-out").exists())
            graph.build(two)
            self.assertEqual(original, (one / "graphify-out/graph.json").read_bytes())
            self.assertNotEqual(original, (two / "graphify-out/graph.json").read_bytes())

    def test_corrupt_graph_is_not_fresh(self):
        out = self.root / "graphify-out"
        out.mkdir()
        file = out / "graph.json"
        file.write_text('{"nodes":[{"id":"valid"}]}')
        expected = graph.signature(graph.inventory(self.root), self.root)
        runtime.atomic_json(out / "manifest.json", {"input": expected, "graphSha256": graph.digest(file.read_bytes())})
        self.assertTrue(graph.fresh(out, expected))
        file.write_text("corrupt")
        self.assertFalse(graph.fresh(out, expected))

    def test_unmerged_index_is_rejected(self):
        blob = subprocess.check_output(["git", "-C", str(self.root), "hash-object", "-w", "--stdin"], input=b"pass").decode().strip()
        # A conflict on any staged source must be resolved, not guessed.
        raw = f"100644 {blob} 1\tconflict.py\0".encode()
        with patch.object(graph, "config", return_value=json.loads((self.root / "graphify.config.json").read_text())), patch.object(graph.subprocess, "check_output", return_value=raw):
            with self.assertRaisesRegex(RuntimeError, "conflicts"):
                graph.inventory(self.root, True)
    def test_existing_hook_is_preserved(self):
        hook = self.root / ".git/hooks/pre-commit"
        hook.write_text("#!/bin/sh\necho user-owned\n")
        before = hook.read_bytes()
        with self.assertRaisesRegex(RuntimeError, "preserved"):
            agent_setup.install_hook(self.root)
        self.assertEqual(before, hook.read_bytes())
    def test_primary_checkout_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "primary"):
            runtime.require_worktree(self.root)
    def test_staged_inventory_does_not_change_index(self):
        (self.root / "test.py").write_text("x=1")
        self.git("add", ".")
        before = (self.root / ".git/index").read_bytes()
        graph.inventory(self.root, True)
        self.assertEqual(before, (self.root / ".git/index").read_bytes())

class Locking(unittest.TestCase):
    def test_other_process_is_excluded_and_lock_recovers(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "shared.lock"
            script = "import sys;sys.path.insert(0,sys.argv[1]);from runtime import exclusive_lock\nwith exclusive_lock(sys.argv[2],'stack'): print('acquired')"
            with runtime.exclusive_lock(path, "stack"):
                result = subprocess.run([sys.executable, "-c", script, str(ROOT / "scripts"), str(path)], capture_output=True)
                self.assertNotEqual(result.returncode, 0)
            result = subprocess.run([sys.executable, "-c", script, str(ROOT / "scripts"), str(path)], capture_output=True)
            self.assertEqual(result.returncode, 0)

class BrowserBoundary(unittest.TestCase):
    def test_remote_identity_rejected_before_credentials_or_fixtures(self):
        import e2e
        from types import SimpleNamespace
        for issuer, server in [("https://identity.example/realms/test", "http://localhost:8080"), ("http://localhost:8080/realms/test", "https://identity.example")]:
            with self.assertRaisesRegex(RuntimeError, "local"):
                e2e.require_local_identity(SimpleNamespace(issuer=issuer, server=server))
    def test_shutdown_failure_still_cleans_artifacts_and_owned_fixtures(self):
        import e2e
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            (base / "results").mkdir()
            (base / "results/error-context.md").write_text("PRIVATE_SENTINEL")
            manifest = base / "fixtures.json"
            manifest.write_text("{}")
            calls = []
            module = SimpleNamespace(read_manifest=lambda *args: (manifest, {}), cleanup_fixtures=lambda *args: calls.append("keycloak"))
            with patch.object(e2e, "stop_owned", side_effect=RuntimeError()), patch.object(e2e, "cleanup_database", side_effect=lambda *args: calls.append("database")), patch.object(e2e, "cleanup_mail", side_effect=lambda *args: calls.append("mail")):
                with self.assertRaisesRegex(RuntimeError, "shutdown"):
                    e2e.finish_run(object(), base, manifest, None, module, {}, "http://localhost:8025")
            self.assertEqual(calls, ["database", "mail", "keycloak"])
            self.assertFalse((base / "results").exists())
    def test_occupied_port_is_never_reused(self):
        import e2e, socket
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            sock.listen()
            with self.assertRaisesRegex(RuntimeError, "occupied"):
                e2e.assert_available("127.0.0.1", sock.getsockname()[1])

if __name__ == "__main__":
    unittest.main()

