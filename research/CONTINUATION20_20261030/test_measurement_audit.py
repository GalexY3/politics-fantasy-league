"""Control fixtures for the posthoc audit; no original outcomes in fixtures."""
import hashlib
import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).parents[1] / 'R0_INSTITUTIONAL_PETITIONS_20261030/committee_measurement_audit.py'
spec = importlib.util.spec_from_file_location('measurement_audit', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.csv = b'identifiant;statut;decision_commission\n2760;ouverte;\n3021;classee;written\n3070;ouverte;\n4583;classee;\n'
        self.minute = ("<p>La commission se prononce pour l’examen de la pétition n° 2760.</p>"
                       "<p>La commission se prononce pour l’examen de la pétition n° 3070.</p>"
                       "<p>La pétition n° 3021 est donc classée.</p>"
                       "<p>La pétition n° 4583 est donc classée.</p>").encode()

    def run_audit(self, data=None, minute=None):
        data = self.csv if data is None else data
        return module.audit(data, self.minute if minute is None else minute,
                            expected_sha=hashlib.sha256(data).hexdigest())

    def test_groups_keep_open_status_separate(self):
        result = self.run_audit()
        self.assertEqual(result['groups']['examination']['open_status'], 2)
        self.assertEqual(result['groups']['classification']['missing_decision_field'], 1)
        self.assertFalse(result['population_missingness_estimate'])

    def test_snapshot_drift_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'SNAPSHOT_MISMATCH'):
            module.audit(self.csv, self.minute)

    def test_ambiguous_duplicate_id_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'DUPLICATE'):
            self.run_audit(self.csv + b'2760;classee;\n')

    def test_absent_case_is_inconclusive_not_a_zero_outcome(self):
        result = self.run_audit(self.csv.replace(b'4583;classee;\n', b''))
        self.assertEqual(result['unmatched'], 1)
        self.assertEqual(result['status'], 'INCONCLUSIVE_UNMATCHED_CASES')

    def test_proposed_examination_without_decision_is_not_accepted(self):
        with self.assertRaisesRegex(ValueError, 'ANCHOR_MISSING'):
            self.run_audit(minute=self.minute.replace(b'La commission se prononce', b'Proposition'))

    def test_repeated_column_rejected(self):
        with self.assertRaisesRegex(ValueError, 'CSV_SCHEMA'):
            self.run_audit(self.csv.replace(b'identifiant;', b'identifiant;identifiant;'))


if __name__ == '__main__':
    unittest.main()
