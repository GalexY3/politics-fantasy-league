"""R19 targeted regressions for two prepatch failures, wholly SYNTHETIC.

The prepatch failure witnesses and frozen hashes are retained in the separate
worker scratch. These tests assert the repaired temporal contracts; they do
not establish anything about an external population or consume AB cycles.
"""
from dataclasses import replace

import pytest

from politics_fantasy.procedural_index_contract import GateError, utc
from politics_fantasy.synthetic_registration_graph import (
    OfficialStageKey, StageVersion, audit_graph,
)
from politics_fantasy.synthetic_temporal_witness import (
    KnowledgeInterval, DocumentaryClaim, audit_documentary_knowledge,
)


KEY = OfficialStageKey(
    "SYNTHETIC:REGIONAL_COURT", "SYNTHETIC:REGIME_2020",
    "SYNTHETIC:APPEALS", "REGISTRATION", "SYNTHETIC:ENTRY_Q",
)


def stage(revision, event, known, captured, sha):
    return StageVersion(
        key=KEY, revision=revision, event_on=event, document_on=event,
        publisher_edition_at=None,
        observed=KnowledgeInterval(known, known),
        captured_at=captured, original_sha_claim=sha * 64,
    )


def audit(records, as_of):
    return audit_graph(
        records=tuple(records), edges=(), cut_on="2020-12-31", as_of=as_of,
    )


def test_latest_known_revision_moves_event_out_of_retrospective_cut():
    old = stage("SYNTHETIC:V1", "2020-06-01",
                "2026-01-01T00:00:00Z", "2026-01-02T12:00:00Z", "a")
    corrected = stage("SYNTHETIC:V2", "2021-06-01",
                      "2026-02-01T00:00:00Z", "2026-02-02T12:00:00Z", "b")
    before = audit([old, corrected], "2026-01-15T00:00:00Z")
    after = audit([old, corrected], "2026-03-01T00:00:00Z")
    assert before["visible_stages"]["REGISTRATION"] == 1
    assert before["revision_keys"] == 1
    assert after["visible_stages"]["REGISTRATION"] == 0
    assert after["visible_stage_total"] == 0
    assert after["revision_keys"] == 2
    assert after["registered_at_risk_population_certified"] is False


def test_later_known_revision_can_move_event_inside_old_cut():
    old = stage("SYNTHETIC:V1", "2021-06-01",
                "2026-01-01T00:00:00Z", "2026-01-02T12:00:00Z", "a")
    corrected = stage("SYNTHETIC:V2", "2020-06-01",
                      "2026-02-01T00:00:00Z", "2026-02-02T12:00:00Z", "b")
    assert audit([old, corrected], "2026-01-15T00:00:00Z")[
        "visible_stages"]["REGISTRATION"] == 0
    assert audit([old, corrected], "2026-03-01T00:00:00Z")[
        "visible_stages"]["REGISTRATION"] == 1


def test_unseen_revision_never_rewrites_older_knowledge():
    old = stage("SYNTHETIC:V1", "2020-06-01",
                "2026-01-01T00:00:00Z", "2026-01-02T12:00:00Z", "a")
    correction = stage("SYNTHETIC:V2", "2021-06-01",
                       "2026-02-01T00:00:00Z", "2026-02-02T12:00:00Z", "b")
    assert audit([old, correction], "2026-01-15T00:00:00Z") == audit(
        [old], "2026-01-15T00:00:00Z")


@pytest.mark.parametrize("stamp", [
    "2026-11-01T00:00:00.000000001Z",
    "2026-11-01T00:00:00.000000000Z",
    "2026-11-01T00:00:00.1234567+01:00",
    "2026-11-01T00:00:00,123456789+01:00",
])
def test_precision_beyond_microseconds_is_rejected_not_truncated(stamp):
    with pytest.raises(GateError, match="UNSUPPORTED_SUBMICROSECOND_TIMESTAMP"):
        utc(stamp)


def test_nano_precision_in_claim_or_asof_is_rejected_before_visibility():
    late = "2026-11-01T00:00:00.000000001Z"
    with pytest.raises(GateError, match="UNSUPPORTED_SUBMICROSECOND_TIMESTAMP"):
        DocumentaryClaim(
            claim_id="SYNTHETIC:NANO", source_id="SYNTHETIC:SOURCE",
            dataset_id="SYNTHETIC:SET", claim_type="CATALOGUE_ENTRY",
            discovered=KnowledgeInterval(late, late), captured_at=late,
            claimed_original_sha256="a" * 64,
        )
    with pytest.raises(GateError, match="UNSUPPORTED_SUBMICROSECOND_TIMESTAMP"):
        audit_documentary_knowledge(
            claims=(), as_of="2026-11-01T00:00:00.000000000Z",
        )


def test_valid_six_digit_fractional_and_offset_stamps_remain_supported():
    assert utc("2026-11-01T01:00:00.000001+01:00") == utc(
        "2026-11-01T00:00:00.000001Z")
    assert utc("2026-11-01T00:00:00Z") < utc(
        "2026-11-01T00:00:00.000001Z")


def test_later_well_resolved_document_is_hidden_as_negative_control():
    captured = "2026-11-01T00:00:01Z"
    claim = DocumentaryClaim(
        claim_id="SYNTHETIC:CLAIM_NANO",
        source_id="SYNTHETIC:CATALOGUE_A",
        dataset_id="SYNTHETIC:DATASET_A", claim_type="CATALOGUE_ENTRY",
        discovered=KnowledgeInterval(captured, captured),
        captured_at=captured, claimed_original_sha256="a" * 64,
    )
    result = audit_documentary_knowledge(
        claims=(claim,), as_of="2026-11-01T00:00:00Z")
    assert result["status"] == "NO_DOCUMENTARY_KNOWLEDGE_AT_CUT"
    assert result["visible_claim_count"] is None
    assert result["first_public_at"] is None
    assert result["scientific_cycles"] == 0
