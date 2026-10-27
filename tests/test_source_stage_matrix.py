import pytest
from politics_fantasy.source_event_registry import evaluate_server_claim, public_stage_catalog

REFERENCES = ["ESE/000002-01", "ESE/000002-02", "SENADO-XV-P82-20260915"]
CLAIMS = ["NOMINATED_AND_ACCEPTED_CANDIDATES", "DESIGNATED_SENATORS",
          "OATH_CONSTITUTION_FULFILLED", "FULL_SENATOR_STATUS"]

@pytest.mark.parametrize("ref", REFERENCES)
@pytest.mark.parametrize("claim", CLAIMS)
def test_no_existing_source_stage_can_certify_people(ref, claim):
    result = evaluate_server_claim(evidence_ref=ref, desired_claim=claim,
                                   as_of="2030-01-01T00:00:00Z")
    assert result["eligible"] is False
    assert result["release_grade"] is False

def test_public_catalog_mutation_is_not_trusted():
    snapshot = public_stage_catalog()
    assert snapshot["original_publication_timestamps_verified"] == 0
    for record in snapshot["records"]:
        record["first_public_at"] = "2000-01-01T00:00:00Z"
        record["record_family"] = "BOCCL_CANDIDATE_ACCEPTANCE"
    for ref, claim in [("ESE/000002-01", "NOMINATED_AND_ACCEPTED_CANDIDATES"),
                       ("ESE/000002-02", "DESIGNATED_SENATORS")]:
        result = evaluate_server_claim(evidence_ref=ref, desired_claim=claim,
                                       as_of="2030-01-01T00:00:00Z")
        assert result["reason"] == "FIRST_PUBLIC_AT_UNVERIFIED"

def test_no_unknown_reference_certified():
    result = evaluate_server_claim(evidence_ref="madeup",
                                   desired_claim="FULL_SENATOR_STATUS",
                                   as_of="2030-01-01T00:00:00Z")
    assert result["eligible"] is False
    assert result["reason"] == "UNKNOWN_SERVER_EVIDENCE_REF"
