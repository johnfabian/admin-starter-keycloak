# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Own one local server/test run and serialize the shared realm across worktrees."""
from __future__ import annotations
import argparse
import sys
import contextlib
import json
import os
from pathlib import Path
import re
import secrets
import socket
import subprocess
import time
import urllib.request
from urllib.parse import urlparse
from runtime import ROOT, common_dir, environment, env_path, executable, exclusive_lock, keycloak_module, require_worktree, run

def assert_available(host, port):
    for family, _, _, _, address in socket.getaddrinfo(host, port, type=socket.SOCK_STREAM):
        with socket.socket(family, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.3)
            if sock.connect_ex(address) == 0:
                raise RuntimeError(f"App port {port} is already occupied. Stop its owning session explicitly; this runner will not reuse or terminate it.")
def wait_owned(proc, base, nonce):
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise RuntimeError("Owned app server exited during startup; no other server was reused.")
        try:
            with urllib.request.urlopen(base + "/__automation/owner", timeout=1) as response:
                if response.headers.get("X-Automation-Owner") == nonce:
                    return
                raise RuntimeError("Server ownership response did not match this run.")
        except (OSError, TimeoutError):
            time.sleep(0.2)
    raise RuntimeError("Owned app server did not become ready within 60 seconds.")
def stop_owned(proc):
    if proc.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    else:
        import signal
        os.killpg(proc.pid, signal.SIGTERM)
    proc.wait(timeout=15)
def require_local_identity(config):
    for value in (config.issuer, config.server):
        parsed = urlparse(value)
        if parsed.scheme != "http" or parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
            raise RuntimeError("Browser fixtures require local direct-mode Keycloak issuer and admin endpoints.")
def cleanup_database(kc, module, manifest_path, env):
    _, manifest = module.read_manifest(kc, manifest_path)
    ids = []
    for record in [*manifest["users"].values(), manifest["registration"]]:
        user = module.verify_owned(kc, manifest, record)
        if user:
            identifier = user["id"]
            if not re.fullmatch(r"[0-9a-fA-F-]{36}", identifier):
                raise RuntimeError("Unexpected fixture ID format; BFF cleanup refused.")
            ids.append(identifier)
    if not ids:
        return
    dburl = urlparse(env["WEB_DATABASE_URL"])
    db = dburl.path.lstrip("/")
    if db != env.get("POSTGRES_DB"):
        raise RuntimeError("BFF database target differs from selected local Postgres database; cleanup refused.")
    sql = "DELETE FROM web_bff_sessions WHERE user_id IN (" + ",".join("'" + item + "'" for item in ids) + ");"
    result = subprocess.run(["docker", "exec", "-i", env.get("E2E_POSTGRES_CONTAINER", "app-postgres"), "psql",
        "-U", env["POSTGRES_USER"], "-d", db, "-v", "ON_ERROR_STOP=1", "-c", sql],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if result.returncode:
        raise RuntimeError("Scoped BFF fixture cleanup failed; recovery manifest retained.")
def cleanup_mail(manifest, mail_url):
    # Search only unique synthetic recipients; never delete the entire inbox.
    from urllib.parse import urlencode
    recipients = {x["email"] for x in [*manifest["users"].values(), manifest["registration"]]}
    for email in recipients:
        query = urlencode({"query": "to:" + email})
        with urllib.request.urlopen(mail_url + "/api/v1/search?" + query, timeout=5) as response:
            messages = json.load(response).get("messages", [])
        for message in messages:
            actual = {recipient.get("Address") for recipient in message.get("To", [])}
            if actual != {email}:
                continue
            request = urllib.request.Request(mail_url + "/api/v1/messages",
                data=json.dumps({"IDs": [message["ID"]]}).encode(), headers={"Content-Type":"application/json"}, method="DELETE")
            with urllib.request.urlopen(request, timeout=5):
                pass
def finish_run(proc, folder, path, kc, module, env, mail):
    failures = []
    if proc:
        try:
            stop_owned(proc)
        except Exception:
            failures.append("owned-server shutdown")
    # Artifact cleanup must run even when termination fails.
    try:
        import shutil
        raw_results = folder / "results"
        if raw_results.is_dir():
            shutil.rmtree(raw_results)
    except Exception:
        failures.append("private raw-artifact removal")
    if path.exists():
        try:
            _, manifest = module.read_manifest(kc, path)
            cleanup_database(kc, module, path, env)
            cleanup_mail(manifest, mail)
            module.cleanup_fixtures(kc, path)
            print("Fixture cleanup completed; exact run recovery record retained.")
        except Exception:
            # Keep Keycloak ownership when dependent cleanup fails so recovery can verify it.
            failures.append("fixture cleanup")
    if failures:
        raise RuntimeError("Cleanup incomplete: " + ", ".join(failures) + ". Exact recovery manifest retained.")
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--env-file")
    p.add_argument("--ui", action="store_true")
    p.add_argument("--public-only", action="store_true", help="Run only anonymous browser checks without administrator authentication.")
    p.add_argument("--cleanup", help="Recover one exact fixture manifest after an interrupted run.")
    args = p.parse_args([a for a in sys.argv[1:] if a != '--'])
    require_worktree()
    env = environment(args.env_file)
    base = env["APP_EXTERNAL_URL"].rstrip("/")
    parsed = urlparse(base)
    if parsed.scheme != "http" or parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
        raise RuntimeError("Browser fixture runner requires the selected direct local HTTP stack.")
    if urlparse(env["WEB_AUTH_REDIRECT_URI"]).netloc != parsed.netloc:
        raise RuntimeError("App and callback origins must match; propose the exact client repair instead of changing it.")
    module = keycloak_module()
    config = module.load_config(env_path(args.env_file))
    require_local_identity(config)
    mail = env.get("MAILPIT_URL", "http://localhost:8025").rstrip("/")
    if urlparse(mail).hostname not in {"localhost", "127.0.0.1", "::1"}:
        raise RuntimeError("Mail fixture access must target local Mailpit.")
    with exclusive_lock(common_dir() / "automation/local-stack.lock", "Shared local browser-test stack"):
        with (contextlib.nullcontext(None) if args.public_only else module.Keycloak(config)) as kc:
            if args.cleanup and args.public_only:
                raise RuntimeError("Cleanup cannot be combined with public-only scope.")
            if args.cleanup:
                path = Path(args.cleanup).resolve()
                _, manifest = module.read_manifest(kc, path)
                cleanup_database(kc, module, path, env)
                cleanup_mail(manifest, mail)
                module.cleanup_fixtures(kc, path)
                print("Recovery cleanup completed.")
                return
            preflight = {"ok": True} if args.public_only else module.doctor(kc)
            if not preflight["ok"]:
                print(json.dumps(preflight))
                raise RuntimeError("Realm prerequisites need the reported repairs; no existing configuration changed.")
            assert_available(parsed.hostname, parsed.port or 80)
            folder = ROOT / ".agent-work/browser-runs" / secrets.token_hex(12)
            folder.mkdir(parents=True)
            module.protect(folder)
            path = folder / "fixtures.json"
            proc = None
            run_error = None
            try:
                if not args.public_only:
                    module.create_fixtures(kc, path, [
                        {"key": "noRole", "role": "none"}, {"key": "users", "role": "Users"},
                        {"key": "admins", "role": "Admins"}, {"key": "logout", "role": "Users"},
                        {"key": "reset", "role": "Users"}])
                nonce = secrets.token_hex(24)
                env.update(PW_BASE_URL=base, PW_SERVER_NONCE=nonce, PW_FIXTURE_MANIFEST=str(path),
                    PW_MAILPIT_URL=mail, PW_RUN_DIR=str(folder), PYTHONUTF8="1")
                proc = subprocess.Popen([executable("node"), str(ROOT / "web/node_modules/@react-router/dev/bin.js"),
                    "dev", "--host", parsed.hostname, "--port", str(parsed.port or 80), "--strictPort"],
                    cwd=ROOT / "web", env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0, start_new_session=os.name != "nt")
                wait_owned(proc, base, nonce)
                command = ["corepack", "pnpm", "exec", "playwright", "test"]
                if args.ui:
                    command.append("--ui")
                if args.public_only:
                    print("Public-only scope: authenticated and role tests are not run.")
                    command.extend(["--grep", "public splash|anonymous protected routes|logout origin checks"])
                run(command, cwd=ROOT / "tests/browser", env=env)
            except BaseException as exc:
                run_error = exc
            finally:
                finish_run(proc, folder, path, kc, module, env, mail)
            if run_error:
                raise run_error
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Run interrupted; use the exact recovery manifest if cleanup did not finish.")
        raise SystemExit(130)
    except Exception as exc:
        if isinstance(exc, RuntimeError):
            print(str(exc))
        else:
            print(f"Browser run failed ({type(exc).__name__}); inspect sanitized report and recovery manifest.")
        raise SystemExit(1)

