# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Realm-scoped kcadm transport and recoverable synthetic browser-test accounts."""
from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from urllib.parse import unquote, urlsplit


class KeycloakError(RuntimeError):
    """Safe, deliberately non-verbatim failure suitable for automation output."""


def read_env(path: str | Path) -> dict[str, str]:
    """Read literal dotenv values. Never execute or interpolate environment content."""
    source = Path(path)
    if not source.is_absolute():
        raise KeycloakError("Environment file must be an explicit absolute path.")
    result = {}
    try:
        lines = source.read_text(encoding="utf-8-sig").splitlines()
    except OSError:
        raise KeycloakError("Cannot read the selected environment file.") from None
    for number, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:]
        match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)", line)
        if not match:
            raise KeycloakError(f"Invalid dotenv syntax on line {number}.")
        key, value = match.groups()
        if value.startswith(("'", '"')):
            quote = value[0]
            close = value.find(quote, 1)
            if close < 0 or (value[close + 1:].strip() and not value[close + 1:].strip().startswith("#")):
                raise KeycloakError(f"Invalid quoted dotenv value on line {number}.")
            value = value[1:close]
        else:
            value = re.split(r"\s+#", value, maxsplit=1)[0].rstrip()
        result[key] = value
    return result


def identifier(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.@-]{0,199}", value) or value in {".", ".."}:
        raise KeycloakError("Invalid realm, resource, or fixture identifier.")
    return value


def url(value: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise KeycloakError("Expected an HTTP(S) URL without credentials, query, or fragment.")
    if any(c in value for c in "\r\n\x00"):
        raise KeycloakError("Invalid URL.")
    return value.rstrip("/")


@dataclass(frozen=True)
class Config:
    realm: str
    issuer: str
    server: str
    admin_realm: str
    admin_user: str
    admin_password: str = field(repr=False)
    client_id: str = ""
    app_url: str = "http://localhost:5173"
    container: str = "app-keycloak"
    cli: str | None = None
    cli_version: str | None = None
    confidential: bool = False


def load_config(path: str | Path) -> Config:
    env = read_env(path)
    dedicated = any(key in env for key in ("KEYCLOAK_AUTOMATION_USER", "KEYCLOAK_AUTOMATION_PASSWORD"))
    user_key, password_key = (("KEYCLOAK_AUTOMATION_USER", "KEYCLOAK_AUTOMATION_PASSWORD") if dedicated
                              else ("KEYCLOAK_ADMIN_USER", "KEYCLOAK_ADMIN_PASSWORD"))
    required = ["KEYCLOAK_ISSUER", "WEB_KEYCLOAK_CLIENT_ID", user_key, password_key]
    if any(not env.get(key) for key in required):
        raise KeycloakError("Required nonempty variables: " + ", ".join(required) + ". Dedicated credentials never fall back to bootstrap credentials.")
    issuer = url(env["KEYCLOAK_ISSUER"])
    match = re.fullmatch(r"(.+)/realms/([^/]+)", issuer)
    if not match:
        raise KeycloakError("KEYCLOAK_ISSUER must end with /realms/<realm>.")
    realm = identifier(unquote(match[2]))
    if env.get("KEYCLOAK_REALM", realm) != realm:
        raise KeycloakError("KEYCLOAK_REALM contradicts the realm in KEYCLOAK_ISSUER.")
    cli = env.get("KEYCLOAK_ADMIN_CLI") or None
    if cli and (not Path(cli).is_absolute() or Path(cli).suffix.lower() in {".bat", ".cmd"}):
        raise KeycloakError("KEYCLOAK_ADMIN_CLI must be an absolute executable path; use Docker for Windows batch CLI distributions.")
    if cli and not env.get("KEYCLOAK_CLI_VERSION"):
        raise KeycloakError("Local CLI mode requires its exact KEYCLOAK_CLI_VERSION for server compatibility validation.")
    password = env[password_key]
    if any(c in password for c in "\r\n\x00"):
        raise KeycloakError("Administrator password cannot contain newline or NUL for stdin authentication.")
    return Config(realm=realm, issuer=issuer,
                  server=url(env.get("KEYCLOAK_ADMIN_URL") or (env.get("KEYCLOAK_EXTERNAL_URL", match[1]) if cli else "http://localhost:8080")),
                  admin_realm=identifier(env.get("KEYCLOAK_ADMIN_REALM", "master")),
                  admin_user=identifier(env[user_key]), admin_password=password,
                  client_id=identifier(env["WEB_KEYCLOAK_CLIENT_ID"]),
                  app_url=url(env.get("APP_EXTERNAL_URL", "http://localhost:5173")),
                  container=identifier(env.get("KEYCLOAK_ADMIN_CONTAINER", "app-keycloak")),
                  cli=cli, cli_version=env.get("KEYCLOAK_CLI_VERSION"),
                  confidential=bool(env.get("WEB_KEYCLOAK_CLIENT_SECRET")))


def protect(path: Path) -> None:
    """Restrict an already empty file/directory before writing credentials."""
    if os.name == "nt":
        try:
            identity = subprocess.run(["whoami", "/user", "/fo", "csv", "/nh"], capture_output=True, text=True, check=True)
            sid = next(csv.reader([identity.stdout.strip()]))[1]
            permission = "(OI)(CI)F" if path.is_dir() else "F"
            subprocess.run(["icacls", str(path), "/inheritance:r", "/grant:r", f"*{sid}:{permission}"], capture_output=True, check=True)
        except (OSError, subprocess.SubprocessError, IndexError, StopIteration):
            raise KeycloakError("Cannot restrict credential file permissions.") from None
    else:
        path.chmod(0o700 if path.is_dir() else 0o600)


def save_manifest(path: Path, data: dict, *, new: bool = False) -> None:
    if not path.is_absolute() or path.is_symlink():
        raise KeycloakError("Manifest must be an absolute non-symlink path.")
    if new and path.exists():
        raise KeycloakError("Manifest already exists; recover/clean it before a new run.")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        handle, filename = tempfile.mkstemp(prefix=".fixture-", dir=path.parent)
        temporary = Path(filename)
        os.close(handle)
        protect(temporary)
        temporary.write_text(json.dumps(data, indent=2), encoding="utf-8")
        if new:
            # Exclusive creation avoids replacing another run's recovery journal.
            with path.open("x", encoding="utf-8"):
                pass
        temporary.replace(path)
    finally:
        if temporary:
            temporary.unlink(missing_ok=True)


class Keycloak:
    def __init__(self, config: Config):
        self.config = config
        self.directory: str | None = None
        self.local_directory: Path | None = None

    def _run(self, args: list[str], payload: str | None = None) -> str:
        environment = os.environ.copy()
        environment.pop("KC_CLI_PASSWORD", None)
        environment.pop("KC_CLI_CLIENT_SECRET", None)
        authenticating = args[:2] == ["config", "credentials"]
        if self.config.cli:
            command = [self.config.cli, *args]
            if authenticating:
                environment["KC_CLI_PASSWORD"] = self.config.admin_password
                payload = None
        elif authenticating:
            # Keycloak 26 documents stdin but requires a console in this image.
            # A constant POSIX bridge receives the password over Docker stdin and
            # exports it only inside this process; neither shell source nor argv
            # contains credentials. "$@" passes validated CLI arguments literally.
            bridge = 'IFS= read -r KC_CLI_PASSWORD; export KC_CLI_PASSWORD; exec "$@"'
            command = ["docker", "exec", "-i", self.config.container, "sh", "-c", bridge,
                       "keycloak-stdin", "/opt/keycloak/bin/kcadm.sh", *args]
        else:
            command = ["docker", "exec", "-i", self.config.container, "/opt/keycloak/bin/kcadm.sh", *args]
        try:
            # Binary pipes preserve LF exactly on Windows; text-mode stdin would
            # append CR to the POSIX read password and change the credential.
            completed = subprocess.run(command, input=payload.encode("utf-8") if payload is not None else None, capture_output=True, timeout=90, env=environment)
        except (OSError, subprocess.SubprocessError):
            raise KeycloakError("Keycloak CLI could not complete; verify the executable/container and connectivity.") from None
        if completed.returncode:
            # CLI stderr can contain supplied credentials or server representations.
            detail = (completed.stderr + completed.stdout).decode("utf-8", errors="replace").lower()
            if "invalid_grant" in detail or "invalid user credentials" in detail:
                raise KeycloakError("Administrator authentication failed; verify existing credentials. Bootstrap credentials were not reset.")
            if "console" in detail and "required" in detail:
                raise KeycloakError("The selected CLI requires console authentication; verify protected password transport support.")
            if "404" in detail or "resource not found" in detail:
                raise KeycloakError("Keycloak resource was not found.")
            raise KeycloakError("Keycloak CLI request failed; verify target permissions and prerequisite configuration. Raw output suppressed.")
        return completed.stdout.decode("utf-8", errors="replace")

    def __enter__(self):
        try:
            if self.config.cli:
                self.local_directory = Path(tempfile.mkdtemp(prefix="keycloak-admin-"))
                protect(self.local_directory)
                self.directory = str(self.local_directory)
            else:
                self.directory = "/tmp/keycloak-admin-" + secrets.token_hex(16)
                subprocess.run(["docker", "exec", self.config.container, "mkdir", "-m", "700", self.directory], check=True, capture_output=True, timeout=30)
            self._run(["config", "credentials", "--config", self.directory + "/config", "--server", self.config.server,
                       "--realm", self.config.admin_realm, "--user", self.config.admin_user], self.config.admin_password + "\n")
            if self.config.cli:
                actual_cli = self._run(["--version"]).strip()
                versions = re.findall(r"(?<![A-Za-z0-9])([0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?)", actual_cli)
                version = self.call(["get", "serverinfo"]).get("systemInfo", {}).get("version")
                if len(set(versions)) != 1 or versions[0] != self.config.cli_version or version != self.config.cli_version:
                    raise KeycloakError("Local CLI executable/configured version does not match the authenticated Keycloak server version.")
            return self
        except (OSError, subprocess.SubprocessError):
            self.__exit__(None, None, None)
            raise KeycloakError("Unable to prepare isolated Keycloak CLI state.") from None
        except BaseException:
            self.__exit__(None, None, None)
            raise

    def __exit__(self, *_):
        if self.local_directory:
            shutil.rmtree(self.local_directory)
        elif self.directory:
            # This is a generated exact directory, never a user-controlled delete path.
            try:
                subprocess.run(["docker", "exec", self.config.container, "rm", "-rf", "--", self.directory], check=True, capture_output=True, timeout=30)
            except (OSError, subprocess.SubprocessError):
                raise KeycloakError("CLI temporary authentication cleanup failed; remove the generated keycloak-admin directory in the configured container.") from None
        self.directory = None

    def call(self, args: list[str], data=None, query: dict | None = None):
        if not self.directory:
            raise KeycloakError("Use Keycloak as a context manager.")
        if not isinstance(args, list) or len(args) != 2 or args[0] not in {"get", "create", "update", "delete"}:
            raise KeycloakError("Supply exactly a verb and realm-scoped resource; extra CLI flags are forbidden.")
        verb, resource = args
        if not isinstance(resource, str):
            raise KeycloakError("Invalid resource.")
        for part in resource.split("/"):
            identifier(part)
        first = resource.split("/")[0]
        if first == "realms":
            if resource != f"realms/{self.config.realm}":
                raise KeycloakError("Realm operations are restricted to the configured target realm.")
            if data and isinstance(data, dict) and data.get("realm", self.config.realm) != self.config.realm:
                raise KeycloakError("Realm renaming or switching is not permitted.")
        elif first == "serverinfo":
            if resource != "serverinfo" or verb != "get":
                raise KeycloakError("Server information is read-only.")
        elif first not in {"users", "clients", "roles", "sessions", "client-scopes", "events", "authentication"}:
            raise KeycloakError("Unsupported resource family.")
        command = [verb, resource, "--config", self.directory + "/config", "-r", self.config.realm]
        for key, value in (query or {}).items():
            if key not in {"username", "email", "exact", "clientId", "first", "max", "search"} or not isinstance(value, (str, int, bool)):
                raise KeycloakError("Unsupported query field or value.")
            value = str(value).lower() if isinstance(value, bool) else str(value)
            if any(c in value for c in "\r\n\x00"):
                raise KeycloakError("Invalid query value.")
            command.extend(["-q", key + "=" + value])
        payload = None
        if data is not None:
            if verb not in {"create", "update", "delete"}:
                raise KeycloakError("Read requests cannot contain a mutation payload.")
            command.extend(["-f", "-"])
            payload = json.dumps(data)
            if verb == "update":
                command.append("-n")
        output = self._run(command, payload).strip()
        if not output:
            return None
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            # Mutation CLIs may emit human-readable success lines; never echo them.
            if verb != "get":
                return None
            raise KeycloakError("Keycloak CLI returned invalid JSON; raw output suppressed.") from None


def client(kc: Keycloak) -> dict:
    matches = kc.call(["get", "clients"], query={"clientId": kc.config.client_id})
    matches = [item for item in matches if item.get("clientId") == kc.config.client_id]
    if len(matches) != 1:
        raise KeycloakError("The configured web client was not found uniquely; create or correct WEB_KEYCLOAK_CLIENT_ID.")
    return matches[0]


def role_catalog(kc: Keycloak, client_id: str) -> dict:
    realm_roles = {item["name"]: item for item in kc.call(["get", "roles"])}
    client_roles = {item["name"]: item for item in kc.call(["get", f"clients/{identifier(client_id)}/roles"])}
    result = {}
    for name in ("Users", "Admins"):
        if name in realm_roles:
            result[name] = {"scope": "realm", "role": realm_roles[name]}
        elif name in client_roles:
            result[name] = {"scope": "clients/" + client_id, "role": client_roles[name]}
    return result


FIXTURE_PROFILE_ATTRIBUTES = ("automation_run_id", "self_registered", "awaiting_admin_approval")


def profile_repairs(profile: dict) -> list[str]:
    problems = []
    for name in FIXTURE_PROFILE_ATTRIBUTES:
        matches = [a for a in profile.get("attributes", []) if a.get("name") == name]
        permissions = matches[0].get("permissions", {}) if len(matches) == 1 else {}
        if set(permissions.get("view", [])) != {"admin"} or set(permissions.get("edit", [])) != {"admin"}:
            problems.append(f"Declare user-profile attribute {name} with view/edit permissions restricted to admin; do not enable unrestricted unmanaged attributes.")
    return problems


def doctor(kc: Keycloak) -> dict:
    realm = kc.call(["get", "realms/" + kc.config.realm])
    web_client = client(kc)
    problems = profile_repairs(kc.call(["get", "users/profile"]))
    def require(condition, repair):
        if not condition:
            problems.append(repair)
    require(realm.get("enabled"), "Enable the selected realm.")
    require(realm.get("registrationAllowed"), "Enable realm registrationAllowed for registration coverage.")
    require(realm.get("verifyEmail"), "Enable realm verifyEmail for email-verification coverage.")
    require(realm.get("resetPasswordAllowed"), "Enable realm resetPasswordAllowed for password-reset coverage.")
    require(bool(realm.get("smtpServer", {}).get("host")), "Configure realm SMTP to the local Mailpit service.")
    require("disable-after-email-verify" in realm.get("eventsListeners", []), "Enable the installed disable-after-email-verify realm event listener.")
    require(web_client.get("enabled") and web_client.get("standardFlowEnabled"), "Enable the web client and standardFlowEnabled.")
    require(web_client.get("protocol") == "openid-connect", "Set the web client protocol to openid-connect.")
    require(bool(web_client.get("publicClient")) != kc.config.confidential, "Match client authentication mode with WEB_KEYCLOAK_CLIENT_SECRET.")
    callback = kc.config.app_url + "/auth/callback"
    require(callback in web_client.get("redirectUris", []) or kc.config.app_url + "/*" in web_client.get("redirectUris", []), "Add the application's exact /auth/callback URI to web client redirectUris.")
    roles = role_catalog(kc, web_client["id"])
    for name in ("Users", "Admins"):
        require(name in roles, f"Create the {name} role in the target realm or selected web client.")
    scopes = kc.call(["get", f"clients/{web_client['id']}/default-client-scopes"])
    mappers = list(web_client.get("protocolMappers", []))
    for scope in scopes:
        mappers.extend(kc.call(["get", f"client-scopes/{scope['id']}/protocol-mappers/models"]))
    for name, mapping in roles.items():
        mapper_id = "oidc-usermodel-realm-role-mapper" if mapping["scope"] == "realm" else "oidc-usermodel-client-role-mapper"
        require(any(mapper.get("protocolMapper") == mapper_id and mapper.get("config", {}).get("access.token.claim") == "true" for mapper in mappers), f"Map {name}'s {'realm' if mapping['scope'] == 'realm' else 'client'} roles into the access token through a default scope or client mapper.")
    return {"ok": not problems, "realm": kc.config.realm, "clientId": kc.config.client_id, "repairs": problems,
            "roles": {name: value["scope"] for name, value in roles.items()}, "effectiveRolesChecked": "Each fixture is checked after provisioning; browser login verifies issued claims."}


MARKER = "automation_run_id"
DEFAULT_ACCOUNTS = [{"key": "noRole", "role": "none"}, {"key": "users", "role": "Users"}, {"key": "admins", "role": "Admins"}]


def effective_roles(kc: Keycloak, user_id: str, client_id: str) -> set[str]:
    names = set()
    for scope in ("realm", "clients/" + client_id):
        roles = kc.call(["get", f"users/{identifier(user_id)}/role-mappings/{scope}/composite"])
        names.update(role["name"] for role in roles)
    return names & {"Users", "Admins"}


def read_manifest(kc: Keycloak, path: str | Path) -> tuple[Path, dict]:
    path = Path(path)
    if not path.is_absolute() or path.is_symlink():
        raise KeycloakError("Manifest must be an absolute non-symlink path.")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise KeycloakError("Cannot read fixture recovery manifest.") from None
    if not isinstance(data, dict):
        raise KeycloakError("Invalid fixture manifest shape.")
    if data.get("realm") != kc.config.realm or data.get("issuer") != kc.config.issuer:
        raise KeycloakError("Fixture manifest belongs to another realm/server.")
    run_id = data.get("runId")
    if not isinstance(run_id, str) or not re.fullmatch(r"[a-f0-9]{32}", run_id):
        raise KeycloakError("Invalid fixture run ID.")
    users = data.get("users")
    registration = data.get("registration")
    if not isinstance(users, dict) or len(users) > 30 or not isinstance(registration, dict):
        raise KeycloakError("Invalid fixture record collection.")
    names = set()
    user_ids = set()
    for key, record in [*users.items(), ("registration", registration)]:
        identifier(key)
        lowered = key.lower()
        if lowered in names or (key in users and lowered == "registration"):
            raise KeycloakError("Duplicate or reserved fixture key.")
        names.add(lowered)
        expected_username = f"e2e-{run_id}-{lowered}"
        if not isinstance(record, dict) or record.get("username") not in {expected_username, expected_username + "@example.test"} or record.get("email") != expected_username + "@example.test":
            raise KeycloakError("Fixture reservation does not match its run and key; no lookup or mutation performed.")
        if not isinstance(record.get("role"), str) or record["role"] not in {"none", "Users", "Admins"} or (key == "registration" and record["role"] != "none"):
            raise KeycloakError("Invalid fixture role.")
        if not isinstance(record.get("password"), str) or not record["password"] or any(c in record["password"] for c in "\r\n\x00"):
            raise KeycloakError("Invalid fixture credential record.")
        if not isinstance(record.get("state"), str) or record["state"] not in {"reserved", "created", "ready", "adopting", "approved", "deleted"}:
            raise KeycloakError("Invalid fixture record state.")
        if "id" not in record:
            raise KeycloakError("Fixture record must explicitly record its ID or pending creation.")
        if record["id"] is not None:
            identifier(record["id"])
            if record["id"] in user_ids:
                raise KeycloakError("Duplicate fixture account ID.")
            user_ids.add(record["id"])
    return path, data


def find_exact(kc: Keycloak, record: dict) -> dict | None:
    matches = kc.call(["get", "users"], query={"username": record["username"], "exact": True})
    matches = [user for user in matches if user.get("username") == record["username"]]
    if len(matches) > 1:
        raise KeycloakError("Fixture username did not identify one account.")
    return matches[0] if matches else None


def verify_owned(kc: Keycloak, manifest: dict, record: dict) -> dict | None:
    expected_prefix = "e2e-" + manifest["runId"] + "-"
    if not record.get("username", "").startswith(expected_prefix) or record.get("email") not in {record["username"], record["username"] + "@example.test"}:
        raise KeycloakError("Fixture ownership record is invalid; no deletion performed.")
    user = find_exact(kc, record)
    if user is None:
        return None
    if (record.get("id") and user.get("id") != record["id"]) or user.get("email") != record["email"] or user.get("attributes", {}).get(MARKER) != [manifest["runId"]]:
        raise KeycloakError("Fixture ownership mismatch; no mutation performed.")
    return user


def clear_fixture_role_mappings(kc: Keycloak, manifest: dict, record: dict) -> None:
    user = verify_owned(kc, manifest, record)
    if not user or user["id"] != record.get("id"):
        raise KeycloakError("Owned fixture must exist before isolating its roles.")
    endpoint = f"users/{identifier(user['id'])}/role-mappings"
    mappings = kc.call(["get", endpoint])
    scoped = [("realm", mappings.get("realmMappings", []))]
    scoped.extend(("clients/" + identifier(group["id"]), group.get("mappings", []))
                  for group in mappings.get("clientMappings", {}).values())
    for scope, roles in scoped:
        if roles:
            verify_owned(kc, manifest, record)
            kc.call(["delete", endpoint + "/" + scope], data=roles)


def create_fixtures(kc: Keycloak, manifest_path: str | Path, accounts: list | None = None) -> dict:
    accounts = DEFAULT_ACCOUNTS if accounts is None else accounts
    if not isinstance(accounts, list) or not accounts or len(accounts) > 30:
        raise KeycloakError("Supply between one and thirty fixture account specifications.")
    keys = set()
    for account in accounts:
        key = identifier(account.get("key", ""))
        if key.lower() in keys or key.lower() == "registration" or account.get("role") not in {"none", "Users", "Admins"}:
            raise KeycloakError("Fixture keys must be unique and roles must be none, Users, or Admins.")
        keys.add(key.lower())
    report = doctor(kc)
    if not report["ok"]:
        raise KeycloakError("Fixture preflight failed: " + " ".join(report["repairs"]))
    web_client = client(kc)
    roles = role_catalog(kc, web_client["id"])
    run_id = secrets.token_hex(16)
    manifest = {"version": 1, "runId": run_id, "realm": kc.config.realm, "issuer": kc.config.issuer,
                "users": {}, "registration": {}, "status": "provisioning"}
    def record(key, role):
        username = f"e2e-{run_id}-{key.lower()}@example.test"
        return {"id": None, "username": username, "email": username, "password": "Aa1!" + secrets.token_urlsafe(24), "role": role, "state": "reserved"}
    manifest["registration"] = record("registration", "none")
    path = Path(manifest_path)
    save_manifest(path, manifest, new=True)
    try:
        for account in accounts:
            item = record(account["key"], account["role"])
            manifest["users"][account["key"]] = item
            save_manifest(path, manifest)
            kc.call(["create", "users"], data={"username": item["username"], "email": item["email"], "firstName": "Browser", "lastName": "Fixture", "enabled": True, "emailVerified": True, "requiredActions": [], "attributes": {MARKER: [run_id]}, "credentials": [{"type": "password", "value": item["password"], "temporary": False}]})
            found = find_exact(kc, item)
            if not found:
                raise KeycloakError("Created fixture could not be located; retain its recovery manifest.")
            item["id"] = found["id"]
            item["state"] = "created"
            save_manifest(path, manifest)
            clear_fixture_role_mappings(kc, manifest, item)
            if account["role"] != "none":
                assignment = roles[account["role"]]
                kc.call(["create", f"users/{item['id']}/role-mappings/{assignment['scope']}"], data=[assignment["role"]])
            actual = effective_roles(kc, item["id"], web_client["id"])
            expected = set() if account["role"] == "none" else {account["role"]}
            if actual != expected:
                raise KeycloakError("Fixture effective role mapping differs from requested role; inspect default/composite mappings. No realm policy changed.")
            item["state"] = "ready"
            save_manifest(path, manifest)
        manifest["status"] = "ready"
        save_manifest(path, manifest)
    except BaseException:
        manifest["status"] = "needs-cleanup"
        save_manifest(path, manifest)
        raise
    return {"manifestPath": str(path), "runId": run_id, "count": len(manifest["users"])}


def adopt_registration(kc: Keycloak, manifest_path: str | Path) -> dict:
    path, manifest = read_manifest(kc, manifest_path)
    record = manifest["registration"]
    user = find_exact(kc, record)
    if not user or user.get("email") != record["email"]:
        raise KeycloakError("Reserved registration account has not been created with its exact fixture email.")
    if record.get("id") and record["id"] != user["id"]:
        raise KeycloakError("Registration fixture ID changed; adoption refused.")
    attributes = user.get("attributes", {})
    if attributes.get(MARKER) not in (None, [manifest["runId"]]):
        raise KeycloakError("Registration is owned by another run.")
    # Random username/email reservation was persisted before browser registration.
    # Persist ID before mutation so interruption does not lose the only reference.
    record["id"] = user["id"]
    record["state"] = "adopting"
    save_manifest(path, manifest)
    attributes[MARKER] = [manifest["runId"]]
    kc.call(["update", f"users/{identifier(user['id'])}"], data={**{key: user[key] for key in ("username", "email", "firstName", "lastName") if key in user}, "attributes": attributes})
    verify_owned(kc, manifest, record)
    record["state"] = "created"
    save_manifest(path, manifest)
    return {"id": record["id"], "enabled": user.get("enabled"), "emailVerified": user.get("emailVerified")}


def approve_registration(kc: Keycloak, manifest_path: str | Path) -> dict:
    path, manifest = read_manifest(kc, manifest_path)
    record = manifest["registration"]
    user = verify_owned(kc, manifest, record)
    if not user or user.get("enabled") or not user.get("emailVerified") or user.get("attributes", {}).get("awaiting_admin_approval") != ["true"]:
        raise KeycloakError("Registration is not a verified, disabled account awaiting approval.")
    attributes = user.get("attributes", {})
    attributes.pop("awaiting_admin_approval", None)
    kc.call(["update", f"users/{identifier(user['id'])}"], data={**{key: user[key] for key in ("username", "email", "firstName", "lastName") if key in user}, "enabled": True, "attributes": attributes})
    record["state"] = "approved"
    save_manifest(path, manifest)
    return {"id": record["id"], "approved": True}


def cleanup_fixtures(kc: Keycloak, manifest_path: str | Path) -> dict:
    path, manifest = read_manifest(kc, manifest_path)
    removed = []
    records = [*manifest["users"].values(), manifest["registration"]]
    # Check every ownership record before any deletion in this invocation.
    resolved = [(record, verify_owned(kc, manifest, record)) for record in records if record]
    for record, user in resolved:
        if user:
            # Recheck directly before mutation rather than trusting a stale lookup.
            current = verify_owned(kc, manifest, record)
            if current:
                kc.call(["delete", f"users/{identifier(current['id'])}"])
                removed.append(current["id"])
        record["state"] = "deleted"
        save_manifest(path, manifest)
    manifest["status"] = "keycloak-cleaned"
    save_manifest(path, manifest)
    return {"runId": manifest["runId"], "removedIds": removed, "remaining": 0}


def fixture_status(kc: Keycloak, manifest_path: str | Path, key: str = "registration") -> dict:
    _, manifest = read_manifest(kc, manifest_path)
    record = manifest["registration"] if key == "registration" else manifest["users"][key]
    user = verify_owned(kc, manifest, record)
    if not user:
        return {"exists": False}
    return {"exists": True, "id": user["id"], "enabled": bool(user.get("enabled")),
            "emailVerified": bool(user.get("emailVerified")),
            "awaitingApproval": user.get("attributes", {}).get("awaiting_admin_approval") == ["true"]}


def reset_fixture_password(kc: Keycloak, manifest_path: str | Path, key: str, password: str | None = None) -> dict:
    path, manifest = read_manifest(kc, manifest_path)
    record = manifest["registration"] if key == "registration" else manifest["users"][key]
    user = verify_owned(kc, manifest, record)
    if not user:
        raise KeycloakError("Fixture account is absent; password reset refused.")
    password = password or "Aa1!" + secrets.token_urlsafe(24)
    if not isinstance(password, str) or not password or any(c in password for c in "\r\n\x00"):
        raise KeycloakError("Invalid fixture password.")
    kc.call(["update", f"users/{identifier(user['id'])}/reset-password"], data={"type": "password", "value": password, "temporary": False})
    record["password"] = password
    save_manifest(path, manifest)
    return {"id": user["id"], "reset": True}


SAFE_FIELDS = {"id", "realm", "clientId", "name", "enabled", "emailVerified", "publicClient", "standardFlowEnabled", "registrationAllowed", "verifyEmail", "resetPasswordAllowed", "protocol", "composite", "clientRole"}


def public_result(value):
    if isinstance(value, list):
        return [public_result(item) for item in value]
    if isinstance(value, dict):
        return {key: item for key, item in value.items() if key in SAFE_FIELDS and isinstance(item, (str, int, float, bool, type(None)))}
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", required=True)
    parser.add_argument("command", choices=["doctor", "call", "fixtures-create", "fixtures-cleanup", "fixtures-adopt-registration", "fixtures-approve-registration", "fixtures-status", "fixtures-reset-password"])
    args = parser.parse_args()
    try:
        request = {} if sys.stdin.isatty() else json.loads(sys.stdin.read() or "{}")
        if not isinstance(request, dict):
            raise KeycloakError("JSON request must be an object.")
        with Keycloak(load_config(args.env_file)) as kc:
            if args.command == "doctor":
                result = doctor(kc)
            elif args.command == "call":
                result = public_result(kc.call(request.get("args"), request.get("data"), request.get("query")))
            elif args.command == "fixtures-create":
                result = create_fixtures(kc, request["manifestPath"], request.get("accounts"))
            elif args.command == "fixtures-cleanup":
                result = cleanup_fixtures(kc, request["manifestPath"])
            elif args.command == "fixtures-adopt-registration":
                result = adopt_registration(kc, request["manifestPath"])
            elif args.command == "fixtures-approve-registration":
                result = approve_registration(kc, request["manifestPath"])
            elif args.command == "fixtures-status":
                result = fixture_status(kc, request["manifestPath"], request.get("key", "registration"))
            else:
                result = reset_fixture_password(kc, request["manifestPath"], request["key"], request.get("password"))
        print(json.dumps(result))
        return 1 if isinstance(result, dict) and result.get("ok") is False else 0
    except (KeycloakError, ValueError, KeyError, TypeError, OSError) as error:
        message = str(error) if isinstance(error, KeycloakError) else "Invalid request or unavailable file; values suppressed."
        print(json.dumps({"error": message}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
