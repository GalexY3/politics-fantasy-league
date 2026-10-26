import unittest
from politics_fantasy.source_eligibility import assess_evidence, policy_status

GOOD = {"scope": "AGGREGATE", "official_url": "https://www.congreso.es/opendata.json",
        "raw_sha256": "a" * 64, "sha_replayed": True, "reuse_adjudicated": True}

class EligibilityTests(unittest.TestCase):
    def test_documentary_claims_not_independent_proof(self):
        r=assess_evidence(GOOD)
        self.assertIn("CLAIMS_NOT_INDEPENDENTLY_ATTESTED", r["reasons"])
        self.assertFalse(r["real_person_scoring"])
    def test_unknown_id_and_time(self):
        r=assess_evidence({**GOOD, "scope": "PERSON_EVENT"})
        self.assertIn("PERSON_ID_UNRESOLVED", r["reasons"])
        self.assertIn("FIRST_PUBLIC_AT_UNKNOWN", r["reasons"])
    def test_spoofing_does_not_authorize_scoring(self):
        r=assess_evidence({**GOOD, "scope": "PERSON_EVENT", "stable_person_id": True,
            "as_of_documented": True, "first_public_at":"2026-07-23T10:00:00Z"})
        self.assertFalse(r["real_person_scoring"])
    def test_host_path_deception_blocked(self):
        r=assess_evidence({**GOOD, "official_url":"https://www.congreso.es.evil.org/original.json"})
        self.assertIn("UNVERIFIED_SOURCE_URL", r["reasons"])
    def test_non_http_and_auth_blocked(self):
        for url in ("http://www.boe.es/", "https://evil@www.boe.es/x"):
            self.assertIn("UNVERIFIED_SOURCE_URL", assess_evidence({**GOOD, "official_url":url})["reasons"])
    def test_caller_fabricated_receipts_blocked(self):
        self.assertIn("UNKNOWN_FIELDS", assess_evidence({**GOOD,"trusted_receipts":["pass"]})["reasons"])
    def test_rights_not_guaranteed_by_official_host(self):
        self.assertIn("REUSE_RIGHTS_UNADJUDICATED", assess_evidence({**GOOD,"reuse_adjudicated":False})["reasons"])
    def test_no_sha_replay(self):
        self.assertIn("ORIGINAL_NOT_REPLAYED", assess_evidence({**GOOD,"sha_replayed":False})["reasons"])
    def test_malformed_input_fails_closed(self):
        for x in (None, [], 12, "source"):
            self.assertEqual(assess_evidence(x)["status"], "QUARANTINED")
    def test_unhashable_scopes_fail_closed(self):
        for scope in ([], {}, ["PERSON_EVENT"], {"nested": 1}):
            r=assess_evidence({**GOOD, "scope": scope})
            self.assertIn("UNKNOWN_SCOPE", r["reasons"])
            self.assertFalse(r["release_ready"])
    def test_absent_or_bad_url_never_releases(self):
        for url in (None, "file:///tmp/secret", "https://www.congreso.es:444/p"):
            self.assertFalse(assess_evidence({**GOOD, "official_url": url})["release_ready"])
    def test_overall_policy(self):
        self.assertFalse(policy_status()["release_ready"])

if __name__ == "__main__": unittest.main()
