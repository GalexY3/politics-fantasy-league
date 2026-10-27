import unittest
from politics_fantasy.source_event_registry import public_stage_catalog, evaluate_server_claim

class ImmutableServerSourceTests(unittest.TestCase):
    def test_01_zero_verified_publication_timestamps(self):
        s=public_stage_catalog()
        self.assertEqual(s['original_publication_timestamps_verified'],0)
        self.assertEqual(len(s['records']),3)
        self.assertFalse(s['real_person_scoring'])
    def test_02_nomination_remains_unverified(self):
        r=evaluate_server_claim(evidence_ref='ESE/000002-01',desired_claim='NOMINATED_AND_ACCEPTED_CANDIDATES',as_of='2026-09-30T12:00:00+02:00')
        self.assertEqual(r['reason'],'FIRST_PUBLIC_AT_UNVERIFIED')
    def test_03_nomination_cannot_prove_designation(self):
        r=evaluate_server_claim(evidence_ref='ESE/000002-01',desired_claim='DESIGNATED_SENATORS',as_of='2026-09-30T12:00:00+02:00')
        self.assertEqual(r['reason'],'ASSERTION_TYPE_MISMATCH')
    def test_04_designation_remains_unverified(self):
        r=evaluate_server_claim(evidence_ref='ESE/000002-02',desired_claim='DESIGNATED_SENATORS',as_of='2026-09-30T12:00:00+02:00')
        self.assertEqual(r['reason'],'FIRST_PUBLIC_AT_UNVERIFIED')
    def test_05_oath_not_first_published(self):
        r=evaluate_server_claim(evidence_ref='SENADO-XV-P82-20260915',desired_claim='OATH_CONSTITUTION_FULFILLED',as_of='2026-09-30T12:00:00+02:00')
        self.assertEqual(r['reason'],'OATH_FIRST_PUBLIC_AT_UNVERIFIED')
    def test_06_full_status_never_inferred_from_oath(self):
        r=evaluate_server_claim(evidence_ref='SENADO-XV-P82-20260915',desired_claim='FULL_SENATOR_STATUS',as_of='2026-09-30T12:00:00+02:00')
        self.assertEqual(r['reason'],'THREE_LEGAL_PREREQUISITES_UNVERIFIED')
    def test_07_forged_entry_not_supported_by_api(self):
        with self.assertRaises(TypeError):
            evaluate_server_claim(evidence_ref='ESE/000002-02',desired_claim='DESIGNATED_SENATORS',as_of='2026-09-30T12:00:00+02:00',trusted_registry={'ESE/000002-02': {'first_public_at':'2000-01-01T00:00:00Z'}})
    def test_08_unknown_ref_fails_closed(self):
        r=evaluate_server_claim(evidence_ref='INVALID',desired_claim='DESIGNATED_SENATORS',as_of='2026-09-30T12:00:00+02:00')
        self.assertEqual(r['reason'],'UNKNOWN_SERVER_EVIDENCE_REF')
    def test_09_catalog_mutation_does_not_change_internal(self):
        stage=public_stage_catalog()
        stage['records'][0]['first_public_at']='2000-01-01T00:00:00Z'
        r=evaluate_server_claim(evidence_ref='ESE/000002-01',desired_claim='NOMINATED_AND_ACCEPTED_CANDIDATES',as_of='2026-09-30T12:00:00+02:00')
        self.assertEqual(r['reason'],'FIRST_PUBLIC_AT_UNVERIFIED')
    def test_10_naive_timestamp_rejected(self):
        r=evaluate_server_claim(evidence_ref='ESE/000002-01',desired_claim='NOMINATED_AND_ACCEPTED_CANDIDATES',as_of='2026-09-30T12:00:00')
        self.assertEqual(r['reason'],'INVALID_AS_OF')
if __name__=='__main__':unittest.main()
