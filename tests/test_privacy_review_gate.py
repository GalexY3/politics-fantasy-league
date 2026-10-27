from politics_fantasy.source_eligibility import assess_evidence, policy_status

CLAIMS = {"scope": "PERSON_EVENT", "official_url": "https://www.senado.es/data.xml",
          "raw_sha256": "a" * 64, "sha_replayed": True, "stable_person_id": True,
          "as_of_documented": True, "first_public_at": "2026-06-01T12:00:00+00:00",
          "reuse_adjudicated": True}

def test_claims_cannot_complete_privacy_review():
    result = assess_evidence(CLAIMS)
    assert result["status"] == "QUARANTINED"
    assert not result["real_person_scoring"] and not result["release_ready"]
    assert "PURPOSE_AND_LEGAL_BASIS_REVIEW_NOT_ATTESTED" in result["reasons"]
    assert "EIPD_SCREENING_NOT_ATTESTED" in result["reasons"]

def test_fabricated_legal_flag_is_not_accepted():
    result = assess_evidence({**CLAIMS, "purpose_review_done": True, "eipd_cleared": True})
    assert "UNKNOWN_FIELDS" in result["reasons"]
    assert "PURPOSE_AND_LEGAL_BASIS_REVIEW_NOT_ATTESTED" in result["reasons"]
    assert not result["release_ready"]

def test_aggregate_remains_quarantined_without_person_specific_reasons():
    data = {**CLAIMS, "scope": "AGGREGATE"}
    result = assess_evidence(data)
    assert not result["release_ready"]
    assert "PURPOSE_AND_LEGAL_BASIS_REVIEW_NOT_ATTESTED" not in result["reasons"]
