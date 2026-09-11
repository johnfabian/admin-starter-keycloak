"""Delivery contracts, real Git worktree ownership, and mocked publication boundaries."""

from contextlib import contextmanager
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import workflow

REAL_RUN = subprocess.run
REAL_OUTPUT = subprocess.check_output


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        local_keys = REAL_OUTPUT(['git', 'rev-parse', '--local-env-vars'], cwd=ROOT, text=True).splitlines()
        clean_env = {k: v for k, v in os.environ.items() if k not in local_keys and not k.startswith('GIT_CONFIG_')}
        clean_env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1')
        isolated = patch.dict(os.environ, clean_env, clear=True)
        isolated.start()
        self.addCleanup(isolated.stop)
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.temp = Path(temp.name)
        self.primary = self.temp / 'primary'
        template = self.temp / 'template'
        template.mkdir()
        self.git('init', '-q', '--initial-branch=main', f'--template={template}', str(self.primary), root=self.temp)
        self.git('config', 'core.hooksPath', str(template), root=self.primary)
        self.git('config', 'core.autocrlf', 'false', root=self.primary)
        self.git('config', 'user.name', 'Workflow Fixture', root=self.primary)
        self.git('config', 'user.email', 'fixture@example.invalid', root=self.primary)
        self.git('remote', 'add', 'origin', 'https://github.com/fixture/repository.git', root=self.primary)
        (self.primary / '.gitignore').write_text('.agent-work/\n', encoding='utf-8')
        self.spec_path = 'specs/features/2026-09-11-fixture.md'
        self.plan_path = 'specs/implementation-plans/2026-09-11-fixture.md'
        self.spec = {
            'version': 2, 'id': 'FEATURE-TEST', 'title': 'Fixture feature',
            'scope': ['Deliver fixture outcomes'], 'nonGoals': ['Production systems'],
            'requirements': [{'id': 'REQ-001', 'actor': 'Developer', 'outcome': 'Observable fixture outcome',
                              'denied': 'Unauthorized action rejected', 'failure': 'Preserve previous state',
                              'acceptance': ['Fixture outcome verified']}],
            'decisions': [],
        }
        self.write_contract(self.primary, self.spec_path, 'feature-spec', self.spec)
        self.plan = {
            'version': 2, 'id': 'FEATURE-TEST', 'title': 'Fixture implementation',
            'specification': self.spec_path, 'specificationDigest': workflow.file_digest(self.primary / self.spec_path),
            'integrationPaths': ['shared'], 'stories': [self.story(1), self.story(2)],
        }
        self.write_contract(self.primary, self.plan_path, 'implementation-plan', self.plan)
        self.commit(self.primary)
        self.integration = self.worktree('integration')
        self.flow = self.new_flow(self.integration)
        self.writers = [self.worktree('writer-one'), self.worktree('writer-two')]

    @staticmethod
    def story(number):
        return {
            'id': f'STORY-{number:03}', 'title': f'Outcome {number}', 'outcome': 'Visible outcome',
            'rollback': 'Revert fixture commit', 'requirements': ['REQ-001'], 'acceptance': ['Outcome exists'],
            'tests': ['Exercise success and rejection'], 'verification': ['test:fast'],
            'ownedPaths': [f'part-{number}'], 'layers': {'data': 'No persistence needed', 'service': 'Fixture logic',
                                                    'ui': 'No interface needed'},
            'kind': 'vertical', 'dependsOn': [],
        }

    def git(self, *args, root=None):
        return REAL_OUTPUT(['git', '-C', str(root or self.integration), *args], text=True).strip()

    def commit(self, root):
        self.git('add', '.', root=root)
        self.git('commit', '-qm', 'Fixture change', '--no-verify', root=root)
        return self.git('rev-parse', 'HEAD', root=root)

    def worktree(self, name):
        path = self.temp / name
        self.git('worktree', 'add', '-qb', name, str(path), root=self.primary)
        return path

    def new_flow(self, root):
        flow = workflow.Workflow(root, '.agent-work/feature/state.json')
        flow.initialize(self.spec_path, self.plan_path, {'independentReview': True, 'worktrees': True,
                                                       'parallel': True, 'harness': 'unit-test fixture', 'coordinator': 'fixture-coordinator'})
        return flow

    @staticmethod
    def write_contract(root, relative, kind, data):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('# Fixture\n\n```' + kind + '\n' + json.dumps(data, indent=2) + '\n```\n', encoding='utf-8')

    @staticmethod
    def state(flow):
        return json.loads(flow.state_path.read_text(encoding='utf-8'))

    def generation(self, flow=None):
        return self.state(flow or self.flow)['generation']

    def record(self, name, data, flow=None):
        path = (flow or self.flow).state_path.parent / (name + '.json')
        path.write_text(json.dumps(data), encoding='utf-8')
        return path

    def approval_data(self, flow=None):
        flow = flow or self.flow
        state = self.state(flow)
        return {'specDigest': state['specDigest'], 'planDigest': state['planDigest'], 'actor': 'human:fixture',
                'statement': 'Implement, commit, push, and submit this exact reviewed fixture plan.',
                'sourceKind': 'conversation', 'source': 'fixture approval record', 'approvedAt': '2026-09-11T20:00:00Z',
                'actions': ['implement', 'commit', 'push', 'pull-request'],
                'target': {'repository': 'fixture/repository', 'branch': state['branch'], 'base': 'main'}}

    def planning_reviews(self, flow=None):
        flow = flow or self.flow
        state = self.state(flow)
        for kind in ('spec', 'plan'):
            path = self.record(kind, {'kind': kind, 'specDigest': state['specDigest'], 'planDigest': state['planDigest'],
                                      'author': 'fixture-author', 'reviewer': 'fixture-reviewer', 'findings': []}, flow)
            flow.record_planning_review(kind, path, self.generation(flow))

    def approve(self, flow=None):
        flow = flow or self.flow
        self.planning_reviews(flow)
        path = self.record('approval', self.approval_data(flow), flow)
        flow.approve(path, self.generation(flow))
        return path

    @contextmanager
    def checks(self, exit_code=0):
        def run(args, **kwargs):
            if len(args) >= 3 and args[1] == 'pnpm':
                kwargs['stdout'].write('Fixture check passed\n' if exit_code == 0 else 'Fixture check failed\n')
                return subprocess.CompletedProcess(args, exit_code)
            if 'push' in args or 'ls-remote' in args:
                raise AssertionError('Unexpected network operation in fixture')
            return REAL_RUN(args, **kwargs)
        with patch.object(workflow.subprocess, 'run', side_effect=run):
            yield

    def claim(self, number=1):
        self.flow.claim(f'STORY-{number:03}', self.writers[number - 1], f'writer-{number}', self.generation())

    def worker_commit(self, number=1, path=None):
        root = self.writers[number - 1]
        target = root / (path or f'part-{number}/value.txt')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text('Observable fixture change\n', encoding='utf-8')
        return self.commit(root)

    def verify(self, number=1):
        with self.checks():
            self.flow.verify_story(f'STORY-{number:03}', self.generation())

    def review(self, number=1, findings=None, reviewer='independent-reviewer', subject=None):
        sid = subject or f'STORY-{number:03}'
        root = self.integration if sid == 'feature' else self.writers[number - 1]
        data = {'kind': 'implementation', 'subject': sid, 'revision': self.git('rev-parse', 'HEAD', root=root),
                'round': self.state(self.flow)['round'], 'reviewer': reviewer, 'findings': findings or []}
        path = self.record(f'review-{sid}-{data["round"]}', data)
        return self.flow.review(sid, path, self.generation())

    def test_identical_review_restores_after_unchanged_recheck(self):
        self.approve(); self.claim(); self.worker_commit(); self.verify(); self.review()
        self.verify()
        self.assertTrue(self.review()["passed"])
        with self.checks():
            self.flow.integrate("STORY-001", self.generation())

    def test_failed_merged_check_retains_claim_and_requires_resolution_review(self):
        self.approve(); self.claim(); self.worker_commit(); self.verify(); self.review()
        with self.checks(1), self.assertRaises(workflow.Invalid):
            self.flow.integrate("STORY-001", self.generation())
        self.assertNotEqual(self.state(self.flow)["stories"]["STORY-001"]["status"], "integrated")
        self.assertIn(self.flow.claim_key("STORY-001"), self.flow.status()["claims"])
        with self.checks(), self.assertRaisesRegex(workflow.Invalid, "resolution review"):
            self.flow.integrate("STORY-001", self.generation())
        record = self.record("resolution", {"kind": "implementation", "subject": "integration:STORY-001",
                           "revision": self.git("rev-parse", "HEAD"), "round": 1,
                           "reviewer": "separate-reviewer", "findings": []})
        with self.checks():
            self.flow.integrate("STORY-001", self.generation(), record)
        self.assertEqual(self.state(self.flow)["stories"]["STORY-001"]["status"], "integrated")
        original = record.read_bytes()
        record.write_text("{}", encoding="utf-8")
        with self.assertRaises(workflow.Invalid):
            self.flow.status()
        record.write_bytes(original)
        record.unlink()
        with self.assertRaises(OSError):
            self.flow.status()

    def test_interrupted_reverification_persists_invalidation(self):
        self.approve()
        self.claim()
        self.worker_commit()
        self.verify()
        for failure in [RuntimeError("corepack unavailable"), KeyboardInterrupt()]:
            with patch.object(self.flow, "run_checks", side_effect=failure):
                with self.assertRaises((workflow.Invalid, KeyboardInterrupt)):
                    self.flow.verify_story("STORY-001", self.generation())
            item = self.state(self.flow)["stories"]["STORY-001"]
            self.assertIsNone(item["verification"])
            self.assertIsNone(item["review"])
            with self.assertRaises(workflow.Invalid):
                self.flow.integrate("STORY-001", self.generation())
            self.verify()

    def test_effective_push_destination_must_match_approval(self):
        self.approve()
        for urls in [
            ["https://github.com/other/repository.git"],
            ["https://github.com/fixture/repository.git", "https://github.com/other/repository.git"],
        ]:
            subprocess.run(["git", "-C", str(self.integration), "config", "--unset-all", "remote.origin.pushurl"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            for url in urls:
                self.git("config", "--add", "remote.origin.pushurl", url)
            with self.assertRaises(workflow.Invalid):
                self.flow.status()

    def test_invalid_contracts_dependencies_and_path_ownership(self):
        cases = []
        missing = copy.deepcopy(self.plan); del missing['stories'][0]['layers']; cases.append((missing, 'layers|data/service/ui'))
        unknown = copy.deepcopy(self.plan); unknown['stories'][0]['dependsOn'] = ['STORY-999']; cases.append((unknown, 'Unknown dependency'))
        cycle = copy.deepcopy(self.plan)
        cycle['stories'][0]['dependsOn'] = ['STORY-002']; cycle['stories'][1]['dependsOn'] = ['STORY-001']
        cases.append((cycle, 'cycle'))
        collision = copy.deepcopy(self.plan); collision['stories'][1]['ownedPaths'] = ['PART-1/nested']; cases.append((collision, 'overlap'))
        shared = copy.deepcopy(self.plan); shared['stories'][0]['ownedPaths'] = ['shared/file']; cases.append((shared, 'integration owner'))
        for plan, message in cases:
            with self.subTest(message=message):
                self.write_contract(self.integration, self.plan_path, 'implementation-plan', plan)
                with self.assertRaisesRegex(workflow.Invalid, message):
                    workflow.validate_plan(self.integration, self.plan_path)
        ordered = copy.deepcopy(collision); ordered['stories'][1]['dependsOn'] = ['STORY-001']
        self.write_contract(self.integration, self.plan_path, 'implementation-plan', ordered)
        workflow.validate_plan(self.integration, self.plan_path)
        invalid = copy.deepcopy(self.spec); invalid['version'] = 1
        self.write_contract(self.integration, self.spec_path, 'feature-spec', invalid)
        with self.assertRaisesRegex(workflow.Invalid, 'version'):
            workflow.validate_spec(self.integration, self.spec_path)

    def test_exact_spec_bytes_and_approval_records_bind_authority(self):
        with self.assertRaisesRegex(workflow.Invalid, 'human approval'):
            self.claim()
        self.planning_reviews()
        data = self.approval_data(); data['planDigest'] = 'sha256:wrong'
        with self.assertRaisesRegex(workflow.Invalid, 'Evidence mismatch'):
            self.flow.approve(self.record('bad-approval', data), self.generation())
        data = self.approval_data(); data['target']['branch'] = 'other-branch'
        with self.assertRaisesRegex(workflow.Invalid, 'destination'):
            self.flow.approve(self.record('wrong-target', data), self.generation())
        self.flow.approve(self.record('approval', self.approval_data()), self.generation())
        approval = self.record('approval', {**self.approval_data(), 'statement': 'Changed after approval'})
        with self.assertRaisesRegex(workflow.Invalid, 'evidence changed'):
            self.claim()
        self.assertTrue(approval.exists())
        path = self.integration / self.spec_path
        path.write_bytes(path.read_bytes() + b'\n')
        with self.assertRaisesRegex(workflow.Invalid, 'Specification changed'):
            workflow.validate_plan(self.integration, self.plan_path)

    def test_planning_review_independence_and_evidence_mutation(self):
        state = self.state(self.flow)
        review = {'kind': 'spec', 'specDigest': state['specDigest'], 'planDigest': state['planDigest'],
                  'author': 'same-agent', 'reviewer': 'same-agent', 'findings': []}
        with self.assertRaisesRegex(workflow.Invalid, 'separate author'):
            self.flow.record_planning_review('spec', self.record('self-review', review), self.generation())
        self.planning_reviews()
        self.record('spec', {**review, 'reviewer': 'different-agent'})
        with self.assertRaisesRegex(workflow.Invalid, 'evidence changed'):
            self.flow.approve(self.record('approval', self.approval_data()), self.generation())

    def test_evidence_cached_data_cannot_disagree_with_recorded_file(self):
        self.approve()
        state = self.state(self.flow)
        state['approval']['data']['target']['branch'] = 'unapproved-branch'
        self.flow.state_path.write_text(json.dumps(state), encoding='utf-8')
        with self.assertRaisesRegex(workflow.Invalid, 'evidence|Evidence'):
            self.flow.status()

    def test_changed_plan_bytes_invalidate_saved_approval(self):
        self.approve()
        path = self.integration / self.plan_path
        path.write_bytes(path.read_bytes() + b'\n')
        with self.assertRaisesRegex(workflow.Invalid, 'implementation plan changed'):
            self.flow.status()

    def test_worker_revision_change_and_log_tamper_invalidate_verification(self):
        self.approve(); self.claim(); self.worker_commit(); self.verify()
        evidence = self.state(self.flow)['stories']['STORY-001']['verification']
        log = Path(evidence['checks'][0]['log'])
        log.write_text('Changed log', encoding='utf-8')
        with self.assertRaisesRegex(workflow.Invalid, 'evidence changed'):
            self.review()
        self.verify()
        path = self.writers[0] / 'part-1/second.txt'
        path.write_text('Another revision', encoding='utf-8')
        self.commit(self.writers[0])
        with self.assertRaisesRegex(workflow.Invalid, 'stale verification'):
            self.review()

    def test_generation_cas_prevents_stale_claim_mutation(self):
        self.approve()
        stale = self.generation()
        self.claim()
        before = self.flow.state_path.read_bytes(), self.flow.registry_path.read_bytes()
        with self.assertRaisesRegex(workflow.Invalid, 'Stale generation'):
            self.flow.claim('STORY-002', self.writers[1], 'writer-2', stale)
        self.assertEqual(before, (self.flow.state_path.read_bytes(), self.flow.registry_path.read_bytes()))

    def test_claims_require_separate_worktrees_and_share_global_capacity(self):
        self.approve()
        with self.assertRaisesRegex(workflow.Invalid, 'dedicated linked'):
            self.flow.claim('STORY-001', self.integration, 'same-root', self.generation())
        with self.assertRaisesRegex(RuntimeError, 'primary checkout'):
            self.flow.claim('STORY-001', self.primary, 'primary', self.generation())
        self.claim(1)
        with self.assertRaisesRegex(workflow.Invalid, 'already reserved'):
            self.flow.claim('STORY-002', self.writers[0], 'another-agent', self.generation())
        self.claim(2)
        other_root = self.worktree('other-integration')
        other = self.new_flow(other_root)
        self.approve(other)
        self.assertEqual(other.registry_path, self.flow.registry_path)
        self.assertEqual(other.status()['ready'], [])
        third = self.worktree('third-writer')
        with self.assertRaisesRegex(workflow.Invalid, 'capacity'):
            other.claim('STORY-001', third, 'third-agent', self.generation(other))
        self.flow.release('STORY-001', 'Stopped and reconciled fixture worker', True, self.generation())
        other.claim('STORY-001', third, 'third-agent', self.generation(other))
        self.assertEqual(len(other.status()['claims']), 2)

    def test_actual_worker_history_and_changed_paths_are_verified(self):
        self.approve(); self.claim()
        self.worker_commit(path='unowned/file.txt')
        with self.checks(), self.assertRaisesRegex(workflow.Invalid, 'Out-of-scope'):
            self.flow.verify_story('STORY-001', self.generation())
        self.git('checkout', '--orphan', 'unrelated-history', root=self.writers[0])
        self.git('rm', '-rf', '.', root=self.writers[0])
        self.worker_commit()
        self.git('branch', '-M', 'writer-one', root=self.writers[0])
        with self.checks(), self.assertRaisesRegex(workflow.Invalid, 'lost its assigned base'):
            self.flow.verify_story('STORY-001', self.generation())

    def test_check_failure_and_blocking_review_prevent_merge(self):
        self.approve(); self.claim(); self.worker_commit()
        head = self.git('rev-parse', 'HEAD')
        with self.checks(1), self.assertRaisesRegex(workflow.Invalid, 'Verification failed'):
            self.flow.verify_story('STORY-001', self.generation())
        with self.assertRaisesRegex(workflow.Invalid, 'verification'):
            self.flow.integrate('STORY-001', self.generation())
        self.verify()
        self.assertFalse(self.review(findings=[{'severity': 'high', 'evidence': 'Fixture blocking defect', 'disposition': 'open'}])['passed'])
        with self.assertRaisesRegex(workflow.Invalid, 'passing review'):
            self.flow.integrate('STORY-001', self.generation())
        self.assertEqual(self.git('rev-parse', 'HEAD'), head)
        self.assertEqual(self.state(self.flow)['stories']['STORY-001']['status'], 'blocked')

    def test_review_round_budget_is_shared_and_exhausts_at_five(self):
        self.approve(); self.claim(1); self.claim(2)
        self.worker_commit(1); self.worker_commit(2)
        finding = [{'severity': 'high', 'evidence': 'Unresolved fixture defect', 'disposition': 'open'}]
        for round_number in range(1, 6):
            self.verify(1)
            result = self.review(1, findings=finding)
            self.assertEqual(result['round'], round_number)
            self.assertEqual(result['exhausted'], round_number == 5)
            if round_number < 5:
                self.flow.next_round('Fix fixture findings', self.generation())
        self.verify(2)
        self.assertEqual(self.review(2)['round'], 5)
        with self.assertRaisesRegex(workflow.Invalid, 'Five review rounds'):
            self.flow.next_round('Another fix', self.generation())
        self.assertEqual(len(self.state(self.flow)['roundHistory']), 6)

    def test_same_subject_cannot_bypass_round_budget_by_repeated_review(self):
        self.approve(); self.claim(); self.worker_commit(); self.verify()
        self.review(findings=[{'severity': 'high', 'evidence': 'Fixture defect', 'disposition': 'open'}])
        with self.assertRaises(workflow.Invalid):
            self.review()
        self.assertEqual(len(self.state(self.flow)['roundHistory']), 1)

    def test_release_requires_reconciliation_and_clean_worker_and_preserves_commit(self):
        self.approve(); self.claim()
        with self.assertRaisesRegex(workflow.Invalid, 'reconciliation'):
            self.flow.release('STORY-001', 'Not reconciled', False, self.generation())
        path = self.writers[0] / 'part-1/value.txt'; path.parent.mkdir(); path.write_text('Pending work', encoding='utf-8')
        with self.assertRaisesRegex(workflow.Invalid, 'unrelated changes'):
            self.flow.release('STORY-001', 'Worker stopped', True, self.generation())
        revision = self.commit(self.writers[0])
        self.flow.release('STORY-001', 'Worker stopped and changes preserved', True, self.generation())
        self.assertEqual(self.git('rev-parse', 'HEAD', root=self.writers[0]), revision)
        self.assertTrue(path.exists())
        self.assertEqual(self.state(self.flow)['stories']['STORY-001']['status'], 'pending')
        self.assertFalse(self.flow.status()['claims'])

    def publishable(self, final_review=True):
        self.approve(); self.claim(1); self.claim(2)
        for number in (1, 2):
            self.worker_commit(number); self.verify(number); self.review(number)
        for number in (1, 2):
            with self.checks():
                self.flow.integrate(f'STORY-{number:03}', self.generation())
        # Reuse the same coordinator instance: load must observe the merge commits.
        self.assertTrue(all(s['status'] == 'integrated' for s in self.flow.status()['stories'].values()))
        with self.checks():
            self.flow.verify_feature(self.generation())
        if final_review:
            self.review(subject='feature')
        head = self.git('rev-parse', 'HEAD')
        body = self.flow.state_path.parent / 'pr.md'
        body.write_text('<!-- feature-workflow: FEATURE-TEST -->\nVerified revision: ' + head + '\n', encoding='utf-8')
        return head, body

    @contextmanager
    def publication_boundary(self, matches, actual=None):
        calls = []
        def output(args, **kwargs):
            if 'ls-remote' in args:
                calls.append(('remote', args)); return ''
            if len(args) >= 3 and args[1:3] == ['pr', 'list']:
                calls.append(('list', args)); return json.dumps(matches)
            if len(args) >= 3 and args[1:3] == ['pr', 'view']:
                calls.append(('view', args)); return json.dumps(actual)
            if len(args) >= 3 and args[1:3] in (['pr', 'create'], ['pr', 'edit']):
                calls.append(('mutation', args)); return 'https://github.com/fixture/repository/pull/7\n'
            return REAL_OUTPUT(args, **kwargs)
        def run(args, **kwargs):
            if 'push' in args:
                calls.append(('push', args)); return subprocess.CompletedProcess(args, 0)
            return REAL_RUN(args, **kwargs)
        with patch.object(workflow, 'executable', return_value='fixture-gh'), patch.object(workflow.subprocess, 'check_output', side_effect=output), patch.object(workflow.subprocess, 'run', side_effect=run):
            yield calls

    def test_failed_reverification_cannot_retain_prior_passing_evidence(self):
        self.approve(); self.claim(); self.worker_commit(); self.verify(); self.review()
        with self.checks(1), self.assertRaisesRegex(workflow.Invalid, 'Verification failed'):
            self.flow.verify_story('STORY-001', self.generation())
        item = self.state(self.flow)['stories']['STORY-001']
        self.assertIsNone(item['verification'])
        self.assertIsNone(item['review'])
        with self.assertRaisesRegex(workflow.Invalid, 'verification'):
            self.flow.integrate('STORY-001', self.generation())

    def test_final_review_rejects_the_actual_coordinator_identity(self):
        self.publishable(final_review=False)
        with self.assertRaisesRegex(workflow.Invalid, 'independent'):
            self.review(subject='feature', reviewer='fixture-coordinator')
        self.assertIsNone(self.state(self.flow)['finalReview'])
        self.assertTrue(self.review(subject='feature')['passed'])

    def test_publication_rejects_target_head_and_workflow_body_conflicts_before_push(self):
        head, body = self.publishable()
        base = {'number': 7, 'headRefName': 'integration', 'headRefOid': head, 'baseRefName': 'main', 'isCrossRepository': False, 'headRepository': {'name': 'repository'}, 'headRepositoryOwner': {'login': 'fixture'},
                'body': body.read_text(), 'url': 'https://github.com/fixture/repository/pull/7', 'title': 'Fixture'}
        for key, value in [('baseRefName', 'other-base'), ('headRefOid', 'a' * 40), ('body', 'Unrelated PR'), ('isCrossRepository', True), ('headRepositoryOwner', {'login': 'foreign'})]:
            with self.subTest(key=key), self.publication_boundary([{**base, key: value}]) as calls:
                with self.assertRaises(workflow.Invalid):
                    self.flow.publish('Fixture', body, self.generation())
                self.assertFalse(any(kind in {'push', 'mutation'} for kind, _ in calls))
        with self.publication_boundary([base, base]) as calls, self.assertRaisesRegex(workflow.Invalid, 'Duplicate'):
            self.flow.publish('Fixture', body, self.generation())
        self.assertFalse(any(kind in {'push', 'mutation'} for kind, _ in calls))

    def test_publication_requires_exact_readback_and_retries_existing_pr(self):
        head, body = self.publishable()
        actual = {'url': 'https://github.com/fixture/repository/pull/7', 'body': body.read_text(),
                  'title': 'Fixture', 'headRefOid': head, 'baseRefName': 'main', 'isCrossRepository': False, 'headRepository': {'name': 'repository'}, 'headRepositoryOwner': {'login': 'fixture'}}
        with self.publication_boundary([], {**actual, 'body': 'Changed externally'}) as calls:
            with self.assertRaisesRegex(workflow.Invalid, 'read-back differs'):
                self.flow.publish('Fixture', body, self.generation())
            self.assertEqual(sum(kind == 'push' for kind, _ in calls), 1)
        self.assertIsNone(self.state(self.flow)['publication'])
        existing = {**actual, 'number': 7, 'headRefName': 'integration'}
        with self.publication_boundary([existing], actual) as calls:
            result = self.flow.publish('Fixture', body, self.generation())
        self.assertEqual(result['revision'], head)
        mutations = [args for kind, args in calls if kind == 'mutation']
        self.assertEqual(len(mutations), 1)
        self.assertEqual(mutations[0][1:3], ['pr', 'edit'])
        self.assertIn('--body-file', mutations[0])
        self.assertEqual(self.state(self.flow)['publication']['bodyDigest'], workflow.file_digest(body))


if __name__ == '__main__':
    unittest.main()
