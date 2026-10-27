import pytest
from politics_fantasy.source_eligibility import assess_evidence

CLAIMS = {"scope": "PERSON_EVENT", "official_url": "https://www.senado.es/fake.xml",
          "raw_sha256": "a" * 64, "sha_replayed": True,
          "stable_person_id": True, "as_of_documented": True,
          "reuse_adjudicated": True}

@pytest.mark.parametrize("value", ["not a time", "2026-10-27",
    "2026-10-27T12:00:00", True, 123])
def test_malformed_or_naive_publication_is_invalid(value):
    report = assess_evidence({**CLAIMS, "first_public_at": value})
    assert "FIRST_PUBLIC_AT_INVALID" in report["reasons"]
    assert report["release_ready"] is False

@pytest.mark.parametrize("value", ["2026-10-27T12:00:00Z",
    "2026-10-27T12:00:00+02:00"])
def test_offset_aware_syntax_is_not_source_attestation(value):
    report = assess_evidence({**CLAIMS, "first_public_at": value})
    assert "FIRST_PUBLIC_AT_INVALID" not in report["reasons"]
    assert "PURPOSE_AND_LEGAL_BASIS_REVIEW_NOT_ATTESTED" in report["reasons"]
    assert report["release_ready"] is False
