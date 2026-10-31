"""Only synthetic witness contracts, never external institutional assertions."""
from dataclasses import replace
import json
import pytest

from politics_fantasy.documentary_availability_intervals import RevisionWitness
from politics_fantasy.procedural_index_contract import GateError

def witness(**overrides):
    x=dict(revision_id="SYNTHETIC:REVIEW01",original_sha256="a"*64,
           captured_at="2026-10-31T06:30:20Z",
           captured_clock_precision="SECOND",
           claimed_event_on="2020-02-02",documentary_date="2020-02-10")
    return RevisionWitness(**(x|overrides))

def test_old_event_and_document_dates_do_not_make_past_predictor():
    w=witness()
    cut=w.temporal_report(as_of="2020-12-31T23:59:59Z",
                          purpose="HISTORICAL_PUBLIC_PREDICTOR")
    assert cut["status"]=="NOT_ADMITTED_AT_CUT"
    assert cut["revision_id"] is None
    assert cut["original_sha256"] is None
    assert cut["event_on"] is None
    assert not cut["public_revision_usable"]
    current=w.temporal_report(as_of="2026-11-01T00:00:00Z",
                              purpose="HISTORICAL_PUBLIC_PREDICTOR")
    assert current["status"]=="NOT_ADMITTED_AT_CUT"
    assert current["first_public_at"] is None

def test_local_capture_safe_after_precision_and_no_leak():
    w=witness()
    early=w.temporal_report(as_of="2026-10-31T06:30:20.999999Z",
                            purpose="LOCAL_OBSERVATORY")
    assert early["revision_id"] is None
    seen=w.temporal_report(as_of="2026-10-31T06:30:21Z",
                           purpose="LOCAL_OBSERVATORY")
    assert seen["status"]=="LOCAL_OBSERVATION_ONLY"
    assert seen["revision_id"]=="SYNTHETIC:REVIEW01"
    assert seen["public_revision_usable"] is False
    assert seen["public_available_by"] is None
    assert seen["first_public_at"] is None

def test_date_precision_is_next_utc_midnight_not_beginning_of_day():
    w=witness(captured_at="2026-10-31T10:52:00Z",captured_clock_precision="DATE")
    assert not w.temporal_report(as_of="2026-10-31T23:59:59Z",
                                 purpose="LOCAL_OBSERVATORY")["public_revision_usable"]
    yes=w.temporal_report(as_of="2026-11-01T00:00:00Z",
                          purpose="LOCAL_OBSERVATORY")
    assert yes["status"]=="LOCAL_OBSERVATION_ONLY"
    assert yes["observed_local_safe_by"]=="2026-11-01T00:00:00+00:00"

def test_reviewed_historical_archive_bounds_public_availability_but_not_exact_first():
    w=witness(positive_basis="TRUSTED_ARCHIVE_REVISION_WITNESS",
              independently_reviewed=True,
              witnessed_public_by="2023-01-01T12:00:00Z",
              witnessed_not_public_before="2022-01-01T12:00:00Z",
              negative_basis="TRUSTED_PREVIOUS_COMPLETE_INDEX_NEGATIVE_WITNESS")
    for t in ["2022-01-01T12:00:00Z","2022-12-31T23:59:59Z"]:
        d=w.temporal_report(as_of=t,purpose="HISTORICAL_PUBLIC_PREDICTOR")
        assert not d["public_revision_usable"]
    d=w.temporal_report(as_of="2023-01-01T12:00:00Z",purpose="HISTORICAL_PUBLIC_PREDICTOR")
    assert d["status"]=="BOUNDED_AVAILABILITY"
    assert d["not_public_before"]=="2022-01-01T12:00:00+00:00"
    assert d["public_available_by"]=="2023-01-01T12:00:00+00:00"
    assert d["first_public_at"] is None
    assert not d["exact_first_public_at_verified"]
    assert d["observed_local_safe_by"] is None

def test_self_attested_historical_bounded_time_is_not_enough():
    with pytest.raises(GateError,match="ARCHIVAL_WITNESS_NOT_REVIEWED"):
        witness(positive_basis="TRUSTED_ARCHIVE_REVISION_WITNESS",
                witnessed_public_by="2023-01-01T12:00:00Z",
                independently_reviewed=False)
    with pytest.raises(GateError,match="CAPTURE_CANNOT_ATTEST_HISTORICAL_PUBLICATION"):
        witness(witnessed_public_by="2023-01-01T12:00:00Z")

def test_negative_witness_requires_full_previous_index_evidence():
    with pytest.raises(GateError,match="NEGATIVE_WITNESS_NOT_COMPLETE_OR_REVIEWED"):
        witness(witnessed_not_public_before="2020-01-01T00:00:00Z",
                independently_reviewed=False)
    with pytest.raises(GateError,match="ORPHAN_NEGATIVE_WITNESS_BASIS"):
        witness(negative_basis="TRUSTED_PREVIOUS_COMPLETE_INDEX_NEGATIVE_WITNESS")
    with pytest.raises(GateError,match="INCONSISTENT_PUBLICATION_INTERVAL"):
        witness(positive_basis="TRUSTED_ARCHIVE_REVISION_WITNESS",
                witnessed_public_by="2023-01-01T00:00:00Z",
                independently_reviewed=True,
                witnessed_not_public_before="2024-01-01T00:00:00Z",
                negative_basis="TRUSTED_PREVIOUS_COMPLETE_INDEX_NEGATIVE_WITNESS")

def test_publisher_date_can_never_be_auto_promoted():
    with pytest.raises(GateError,match="EXACT_FIRST_PUBLICATION_NOT_ESTABLISHED"):
        witness(exact_first_public_at="2020-02-10T00:00:00Z")
    with pytest.raises(GateError,match="UNSAFE_POSITIVE_WITNESS_BASIS"):
        witness(positive_basis="DOCUMENT_DATE_ONLY")

def test_archival_publication_after_capture_is_impossible():
    with pytest.raises(GateError,match="WITNESS_POSTDATES_ITS_CAPTURE"):
        witness(positive_basis="TRUSTED_ARCHIVE_REVISION_WITNESS",
                independently_reviewed=True,witnessed_public_by="2027-01-01T00:00:00Z")

def test_invalid_cut_and_purpose_are_rejected():
    w=witness()
    with pytest.raises(GateError,match="INVALID_TIMESTAMP"):
        w.temporal_report(as_of="2020",purpose="LOCAL_OBSERVATORY")
    with pytest.raises(GateError,match="INVALID_TEMPORAL_PURPOSE"):
        w.temporal_report(as_of="2026-11-01T00:00:00Z",purpose="UNAUTHORIZED")


def test_real_historical_archival_witness_cannot_self_authorize():
    with pytest.raises(GateError,match="REAL_ARCHIVAL_EVIDENCE_REQUIRES_SEPARATE_TRUSTED_REGISTRY"):
        witness(revision_id="PARLIAMENT_REAL_01",
                source_evidence_class="REAL_LOCAL_CAPTURE_ONLY",
                positive_basis="TRUSTED_ARCHIVE_REVISION_WITNESS",
                witnessed_public_by="2023-01-01T00:00:00Z",
                independently_reviewed=True)
    with pytest.raises(GateError,match="SYNTHETIC_WITNESS_NEEDS_LAB_NAMESPACE"):
        witness(revision_id="PARLIAMENT_REAL_01")


def test_fictional_archive_witness_must_not_backdate_future_event_or_document():
    # R16 counterexample: revision claimed public in 2020, yet the *same*
    # purported original describes a later registration and document in 2025.
    for future in ({"claimed_event_on":"2025-02-01"},
                   {"documentary_date":"2025-02-10"}):
        with pytest.raises(GateError,match="PUBLIC_WITNESS_PRECEDES_DATED_CONTENT"):
            witness(positive_basis="TRUSTED_ARCHIVE_REVISION_WITNESS",
                    independently_reviewed=True,
                    witnessed_public_by="2020-10-01T12:00:00Z",**future)


def test_public_witness_at_start_of_same_day_is_not_positive_day_witness():
    with pytest.raises(GateError,match="PUBLIC_WITNESS_PRECEDES_DATED_CONTENT"):
        witness(positive_basis="TRUSTED_ARCHIVE_REVISION_WITNESS",
                independently_reviewed=True,
                claimed_event_on="2023-01-01",
                witnessed_public_by="2023-01-01T00:01:00Z")
    valid=witness(positive_basis="TRUSTED_ARCHIVE_REVISION_WITNESS",
                  independently_reviewed=True,claimed_event_on="2023-01-01",
                  documentary_date="2023-01-01",
                  witnessed_public_by="2023-01-02T00:00:00Z")
    assert valid.temporal_report(as_of="2023-01-02T00:00:00Z",
                                 purpose="HISTORICAL_PUBLIC_PREDICTOR")[
                                     "public_revision_usable"] is True


def test_local_capture_cannot_claim_future_dated_source_content():
    with pytest.raises(GateError,match="SOURCE_CONTAINS_FUTURE_DATED_EVENT_OR_DOCUMENT"):
        witness(claimed_event_on="2027-01-01")
    with pytest.raises(GateError,match="SOURCE_CONTAINS_FUTURE_DATED_EVENT_OR_DOCUMENT"):
        witness(documentary_date="2027-01-01")
