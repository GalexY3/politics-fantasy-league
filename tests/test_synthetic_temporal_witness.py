"""R15 adversarial clocks: no future metadata in historical cuts."""
import pytest

from politics_fantasy.procedural_index_contract import GateError
from politics_fantasy.synthetic_temporal_witness import (
    KnowledgeInterval, DocumentaryClaim, audit_documentary_knowledge as audit)

PRE="2026-10-11T00:00:00Z"
POST="2026-11-01T00:00:00Z"
DAY=KnowledgeInterval("2026-10-31T00:00:00Z","2026-11-01T00:00:00Z")


def claim(**changes):
    d=dict(claim_id="SYNTHETIC:SAIP_CATALOGUE_VERSION_10OCT",
        source_id="SYNTHETIC:SAIP",dataset_id="SYNTHETIC:YJPN",
        claim_type="CATALOGUE_RESTORE_METADATA",discovered=DAY,
        captured_at="2026-10-31T23:15:00Z",
        publisher_backend="SYNTHETIC:SAME_BACKEND",
        publisher_edition_at="2026-10-10T13:00:00Z")
    d.update(changes)
    return DocumentaryClaim(**d)


def test_past_editorial_restore_is_invisible_before_later_discovery():
    before=audit(claims=(claim(),),as_of=PRE)
    assert before["status"]=="NO_DOCUMENTARY_KNOWLEDGE_AT_CUT"
    assert before["visible_restore_labels_count"] is None
    assert before["visible_sources_count"] is None
    assert before["claim_original_sha256"] is None
    assert before["first_public_at"] is None


def test_imprecise_discovery_window_and_capture_both_gate_visibility():
    assert audit(claims=(claim(),),as_of="2026-10-31T23:59:59Z")[
        "visible_claim_count"] is None
    x=audit(claims=(claim(),),as_of=POST)
    assert x["status"]=="DOCUMENTARY_ASSERTIONS_VISIBLE_NOT_EMPIRICAL"
    assert x["visible_claim_count"]==1
    assert x["visible_restore_labels_count"]==1
    assert x["first_public_at"] is None
    assert not x["independent_archive_certified"]


def test_capture_time_more_conservative_than_window_upper():
    c=claim(captured_at="2026-11-03T12:00:00Z")
    assert audit(claims=(c,),as_of="2026-11-02T12:00:00Z")[
        "visible_claim_count"] is None
    assert audit(claims=(c,),as_of="2026-11-03T12:00:00Z")[
        "visible_claim_count"]==1


def test_missing_upper_bound_or_capture_never_exposes_edition():
    c=claim(discovered=KnowledgeInterval(None,None),captured_at=None)
    assert audit(claims=(c,),as_of="2040-01-01T00:00:00Z")[
        "visible_claim_count"] is None
    c=claim(captured_at=None)
    assert audit(claims=(c,),as_of="2040-01-01T00:00:00Z")[
        "visible_claim_count"] is None


def test_lookahead_cannot_be_resurrected_by_forged_earlier_publisher_date():
    old=claim(publisher_edition_at="2015-01-01T00:00:00Z",
              event_at="2015-01-01T00:00:00Z",
              document_dated_at="2015-01-02T00:00:00Z")
    assert audit(claims=(old,),as_of="2020-01-01T00:00:00Z")[
        "status"]=="NO_DOCUMENTARY_KNOWLEDGE_AT_CUT"


def test_same_claim_repeated_is_one_witness_not_two_independent_sightings():
    result=audit(claims=(claim(),claim()),as_of=POST)
    assert result["visible_claim_count"]==1
    assert result["visible_restore_labels_count"]==1
    assert not result["independent_archive_certified"]


def test_later_conflicting_claim_quarantines_later_without_revising_old_cut():
    first=claim(discovered=KnowledgeInterval(
        "2026-10-01T00:00:00Z","2026-10-02T00:00:00Z"),
        captured_at="2026-10-02T00:00:00Z")
    later=claim(dataset_id="SYNTHETIC:DIFFERENT_DATASET")
    early=audit(claims=(first,later),as_of="2026-10-11T00:00:00Z")
    assert early["visible_claim_count"]==1
    future=audit(claims=(first,later),as_of=POST)
    assert future["status"]=="VISIBLE_DOCUMENTARY_CLAIMS_QUARANTINED"
    assert future["visible_claim_count"] is None
    assert future["claim_original_sha256"] is None


def test_multiple_restore_labels_are_not_two_originals_even_with_sha_claim():
    a=claim(claimed_original_sha256="a"*64)
    b=claim(claim_id="SYNTHETIC:SAIP_24OCT",
        publisher_edition_at="2026-10-24T13:00:00Z",
        claimed_original_sha256="b"*64)
    x=audit(claims=(a,b),as_of=POST)
    assert x["visible_restore_labels_count"]==2
    assert x["comparable_historical_original_pairs"] is None
    assert x["first_public_at"] is None
    assert not x["originals_verified"]


def test_distinct_publishers_same_backend_are_not_independent():
    b=claim(claim_id="SYNTHETIC:SECOND_INDEX",
        claim_type="INDEPENDENT_ARCHIVE_INDEX_CANDIDATE",
        source_id="SYNTHETIC:SECOND_PUBLISHER")
    x=audit(claims=(claim(),b),as_of=POST)
    assert x["visible_sources_count"]==2
    assert not x["independent_archive_certified"]
    assert x["all_received_denominator"] is None


@pytest.mark.parametrize("start,end",[
    (None,"2026-10-31T00:00:00Z"),
    ("2026-10-31T00:00:00Z",None),
])
def test_unknown_partial_interval_must_not_be_guessed(start,end):
    with pytest.raises(GateError, match="UNBOUNDED_DISCOVERY_INTERVAL"):
        KnowledgeInterval(start,end)


def test_reversed_invalid_and_too_early_capture_rejected():
    with pytest.raises(GateError):
        KnowledgeInterval("2026-11-01T00:00:00Z","2026-10-31T00:00:00Z")
    with pytest.raises(GateError):
        KnowledgeInterval(None,"2026-11-01T00:00:00Z")
    with pytest.raises(GateError):
        claim(captured_at="2026-10-30T13:00:00Z")
    with pytest.raises(GateError):
        claim(source_id="REAL_SAIP")
    with pytest.raises(GateError):
        claim(original_verified=True)
    with pytest.raises(GateError):
        claim(first_public_at="2026-10-10T13:00:00Z")
