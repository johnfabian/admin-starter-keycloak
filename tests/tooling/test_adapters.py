"""Behavioral coverage for scoped provider discovery and invocation-policy audits."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SKILLS_AUDIT = ROOT / '.agents-config/skills/meta/skills-audit/scripts/audit_skills.py'
RULES_AUDIT = ROOT / '.agents-config/skills/meta/rules-audit/scripts/audit_rules.py'


class AdapterAuditTests(unittest.TestCase):
    def setUp(self):
        local_keys = subprocess.check_output(
            ['git', 'rev-parse', '--local-env-vars'], cwd=ROOT, text=True
        ).splitlines()
        clean_env = {
            key: value for key, value in os.environ.items()
            if key not in local_keys and not key.startswith('GIT_CONFIG_')
        }
        clean_env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1')
        isolated = patch.dict(os.environ, clean_env, clear=True)
        isolated.start()
        self.addCleanup(isolated.stop)
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.temp = Path(temp.name)
        self.root = self.temp / 'repo'
        self.home = self.temp / 'home'
        template = self.temp / 'template'
        template.mkdir()
        self.git('init', '-q', f'--template={template}', str(self.root), cwd=self.temp)
        self.git('config', 'core.hooksPath', str(template))
        self.git('config', 'core.autocrlf', 'false')
        self.git('config', 'core.symlinks', 'true')
        for kind in ('dev', 'meta', 'ops'):
            (self.root / '.agents-config/skills' / kind).mkdir(parents=True)
        self.skill('plan-feature')
        self.catalog()
        self.git('add', '.')
        self.git('-c', 'user.name=Adapter Fixture', '-c', 'user.email=fixture@example.invalid',
                 'commit', '-qm', 'fixture', '--no-verify')

    def git(self, *args, cwd=None):
        return subprocess.check_output(['git', *args], cwd=cwd or self.root, text=True)

    def skill(self, name, *, claude=False, codex=False):
        path = self.root / '.agents-config/skills/dev' / name
        (path / 'agents').mkdir(parents=True, exist_ok=True)
        lock = 'disable-model-invocation: true\n' if claude else ''
        (path / 'SKILL.md').write_text(
            f'---\nname: {name}\ndescription: Fixture skill.\n{lock}---\n\nFixture.\n',
            encoding='utf-8',
        )
        (path / 'agents/openai.yaml').write_text(
            'policy:\n  allow_implicit_invocation: false\n' if codex else 'interface:\n  display_name: Fixture\n',
            encoding='utf-8',
        )
        return path

    def catalog(self):
        packages = sorted((self.root / '.agents-config/skills').glob('*/*/SKILL.md'))
        content = '<!-- skills-catalog:start -->\n'
        content += '\n'.join(f'[skill]({path.relative_to(self.root).as_posix()})' for path in packages)
        (self.root / 'README.md').write_text(content + '\n<!-- skills-catalog:end -->\n', encoding='utf-8')

    def audit(self, *args, root=None, script=SKILLS_AUDIT, expected=0):
        result = subprocess.run(
            [sys.executable, str(script), str(root or self.root), '--json', *args],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def test_two_worktrees_do_not_retarget_project_or_global_adapters(self):
        one, two = self.temp / 'one', self.temp / 'two'
        self.git('worktree', 'add', '-qb', 'one', str(one))
        self.git('worktree', 'add', '-qb', 'two', str(two))
        for tree in (one, two):
            for kind in ('meta', 'ops'):
                (tree / '.agents-config/skills' / kind).mkdir()
        self.audit('--fix', '--global-adapters', '--home', str(self.home), root=one)
        global_link = self.home / '.codex/skills/plan-feature'
        original = os.readlink(global_link)
        first = one / '.agents/skills/plan-feature'
        first_target = os.readlink(first)
        report = self.audit('--fix', '--home', str(self.home), root=two)
        self.assertEqual(report['adapterScope'], 'project')
        self.assertIsNone(report['home'])
        self.assertEqual(report['summary']['globalAdapters'], 0)
        self.assertEqual(os.readlink(global_link), original)
        self.assertEqual(os.readlink(first), first_target)
        for tree in (one, two):
            for provider in ('.agents', '.claude'):
                link = tree / provider / 'skills/plan-feature'
                self.assertFalse(os.path.isabs(os.readlink(link)))
                self.assertEqual(link.resolve(), tree / '.agents-config/skills/dev/plan-feature')

    def test_global_adapters_require_opt_in_for_audit_and_repair(self):
        self.audit('--fix', '--home', str(self.home))
        self.assertFalse(self.home.exists())
        report = self.audit('--global-adapters', '--home', str(self.home), expected=1)
        self.assertIn('missing-global-adapter-root', {item['code'] for item in report['errors']})
        self.assertFalse(self.home.exists())
        self.audit('--fix', '--global-adapters', '--home', str(self.home))
        report = self.audit('--global-adapters', '--home', str(self.home))
        self.assertEqual(report['summary']['globalAdapters'], 2)
        for provider in ('.claude', '.codex'):
            link = self.home / provider / 'skills/plan-feature'
            self.assertTrue(os.path.isabs(os.readlink(link)))
            self.assertEqual(link.resolve(), self.root / '.agents-config/skills/dev/plan-feature')

    def test_renamed_links_are_removed_only_after_replacement_exists(self):
        self.audit('--fix')
        for old, new in [('critique-plan', 'critique-feature-spec'), ('decompose-stories', 'plan-implementation')]:
            for provider in ('.agents', '.claude'):
                link = self.root / provider / 'skills' / old
                link.symlink_to(f'../../.agents-config/skills/dev/{old}', target_is_directory=True)
            self.audit('--fix', expected=1)
            self.assertTrue((self.root / '.agents/skills' / old).is_symlink())
            self.skill(new)
            self.catalog()
            report = self.audit('--fix')
            self.assertEqual(sum(f['code'] == 'removed-renamed-project-adapter' for f in report['fixes']), 2)
            for provider in ('.agents', '.claude'):
                self.assertFalse(os.path.lexists(self.root / provider / 'skills' / old))
        self.audit()

    def test_real_files_directories_and_unrelated_links_survive_repair(self):
        self.skill('critique-feature-spec')
        self.skill('plan-implementation')
        self.catalog()
        self.audit('--fix')
        obsolete_file = self.root / '.agents/skills/critique-plan'
        obsolete_file.write_text('user-owned', encoding='utf-8')
        obsolete_dir = self.root / '.agents/skills/decompose-stories'
        obsolete_dir.mkdir()
        (obsolete_dir / 'SKILL.md').write_text('user-owned package', encoding='utf-8')
        unrelated = self.root / '.claude/skills/unrelated'
        unrelated.symlink_to('missing', target_is_directory=True)
        canonical_collision = self.root / '.claude/skills/plan-feature'
        canonical_collision.unlink()
        canonical_collision.write_text('user-owned adapter', encoding='utf-8')
        report = self.audit('--fix', expected=1)
        self.assertIn('project-adapter-collision', {item['code'] for item in report['errors']})
        self.assertEqual(obsolete_file.read_text(), 'user-owned')
        self.assertEqual((obsolete_dir / 'SKILL.md').read_text(), 'user-owned package')
        self.assertEqual(canonical_collision.read_text(), 'user-owned adapter')
        self.assertTrue(unrelated.is_symlink())
        self.assertFalse((self.root / '.agents-config/skills/dev/decompose-stories').exists())
        # A known obsolete name is not enough to authorize unlinking an unrelated target.
        external_link = self.root / '.claude/skills/critique-plan'
        external_link.symlink_to(self.temp / 'user-owned-target', target_is_directory=True)
        self.audit('--fix', expected=1)
        self.assertTrue(external_link.is_symlink())

    def test_global_collision_is_preserved(self):
        directory = self.home / '.codex/skills'
        directory.mkdir(parents=True)
        collision = directory / 'plan-feature'
        collision.write_text('user-owned', encoding='utf-8')
        report = self.audit('--fix', '--global-adapters', '--home', str(self.home), expected=1)
        self.assertIn('global-adapter-collision', {item['code'] for item in report['errors']})
        self.assertEqual(collision.read_text(), 'user-owned')

    def test_tracked_adapters_require_symlink_mode(self):
        self.audit('--fix')
        self.git('add', '.agents/skills', '.claude/skills')
        self.audit()
        self.assertTrue(self.git('ls-files', '-s', '--', '.agents/skills/plan-feature').startswith('120000 '))
        # Retain a real symlink in the worktree but corrupt the index mode.
        blob = self.git('rev-parse', ':.agents/skills/plan-feature').strip()
        self.git('update-index', '--cacheinfo', f'100644,{blob},.agents/skills/plan-feature')
        report = self.audit(expected=1)
        self.assertIn('invalid-project-adapter-mode', {item['code'] for item in report['errors']})

    def test_contextual_flows_and_protected_workflows(self):
        for name in ('plan-implementation', 'implement-feature', 'implement-story'):
            self.skill(name)
        self.skill('publish-issues', claude=True, codex=True)
        self.catalog()
        self.audit('--fix')
        self.skill('publish-issues')
        report = self.audit(expected=1)
        codes = {item['code'] for item in report['errors']}
        self.assertIn('missing-claude-invocation-lock', codes)
        self.assertIn('missing-openai-invocation-lock', codes)

    def test_each_audit_rejects_provider_policy_mismatch(self):
        rules = self.root / '.agents-config/rules'
        shutil.copytree(ROOT / '.agents-config/rules', rules)
        # Other rule-fixture errors are unrelated; compare parity findings directly.
        for claude, codex in ((True, False), (False, True)):
            with self.subTest(claude=claude, codex=codex):
                self.skill('plan-feature', claude=claude, codex=codex)
                for script in (SKILLS_AUDIT, RULES_AUDIT):
                    report = self.audit('--fix', script=script, expected=1) if script == SKILLS_AUDIT else self.audit(script=script, expected=1)
                    self.assertIn('provider-invocation-lock-mismatch', {item['code'] for item in report['errors']})
        self.skill('plan-feature')
        self.audit()
        report = self.audit(script=RULES_AUDIT, expected=1)
        self.assertNotIn('provider-invocation-lock-mismatch', {item['code'] for item in report['errors']})


if __name__ == '__main__':
    unittest.main()
