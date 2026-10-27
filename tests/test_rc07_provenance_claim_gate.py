"""Pre-registered RC07 tests; datetime examples are deliberately SYNTHETIC."""
import unittest
from politics_fantasy.provenance_claim_gate import evaluate_claim_as_of as check, AUTHORITY

NOM = 'ESE/000002-01'
DES = 'ESE/000002-02'
NOM_FAMILY = 'BOCCL_CANDIDATE_ACCEPTANCE'
DES_FAMILY = 'BOCCL_PLENARY_DESIGNATION'
SYNTHETIC_AUTHENTICATED = {
    NOM: {'authority': AUTHORITY, 'record_family': NOM_FAMILY,
          'evidence_ref': NOM, 'first_public_at': '2026-09-10T12:00:00+02:00'},
    DES: {'authority': AUTHORITY, 'record_family': DES_FAMILY,
          'evidence_ref': DES, 'first_public_at': '2026-09-16T12:00:00+02:00'},
}
ACTUAL_UNVERIFIED = {
    k: {**v, 'first_public_at': None}
    for k, v in SYNTHETIC_AUTHENTICATED.items()
}

def ask(ref, family, claim, date='2026-09-17T00:00:00+02:00', registry=None, authority=AUTHORITY):
    return check(authority=authority, record_family=family,
                 evidence_ref=ref, desired_claim=claim, as_of=date,
                 trusted_registry=registry)

class ProvenanceGateRC07(unittest.TestCase):
    def test_01_nomination_cannot_prove_designation(self):
        self.assertEqual(ask(NOM, NOM_FAMILY, 'DESIGNATED_SENATORS', registry=SYNTHETIC_AUTHENTICATED)['reason'], 'ASSERTION_TYPE_MISMATCH')
    def test_02_bulletin_day_not_first_public(self):
        self.assertEqual(ask(NOM, NOM_FAMILY, 'NOMINATED_AND_ACCEPTED_CANDIDATES', registry=ACTUAL_UNVERIFIED)['reason'], 'FIRST_PUBLIC_AT_UNVERIFIED')
    def test_03_synthetic_nomination_later_eligible(self):
        self.assertTrue(ask(NOM, NOM_FAMILY, 'NOMINATED_AND_ACCEPTED_CANDIDATES', date='2026-09-12T00:00:00+02:00', registry=SYNTHETIC_AUTHENTICATED)['eligible'])
    def test_04_synthetic_nomination_before_publication_denied(self):
        self.assertEqual(ask(NOM, NOM_FAMILY, 'NOMINATED_AND_ACCEPTED_CANDIDATES', date='2026-09-09T23:59:59+02:00', registry=SYNTHETIC_AUTHENTICATED)['reason'], 'NOT_PUBLIC_BY_CUTOFF')
    def test_05_actual_designation_unverified_denied(self):
        self.assertEqual(ask(DES, DES_FAMILY, 'DESIGNATED_SENATORS', registry=ACTUAL_UNVERIFIED)['reason'], 'FIRST_PUBLIC_AT_UNVERIFIED')
    def test_06_future_designation_fails_historical_cut(self):
        self.assertEqual(ask(DES, DES_FAMILY, 'DESIGNATED_SENATORS', date='2026-09-12T00:00:00+02:00', registry=SYNTHETIC_AUTHENTICATED)['reason'], 'NOT_PUBLIC_BY_CUTOFF')
    def test_07_synthetic_designation_later_eligible(self):
        self.assertTrue(ask(DES, DES_FAMILY, 'DESIGNATED_SENATORS', registry=SYNTHETIC_AUTHENTICATED)['eligible'])
    def test_08_naive_or_bad_cutoff_denied(self):
        for value in ('2026-09-17T00:00:00','not-a-date'):
            with self.subTest(value=value):
                self.assertEqual(ask(DES, DES_FAMILY, 'DESIGNATED_SENATORS', date=value, registry=SYNTHETIC_AUTHENTICATED)['reason'],'INVALID_AS_OF')
    def test_09_unsupported_claim_denied(self):
        self.assertEqual(ask(DES, DES_FAMILY, 'PERSON_CERTIFIED', registry=SYNTHETIC_AUTHENTICATED)['reason'],'UNSUPPORTED_CLAIM')
    def test_10_wrong_authority_family_missing_reference_denied(self):
        self.assertEqual(ask(DES, DES_FAMILY, 'DESIGNATED_SENATORS', registry=SYNTHETIC_AUTHENTICATED, authority='untrusted')['reason'], 'UNSUPPORTED_AUTHORITY')
        self.assertEqual(ask(DES, NOM_FAMILY, 'DESIGNATED_SENATORS', registry=SYNTHETIC_AUTHENTICATED)['reason'], 'ASSERTION_TYPE_MISMATCH')
        self.assertEqual(ask('', DES_FAMILY, 'DESIGNATED_SENATORS', registry=SYNTHETIC_AUTHENTICATED)['reason'], 'MISSING_REFERENCE')
        self.assertEqual(ask(DES, DES_FAMILY, 'DESIGNATED_SENATORS', registry=None)['reason'], 'NO_TRUSTED_REGISTRY')

if __name__ == '__main__': unittest.main()
