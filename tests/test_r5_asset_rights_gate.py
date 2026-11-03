"""Synthetic red-team of one R5 prerequisite: rights at exact asset-vintage-use."""
import copy
import unittest
from politics_fantasy.r5_asset_rights_gate import assess_distribution_rights as assess

SHA="a"*64
GOOD={
    "distribution_id":"synthetic-urn:case-A-v1",
    "asset_url":"https://source.example.test/datasets/demo-A.csv",
    "asset_sha256":SHA,
    "requested_purpose":"LOCAL_ACADEMIC_READ",
    "historical_as_of":"2026-10-31T12:00:00+01:00",
    "first_public_at":"2026-10-30T08:00:00Z",
    "rights":{
        "kind":"PUBLISHER_ASSET_SPECIFIC",
        "distribution_id":"synthetic-urn:case-A-v1",
        "asset_sha256":SHA,
        "covered_purposes":["LOCAL_ACADEMIC_READ"],
        "notice_published_at":"2026-10-30T08:00:00Z",
        "terms_mode":"PUBLISHER_OPEN_NOTICE",
        "terms_reviewed_by_human":True,
        "rights_reviewed_by_human":True,
    }
}

class R5RightsTests(unittest.TestCase):
    def mutate(self, field, value, *, nested=False):
        rec=copy.deepcopy(GOOD)
        if nested:
            rec["rights"][field]=value
        else:
            rec[field]=value
        return assess(rec)

    def test_perfect_claim_is_still_not_attestation(self):
        result=assess(GOOD)
        self.assertEqual(result["status"],"BLOCKED_R5")
        self.assertEqual(result["reasons"],["INDEPENDENT_LEGAL_AND_PROVENANCE_ATTESTATION_ABSENT"])
        self.assertFalse(result["reuse_admitted"])
        self.assertFalse(result["empirical_r5_open"])

    def test_publisher_catalogue_general_cannot_inherit_to_asset(self):
        x=self.mutate("kind","PUBLISHER_CATALOGUE_GENERAL",nested=True)
        self.assertIn("GENERAL_OR_THIRD_PARTY_NOTICE_NOT_ASSET_PERMISSION",x["reasons"])

    def test_rights_for_other_distribution_cannot_upgrade_current(self):
        x=self.mutate("distribution_id","synthetic-urn:case-B-v1",nested=True)
        self.assertIn("RIGHTS_DISTRIBUTION_BINDING_MISMATCH",x["reasons"])

    def test_rights_for_other_asset_version_cannot_upgrade_current(self):
        x=self.mutate("asset_sha256","b"*64,nested=True)
        self.assertIn("RIGHTS_VINTAGE_SHA_BINDING_MISMATCH",x["reasons"])

    def test_academic_read_does_not_authorize_public_redistribution(self):
        x=self.mutate("requested_purpose","PUBLIC_ORIGINAL_REDISTRIBUTION")
        self.assertIn("REQUESTED_USE_NOT_COVERED",x["reasons"])

    def test_rights_published_after_historical_cut_are_future_knowledge(self):
        x=self.mutate("notice_published_at","2026-11-01T00:00:00Z",nested=True)
        self.assertIn("RIGHTS_NOTICE_POSTDATES_KNOWLEDGE_CUT",x["reasons"])

    def test_first_public_after_cut_is_future_source(self):
        x=self.mutate("first_public_at","2026-11-01T00:00:00Z")
        self.assertIn("SOURCE_NOT_YET_PUBLIC_AT_CUT",x["reasons"])

    def test_terms_bind_on_access_must_never_auto_accept(self):
        x=self.mutate("terms_mode","BIND_ON_ACCESS",nested=True)
        self.assertIn("TERMS_REQUIRE_SEPARATE_PRIOR_ACCESS_REVIEW",x["reasons"])

    def test_unknown_terms_cannot_be_treated_as_open(self):
        x=self.mutate("terms_mode","NOT_ESTABLISHED",nested=True)
        self.assertIn("TERMS_NOT_ESTABLISHED",x["reasons"])

    def test_review_booleans_cannot_authenticate_a_fake_notice(self):
        x=self.mutate("asset_url","https://evil.test/pretends-to-be-official.csv")
        self.assertFalse(x["reuse_admitted"])
        self.assertFalse(x["independent_attestation"])

    def test_spoofed_extra_authorization_is_quarantined(self):
        x=self.mutate("override_r5",True)
        self.assertIn("UNKNOWN_ASSET_FIELDS",x["reasons"])

    def test_bad_schema_fail_closed(self):
        for x in (None,[],{"rights":None},"unexpected"):
            self.assertFalse(assess(x)["empirical_r5_open"])

    def test_timestamp_naive_rejected(self):
        x=self.mutate("historical_as_of","2026-10-31T12:00:00")
        self.assertIn("KNOWLEDGE_CUT_INVALID",x["reasons"])

    def test_strict_id_and_digest(self):
        self.assertIn("DISTRIBUTION_ID_UNKNOWN",
                      self.mutate("distribution_id",[])["reasons"])
        self.assertIn("ASSET_DIGEST_UNKNOWN",
                      self.mutate("asset_sha256","A"*64)["reasons"])

if __name__=="__main__":unittest.main()
