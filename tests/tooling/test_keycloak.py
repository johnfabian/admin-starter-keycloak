"""Observable contracts for isolated Keycloak automation; no live realm calls."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HELPER = Path(__file__).resolve().parents[2] / '.agents-config/skills/ops/keycloak-admin/scripts/keycloak.py'
spec = importlib.util.spec_from_file_location('tested_keycloak', HELPER)
k = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = k
spec.loader.exec_module(k)


class FakeKeycloak:
    def __init__(self, users=None, fail_delete=None):
        self.config = k.Config('other-realm', 'http://localhost:8080/realms/other-realm', 'http://localhost:8080', 'master', 'admin', 'secret', 'web')
        self.users = users or {}
        self.deleted = []
        self.calls = []
        self.fail_delete = fail_delete

    def call(self, args, data=None, query=None):
        self.calls.append((args, data, query))
        verb, endpoint = args
        if verb == 'get' and endpoint == 'users':
            return [u.copy() for u in self.users.values() if u['username'] == query['username']]
        if verb == 'delete':
            uid = endpoint.split('/')[1]
            if uid == self.fail_delete:
                raise k.KeycloakError('Simulated delete failure.')
            self.deleted.append(uid)
            self.users.pop(uid, None)
            return None
        if verb == 'update':
            uid = endpoint.split('/')[1]
            if endpoint.endswith('/reset-password'):
                return None
            self.users[uid].update(data)
            return None
        raise AssertionError(args)


class KeycloakTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.env = self.directory / 'fixture.env'
        self.env.write_text('KEYCLOAK_ISSUER=http://localhost:8080/realms/other-realm\nKEYCLOAK_ADMIN_USER=admin\nKEYCLOAK_ADMIN_PASSWORD="secret # literal"\nWEB_KEYCLOAK_CLIENT_ID=web\n', encoding='utf-8')

    def manifest(self, count=1):
        run = 'a' * 32
        records = {}
        users = {}
        for i in range(count):
            username = f'e2e-{run}-user{i}'
            record = {'id': f'id{i}', 'username': username, 'email': username + '@example.test', 'password': 'synthetic', 'role': 'none', 'state': 'ready'}
            records[f'user{i}'] = record
            users[f'id{i}'] = {**record, 'attributes': {k.MARKER: [run]}}
        registration = {'id': None, 'username': f'e2e-{run}-registration', 'email': f'e2e-{run}-registration@example.test', 'password': 'synthetic', 'role': 'none', 'state': 'reserved'}
        manifest = {'runId': run, 'realm': 'other-realm', 'issuer': 'http://localhost:8080/realms/other-realm', 'users': records, 'registration': registration}
        path = self.directory / 'manifest.json'
        k.save_manifest(path, manifest, new=True)
        return path, manifest, users

    def test_derives_alternate_realm_and_independent_admin_realm(self):
        config = k.load_config(self.env)
        self.assertEqual(config.realm, 'other-realm')
        self.assertEqual(config.admin_realm, 'master')
        self.assertEqual(config.admin_password, 'secret # literal')
        self.assertNotIn(config.admin_password, repr(config))

    def test_dedicated_credentials_override_bootstrap_without_changing_target(self):
        with self.env.open('a') as out:
            out.write('KEYCLOAK_AUTOMATION_USER=automation@example.test\nKEYCLOAK_AUTOMATION_PASSWORD=dedicated-secret\nKEYCLOAK_ADMIN_REALM=other-realm\n')
        config = k.load_config(self.env)
        self.assertEqual(config.admin_user, 'automation@example.test')
        self.assertEqual(config.admin_password, 'dedicated-secret')
        self.assertEqual(config.admin_realm, 'other-realm')
        self.assertEqual(config.realm, 'other-realm')
        self.assertEqual(k.read_env(self.env)['KEYCLOAK_ADMIN_USER'], 'admin')

    def test_partial_dedicated_credentials_never_fall_back(self):
        original = self.env.read_text()
        for suffix in ['KEYCLOAK_AUTOMATION_USER=automation@example.test\n', 'KEYCLOAK_AUTOMATION_PASSWORD=secret\n', 'KEYCLOAK_AUTOMATION_USER=\nKEYCLOAK_AUTOMATION_PASSWORD=\n']:
            self.env.write_text(original + suffix)
            with self.assertRaisesRegex(k.KeycloakError, 'never fall back'):
                k.load_config(self.env)

    def test_profile_preflight_requires_explicit_admin_only_markers(self):
        profile = {'attributes': [{'name': name, 'permissions': {'view': ['admin'], 'edit': ['admin']}} for name in k.FIXTURE_PROFILE_ATTRIBUTES]}
        self.assertEqual(k.profile_repairs(profile), [])
        profile['attributes'][0]['permissions']['edit'].append('user')
        self.assertIn('automation_run_id', k.profile_repairs(profile)[0])
        self.assertEqual(len(k.profile_repairs({'unmanagedAttributePolicy': 'ENABLED'})), 3)
        profile['attributes'].append(profile['attributes'][1])
        self.assertTrue(any('self_registered' in x for x in k.profile_repairs(profile)))

    def test_email_username_fixture_retains_exact_ownership(self):
        path, manifest, users = self.manifest()
        record = manifest['users']['user0']
        record['username'] = record['email']
        users['id0']['username'] = record['username']
        k.save_manifest(path, manifest)
        kc = FakeKeycloak(users)
        _, checked = k.read_manifest(kc, path)
        self.assertEqual(k.verify_owned(kc, checked, record)['id'], 'id0')
        record['username'] = 'unrelated@example.test'
        k.save_manifest(path, manifest)
        with self.assertRaises(k.KeycloakError):
            k.read_manifest(kc, path)

    def test_role_isolation_is_scoped_to_verified_fixture(self):
        path, manifest, users = self.manifest()
        kc = FakeKeycloak(users)
        original = kc.call
        writes = []
        def call(args, data=None, query=None):
            if args == ['get', 'users/id0/role-mappings']:
                return {'realmMappings': [{'id': 'default', 'name': 'default-roles'}], 'clientMappings': {'app': {'id': 'app-client', 'mappings': [{'id': 'users', 'name': 'Users'}]}}}
            if args[0] == 'delete':
                writes.append((args, data))
                return None
            return original(args, data, query)
        kc.call = call
        k.clear_fixture_role_mappings(kc, manifest, manifest['users']['user0'])
        self.assertEqual([args[1] for args, _ in writes], ['users/id0/role-mappings/realm', 'users/id0/role-mappings/clients/app-client'])
        writes.clear()
        users['id0']['attributes'][k.MARKER] = ['different-run']
        with self.assertRaises(k.KeycloakError):
            k.clear_fixture_role_mappings(kc, manifest, manifest['users']['user0'])
        self.assertEqual(writes, [])

    def test_requires_absolute_env_path(self):
        with self.assertRaisesRegex(k.KeycloakError, 'absolute'):
            k.load_config('relative.env')

    def test_contradictory_realm_fails(self):
        with self.env.open('a') as out:
            out.write('KEYCLOAK_REALM=unrelated\n')
        with self.assertRaisesRegex(k.KeycloakError, 'contradicts'):
            k.load_config(self.env)

    def test_literal_env_quotes_comments_and_no_execution(self):
        self.env.write_text("export A='hello # world' # comment\nB=$(never-run) # comment\nC=some#literal\n", encoding='utf-8')
        self.assertEqual(k.read_env(self.env), {'A': 'hello # world', 'B': '$(never-run)', 'C': 'some#literal'})

    def test_malformed_env_error_does_not_print_content(self):
        self.env.write_text('SECRET="do-not-print', encoding='utf-8')
        with self.assertRaises(k.KeycloakError) as raised:
            k.read_env(self.env)
        self.assertNotIn('do-not-print', str(raised.exception))

    def test_transport_rejects_flags_traversal_cross_realm_and_get_payload(self):
        kc = k.Keycloak(k.load_config(self.env))
        kc.directory = '/tmp/test'
        for args in [['get', 'users', '-r', 'other'], ['get', '../realms/master'], ['get', 'realms/master'], ['get', 'users%2f..'], ['get', 'https://host/users'], ['get', 'users?max=1'], ['get', '--server']]:
            with self.subTest(args=args), self.assertRaises(k.KeycloakError):
                kc.call(args)
        with self.assertRaises(k.KeycloakError):
            kc.call(['get', 'users'], data={'password': 'test'})
        with self.assertRaises(k.KeycloakError):
            kc.call(['update', 'realms/other-realm'], data={'realm': 'master'})

    def test_mutation_payload_is_stdin_not_argv(self):
        kc = k.Keycloak(k.load_config(self.env))
        kc.directory = '/tmp/test'
        with patch.object(kc, '_run', return_value='') as run:
            kc.call(['update', 'users/id/reset-password'], data={'value': 'do-not-log'})
        args, payload = run.call_args.args
        self.assertNotIn('do-not-log', ' '.join(args))
        self.assertEqual(json.loads(payload), {'value': 'do-not-log'})
        self.assertIn('-n', args)
        self.assertIn('other-realm', args)

    def test_authentication_password_is_stdin_and_state_is_removed(self):
        config = k.load_config(self.env)
        seen = []
        def run(argv, **kwargs):
            seen.append((argv, kwargs))
            return subprocess.CompletedProcess(argv, 0, stdout=b'', stderr=b'')
        with patch.object(k.subprocess, 'run', side_effect=run):
            with k.Keycloak(config):
                pass
        login = next(item for item in seen if 'credentials' in item[0])
        self.assertEqual(login[1]['input'], (config.admin_password + '\n').encode('utf-8'))
        self.assertNotIn('text', login[1])
        self.assertNotIn('encoding', login[1])
        self.assertNotIn(config.admin_password, ' '.join(login[0]))
        self.assertTrue(any('rm' in args for args, _ in seen))
        self.assertIn('IFS= read -r KC_CLI_PASSWORD; export KC_CLI_PASSWORD; exec "$@"', login[0])

    def test_local_cli_version_mismatch_removes_auth_state(self):
        from dataclasses import replace
        config = replace(k.load_config(self.env), cli=str(self.directory / 'kcadm'), cli_version='26.0.0')
        instance = k.Keycloak(config)
        with patch.object(instance, '_run', side_effect=['', 'kcadm 25.0.0']), patch.object(instance, 'call', return_value={'systemInfo': {'version': '26.0.0'}}), self.assertRaisesRegex(k.KeycloakError, 'version'):
            with instance:
                pass
        self.assertFalse(instance.local_directory.exists())

    def test_local_password_is_only_child_environment(self):
        from dataclasses import replace
        config = replace(k.load_config(self.env), cli=str(self.directory / 'kcadm'), cli_version='26.0.0')
        instance = k.Keycloak(config)
        with patch.object(k.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, stdout=b'', stderr=b'')) as run:
            instance._run(['config', 'credentials'], config.admin_password + '\n')
        self.assertEqual(run.call_args.kwargs['env']['KC_CLI_PASSWORD'], config.admin_password)
        self.assertIsNone(run.call_args.kwargs['input'])
        self.assertNotIn(config.admin_password, ' '.join(run.call_args.args[0]))

    def test_login_failure_is_redacted_and_cleaned(self):
        config = k.load_config(self.env)
        seen = []
        def run(argv, **kwargs):
            seen.append(argv)
            fail = 'credentials' in argv
            return subprocess.CompletedProcess(argv, int(fail), stdout=b'', stderr=b'invalid_grant secret-value' if fail else b'')
        with patch.object(k.subprocess, 'run', side_effect=run), self.assertRaises(k.KeycloakError) as raised:
            with k.Keycloak(config):
                pass
        self.assertNotIn('secret-value', str(raised.exception))
        self.assertIn('authentication failed', str(raised.exception))
        self.assertTrue(any('rm' in args for args in seen))

    def test_public_output_omits_credentials_and_arbitrary_nested_fields(self):
        source = {'id': '123', 'secret': 'hidden', 'credentials': [{'value': 'hidden'}], 'attributes': {'secret': 'hidden'}, 'username': 'private-user', 'enabled': True}
        self.assertEqual(k.public_result(source), {'id': '123', 'enabled': True})

    def test_cleanup_removes_only_owned_ids_and_is_repeatable(self):
        path, manifest, users = self.manifest()
        users['unrelated'] = {'id': 'unrelated', 'username': 'unrelated', 'email': 'private@example.test'}
        kc = FakeKeycloak(users)
        result = k.cleanup_fixtures(kc, path)
        self.assertEqual(result['removedIds'], ['id0'])
        self.assertIn('unrelated', kc.users)
        self.assertEqual(k.cleanup_fixtures(kc, path)['removedIds'], [])
        self.assertEqual(json.loads(path.read_text())['status'], 'keycloak-cleaned')

    def test_cleanup_rejects_changed_marker_id_email_before_any_delete(self):
        for field in ['attributes', 'id', 'email']:
            (self.directory / 'manifest.json').unlink(missing_ok=True)
            path, manifest, users = self.manifest(2)
            users['id1'][field] = {} if field == 'attributes' else 'wrong'
            kc = FakeKeycloak(users)
            with self.subTest(field=field), self.assertRaisesRegex(k.KeycloakError, 'ownership mismatch'):
                k.cleanup_fixtures(kc, path)
            self.assertEqual(kc.deleted, [])

    def test_cleanup_failure_journals_prior_success(self):
        path, _, users = self.manifest(2)
        kc = FakeKeycloak(users, fail_delete='id1')
        with self.assertRaises(k.KeycloakError):
            k.cleanup_fixtures(kc, path)
        saved = json.loads(path.read_text())
        self.assertEqual(saved['users']['user0']['state'], 'deleted')
        self.assertEqual(saved['users']['user1']['state'], 'ready')

    def test_cleanup_recovers_created_account_before_id_was_journaled(self):
        path, manifest, users = self.manifest()
        manifest['users']['user0']['id'] = None
        k.save_manifest(path, manifest)
        kc = FakeKeycloak(users)
        self.assertEqual(k.cleanup_fixtures(kc, path)['removedIds'], ['id0'])

    def test_manifest_wrong_server_rejected(self):
        path, manifest, users = self.manifest()
        manifest['issuer'] = 'http://another/realms/other-realm'
        k.save_manifest(path, manifest)
        kc = FakeKeycloak(users)
        with self.assertRaisesRegex(k.KeycloakError, 'another realm/server'):
            k.cleanup_fixtures(kc, path)
        self.assertEqual(kc.deleted, [])

    def test_manifest_creation_never_overwrites_existing_credentials(self):
        path, manifest, _ = self.manifest()
        original = path.read_bytes()
        with self.assertRaisesRegex(k.KeycloakError, 'already exists'):
            k.save_manifest(path, {'bad': True}, new=True)
        self.assertEqual(path.read_bytes(), original)

    def test_registration_adoption_and_approval_are_owned(self):
        path, manifest, users = self.manifest()
        registration = {**manifest['registration'], 'firstName': 'Browser', 'lastName': 'Fixture', 'id': 'registered', 'enabled': False, 'emailVerified': True, 'attributes': {'awaiting_admin_approval': ['true']}}
        users['registered'] = registration
        kc = FakeKeycloak(users)
        k.adopt_registration(kc, path)
        self.assertEqual(k.fixture_status(kc, path)['awaitingApproval'], True)
        self.assertEqual(k.approve_registration(kc, path), {'id': 'registered', 'approved': True})
        self.assertEqual(kc.users['registered']['attributes'][k.MARKER], [manifest['runId']])
        self.assertNotIn('awaiting_admin_approval', kc.users['registered']['attributes'])
        self.assertTrue(kc.users['registered']['enabled'])
        updates = [data for args, data, _ in kc.calls if args[0] == 'update']
        self.assertTrue(all(data.get('firstName') == 'Browser' and data.get('lastName') == 'Fixture' for data in updates))

    def test_registration_adoption_rejects_different_email(self):
        path, manifest, users = self.manifest()
        users['registered'] = {**manifest['registration'], 'id': 'registered', 'email': 'someone@example.test'}
        kc = FakeKeycloak(users)
        with self.assertRaises(k.KeycloakError):
            k.adopt_registration(kc, path)
        self.assertFalse(any(args[0] != 'get' for args, _, _ in kc.calls))

    def test_tampered_registration_cannot_adopt_existing_user(self):
        path, manifest, users = self.manifest()
        manifest['registration'].update(username='existing-admin', email='existing-admin@example.test')
        k.save_manifest(path, manifest)
        users['existing-admin-id'] = {'id': 'existing-admin-id', 'username': 'existing-admin', 'email': 'existing-admin@example.test', 'attributes': {}}
        kc = FakeKeycloak(users)
        with self.assertRaisesRegex(k.KeycloakError, 'reservation'):
            k.adopt_registration(kc, path)
        self.assertEqual(kc.calls, [])
        self.assertEqual(users['existing-admin-id']['attributes'], {})

    def test_every_record_is_validated_before_registration_lookup(self):
        cases = [
            ('username', 'existing-user'),
            ('email', 'unrelated@example.test'),
            ('role', 'owner'),
            ('id', '../other'),
            ('id', ''),
            ('password', None),
            ('state', 'unknown'),
        ]
        for field, replacement in cases:
            (self.directory / 'manifest.json').unlink(missing_ok=True)
            path, manifest, users = self.manifest()
            manifest['users']['user0'][field] = replacement
            k.save_manifest(path, manifest)
            kc = FakeKeycloak(users)
            with self.subTest(field=field, value=replacement), self.assertRaises(k.KeycloakError):
                k.adopt_registration(kc, path)
            self.assertEqual(kc.calls, [])

    def test_manifest_rejects_key_mismatch_and_registration_role(self):
        path, manifest, users = self.manifest()
        manifest['users']['different-key'] = manifest['users'].pop('user0')
        k.save_manifest(path, manifest)
        kc = FakeKeycloak(users)
        with self.assertRaises(k.KeycloakError):
            k.read_manifest(kc, path)
        self.assertEqual(kc.calls, [])
        manifest['users']['user0'] = manifest['users'].pop('different-key')
        manifest['registration']['role'] = 'Admins'
        k.save_manifest(path, manifest)
        with self.assertRaises(k.KeycloakError):
            k.adopt_registration(kc, path)
        self.assertEqual(kc.calls, [])

    def test_duplicate_case_fixture_keys_rejected_before_doctor(self):
        kc = FakeKeycloak()
        with self.assertRaises(k.KeycloakError):
            k.create_fixtures(kc, self.directory / 'fixture.json', [{'key': 'One', 'role': 'none'}, {'key': 'one', 'role': 'Users'}])
        self.assertEqual(kc.calls, [])

    def test_missing_prerequisites_prevent_fixture_creation(self):
        kc = FakeKeycloak()
        with patch.object(k, 'doctor', return_value={'ok': False, 'repairs': ['Enable registration.']}), self.assertRaisesRegex(k.KeycloakError, 'Enable registration'):
            k.create_fixtures(kc, self.directory / 'fixture.json')
        self.assertFalse((self.directory / 'fixture.json').exists())
        self.assertEqual(kc.calls, [])


if __name__ == '__main__':
    unittest.main()
