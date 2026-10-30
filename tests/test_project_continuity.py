"""A new chat must fail visibly on stale evidence, reset budgets or invented completion."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

PROJECT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('project_status', PROJECT / 'scripts/project_status.py')
status = importlib.util.module_from_spec(spec)
spec.loader.exec_module(status)


class ContinuityTests(unittest.TestCase):
    def setUp(self):
        self.state = json.loads((PROJECT / 'PROJECT_STATE.json').read_text(encoding='utf-8'))
        self.atlas = copy.deepcopy(self.state['atlas_snapshot'])
        self.budget = copy.deepcopy(self.state['authorization_snapshot'])

    def errors(self):
        return status.validate_state(self.state, self.atlas, self.budget)

    def test_real_state_and_actual_ledger_are_consistent(self):
        _, derived = status.derive()
        self.assertEqual(derived['errors'], [])

    def test_new_atlas_lot_cannot_silently_inherit_old_certification(self):
        self.atlas['batches'] += 1
        self.assertTrue(any('STALE_ATLAS' in e for e in self.errors()))

    def test_prior_authorization_cannot_be_reset_in_handoff(self):
        self.budget['remaining'] = 0
        self.assertTrue(any('STALE_BUDGET' in e for e in self.errors()))

    def test_a_written_milestone_is_not_completed_evidence(self):
        self.state['milestones'][0].update(status='DONE', evidence=[], verified_commit='')
        self.assertTrue(any('Unsubstantiated completion' in e for e in self.errors()))

    def test_missing_evidence_does_not_certify_completion(self):
        self.state['milestones'][0].update(status='DONE', evidence=['missing-receipt.json'], verified_commit='a' * 40)
        self.assertTrue(any('Missing local completion evidence' in e for e in self.errors()))

    def test_parked_question_requires_condition_to_reopen(self):
        self.state['milestones'][0].update(status='PARKED', reopen_when='')
        self.assertTrue(any('reopening condition' in e for e in self.errors()))

    def test_two_active_milestones_in_one_lane_are_rejected(self):
        active = [m for m in self.state['milestones'] if m['lane'] == 'product'][:2]
        for m in active:
            m['status'] = 'IN_PROGRESS'
        self.assertTrue(any('Too much active work' in e for e in self.errors()))


if __name__ == '__main__':
    unittest.main()
