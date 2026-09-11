# Helper interface

Invoke from the skill directory with `uv run scripts/keycloak.py --env-file <absolute-path> <command>`. Supply request JSON on stdin through a subprocess pipe. No shell expansion or inline secrets are needed.

## Configuration

`read_env(path)` reads literal dotenv assignments, optional `export`, single/double quotes, and whitespace-prefixed inline comments. It does not evaluate shell expressions, interpolate variables, or support multiline values/escaped quotes. The full dictionary is for trusted in-memory use only.

`load_config(path)` requires `KEYCLOAK_ISSUER`, `WEB_KEYCLOAK_CLIENT_ID`, and credentials. Prefer the paired `KEYCLOAK_AUTOMATION_USER` and `KEYCLOAK_AUTOMATION_PASSWORD` for a dedicated realm-local administrator. If either automation key is present, both must be nonempty; partial configuration fails without falling back. When neither is present, existing `KEYCLOAK_ADMIN_USER` and `KEYCLOAK_ADMIN_PASSWORD` are used. Bootstrap variables remain unchanged. Optional values:

| Variable                     | Default and effect                                                                              |
| ---------------------------- | ----------------------------------------------------------------------------------------------- |
| `KEYCLOAK_REALM`             | Issuer realm; differing values fail.                                                            |
| `KEYCLOAK_ADMIN_REALM`       | `master`; administrator login realm only.                                                       |
| `KEYCLOAK_ADMIN_CONTAINER`   | `app-keycloak`.                                                                                 |
| `KEYCLOAK_ADMIN_URL`         | Container-local `http://localhost:8080`; local CLI uses `KEYCLOAK_EXTERNAL_URL` or issuer base. |
| `KEYCLOAK_ADMIN_CLI`         | Unset uses Docker; otherwise absolute executable path.                                          |
| `KEYCLOAK_CLI_VERSION`       | Required in local mode; must equal the executable version and authenticated server version.     |
| `APP_EXTERNAL_URL`           | `http://localhost:5173`, used to inspect the callback allowlist.                                |
| `WEB_KEYCLOAK_CLIENT_SECRET` | Presence determines expected client authentication mode; never printed.                         |

## JSON commands

- `doctor`: `{}` returns `{ok,realm,clientId,repairs,roles,effectiveRolesChecked}`. A missing prerequisite exits nonzero and supplies a specific proposed repair. It checks explicit admin-only ownership/approval profile attributes, realm registration, verification, reset, SMTP, approval listener, client flow/authentication/callback, role definitions and access-token mappers. Effective roles are additionally checked per fixture after creation; browser assertions establish issued-claim behavior.
- `call`: `{"args":["get","users"],"query":{"username":"synthetic-name","exact":true}}`. Mutations use `create`, `update`, or `delete` and optional `data` JSON. Only selected realm resources are allowed. `realms/<selected-realm>` supports inspection/update; cross-realm operations, arbitrary flags, endpoints, and realm renaming fail. Requests with payloads use stdin; updates use explicit no-merge PUT. Unspecified fields are subject to Keycloak endpoint semantics, so send all required fields for the requested update.
- `fixtures-create`: `{"manifestPath":"<absolute-ignored-path>","accounts":[{"key":"noRole","role":"none"},{"key":"users","role":"Users"},{"key":"admins","role":"Admins"}]}`. Omit `accounts` for these defaults. Use extra unique keys for logout/reset journeys. Returns only `{manifestPath,runId,count}`; usernames/passwords/email live in the protected manifest.
- `fixtures-adopt-registration`: `{"manifestPath":"<absolute-ignored-path>"}`. Call immediately once the browser creates the reserved registration account. Confirms exact random username/email, records exact ID before mutation, adds the run marker, and retains existing approval attributes. If interrupted before adoption, retry this operation before cleanup.
- `fixtures-status`: `{"manifestPath":"<absolute-ignored-path>","key":"registration"}` returns existence, ID, enabled, emailVerified, and awaitingApproval after checking ownership. Named fixture keys also work.
- `fixtures-approve-registration`: `{"manifestPath":"<absolute-ignored-path>"}` enables only the owned verified account currently disabled and marked awaiting approval.
- `fixtures-reset-password`: `{"manifestPath":"<absolute-ignored-path>","key":"users"}` generates a fresh password, resets only the verified owned account, and updates the protected manifest. An optional `password` property permits a synthetic browser-test password via stdin. Returns ID and success only.
- `fixtures-cleanup`: `{"manifestPath":"<absolute-ignored-path>"}` returns `{runId,removedIds,remaining}`. The manifest remains with `status: keycloak-cleaned` for the runner's BFF/Mailpit cleanup. Repeated cleanup tolerates already absent users; a different server, ID, marker, or email fails before deletion.

Python integration exposes `Config`, `read_env`, `load_config`, `Keycloak`, `doctor`, `create_fixtures`, `adopt_registration`, `fixture_status`, `approve_registration`, `reset_fixture_password`, and `cleanup_fixtures`. Use `with Keycloak(load_config(path)) as kc:` followed by `kc.call([verb, resource], data=None, query=None)`. Full JSON returned to trusted Python stays in memory. CLI errors deliberately suppress upstream output and authentication is removed on context exit, including failed login.

## Recovery journal

Manifest shape is `{version,runId,realm,issuer,status,users:{<key>:{id,username,email,password,role,state}},registration:{id,username,email,password,role,state}}`. Run IDs and usernames are generated internally. New usernames equal their generated synthetic emails to support email-as-username realms; recovery accepts only the exact run/key-derived legacy username or exact synthetic email. The manifest is an active credential file; keep it ignored and outside graph inputs. Creation records each reserved username before the API mutation, then its exact ID and progression. Cleanup can recover a just-created user from an exact journaled username only when its server run marker/email match. Registration adoption handles the browser-created account separately because a browser cannot set the administrative run marker.

A crash before marking a browser registration requires retrying adoption before cleanup. A failed delete leaves the journal for retry. A failed password reset journal write requires resetting that same owned fixture again; no existing application user is affected. Provisioned fixture accounts have their own direct role mappings cleared after ownership verification, then receive only the requested application role. Effective/composite grants are checked afterward and mismatches fail. Realm defaults and other users are unchanged. Browser-created registration retains realm defaults through approval.

Docker login receives its password via stdin into a constant POSIX bridge, exports `KC_CLI_PASSWORD` for the CLI, and then executes the validated argument array. Local mode supplies that variable only in the child process environment. This works around the bundled Keycloak 26 console requirement while keeping secrets out of arguments and shell source. The subprocess environment remains readable to privileged OS/container principals.
