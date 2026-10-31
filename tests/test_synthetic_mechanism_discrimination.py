"""Adversarial C20 fixture gates; all cases, forecasts and outcomes are fiction."""
from dataclasses import replace
import json

import pytest

from politics_fantasy.procedural_index_contract import GateError
from politics_fantasy.synthetic_mechanism_discrimination import (
    FictionalForecastRow, MODEL_RULE_SHA256, MODEL_NAMES,
    compare_synthetic_mechanism_rivals,
)

PRED = "2026-02-01T12:00:00Z"
FEATURE = "2026-01-30T09:00:00Z"
RESULT = "2026-02-15T12:00:00Z"
EVAL = "2026-03-01T12:00:00Z"
ZONE = "Europe/Madrid"


def rows():
    settings = [
        (0, 1, 1, 1, 0),
        (1, 1, 1, -1, 0),
        (0, 2, 1, 0, 1),
        (1, 0, 2, 0, -1),
    ]
    return tuple(
        FictionalForecastRow(
            case_id=f"SYNTHETIC:C20_{i}",
            holdout_group="SYNTHETIC:HOLDOUT_A",
            prediction_at=PRED, target_event_on="2026-02-10",
            outcome_captured_at=RESULT, outcome_binary=outcome,
            calendar_level=cal, institutional_level=institution,
            internal_history_signal=internal, environmental_signal=environment,
            calendar_captured_at=FEATURE,
            institutional_captured_at=FEATURE,
            internal_captured_at=FEATURE,
            environment_captured_at=FEATURE,
            legal_calendar_zone=ZONE,
        )
        for i, (outcome, cal, institution, internal, environment)
        in enumerate(settings)
    )


def evaluate(data=None, *, at=EVAL, digest=MODEL_RULE_SHA256, zone=ZONE):
    return compare_synthetic_mechanism_rivals(
        rows=rows() if data is None else data,
        evaluation_as_of=at, legal_calendar_zone=zone,
        declared_model_sha256=digest,
    )


def test_frozen_synthetic_rivals_produce_exact_brier_not_real_inference():
    report = evaluate()
    assert set(report["mean_brier_exact"]) == set(MODEL_NAMES)
    assert report["holdout_n"] == 4
    assert report["internal_and_environment_forecasts_differ"] is True
    assert report["model_rule_sha256"] == MODEL_RULE_SHA256
    assert report["competent_empirical_baselines_validated"] is False
    assert report["causal_mechanism_identified"] is False
    assert report["real_historical_first_public_at"] is None
    assert report["AB_scientific_cycles"] == 0
    payload = json.dumps(report)
    assert "SYNTHETIC:C20_" not in payload
    assert "SYNTHETIC:HOLDOUT" not in payload


def test_identical_internal_and_environment_signals_do_not_discriminate():
    same = tuple(replace(x, environmental_signal=x.internal_history_signal)
                 for x in rows())
    result = evaluate(same)
    assert result["internal_and_environment_forecasts_differ"] is False
    assert result["internal_and_environment_brier_differs"] is False
    assert result["mean_brier_exact"]["B2_INTERNAL_MEMORY"] == (
        result["mean_brier_exact"]["B2_ENVIRONMENT"])


@pytest.mark.parametrize("field", [
    "calendar_captured_at", "institutional_captured_at",
    "internal_captured_at", "environment_captured_at",
])
def test_feature_available_only_after_prediction_is_rejected(field):
    data = list(rows())
    with pytest.raises(GateError, match="FEATURE_FROM_FUTURE_LEAKAGE"):
        # The constructor itself rejects a future feature; it must not
        # survive until scoring, even in a synthetic holdout.
        data[0] = replace(data[0], **{field: "2026-02-02T12:00:00Z"})


def test_outcome_after_evaluation_time_rejected():
    with pytest.raises(GateError, match="OUTCOMES_NOT_YET_KNOWN"):
        evaluate(at="2026-02-12T12:00:00Z")


def test_predicted_event_not_in_future_is_rejected():
    with pytest.raises(GateError, match="TARGET_MUST_FOLLOW_PREDICTION"):
        replace(rows()[0], target_event_on="2026-02-01")


def test_outcome_claimed_before_legal_day_completion_rejected():
    with pytest.raises(GateError, match="FUTURE_TARGET_CANNOT_BE_KNOWN"):
        replace(rows()[0], outcome_captured_at="2026-02-10T12:00:00Z")


def test_model_hash_must_match_frozen_contract():
    with pytest.raises(GateError, match="MODEL_CONTRACT_SHA_MISMATCH"):
        evaluate(digest="0" * 64)


def test_duplicate_and_mixed_holdout_groups_rejected():
    data = rows()
    with pytest.raises(GateError, match="DUPLICATED_SYNTHETIC_CASE"):
        evaluate((data[0], data[0]))
    with pytest.raises(GateError, match="HOLDOUT_GROUP_MIXING"):
        evaluate((data[0], replace(data[1], holdout_group="SYNTHETIC:OTHER")))


def test_real_case_ids_and_claims_rejected():
    base = rows()[0]
    with pytest.raises(GateError, match="SYNTHETIC_IDS_ONLY"):
        replace(base, case_id="REAL_ES_007")
    for kwargs in (
        {"official_source_authenticated": True},
        {"official_rights_verified": True},
        {"first_public_at": "2026-02-01T10:00:00Z"},
        {"person_identifier": "REAL_PERSON"},
    ):
        with pytest.raises(GateError, match="REAL_EVIDENCE_CANNOT_BE_ENTERED"):
            replace(base, **kwargs)


def test_invalid_binary_or_outside_feature_domain_rejected():
    for kwargs in (
        {"outcome_binary": 2},
        {"outcome_binary": True},
        {"calendar_level": -1},
        {"institutional_level": 3},
        {"internal_history_signal": 2},
        {"environmental_signal": -2},
    ):
        with pytest.raises(GateError, match="BOUNDED_BINARY_SYNTHETIC"):
            replace(rows()[0], **kwargs)


def test_clock_precision_and_timezone_are_not_silently_coerced():
    with pytest.raises(GateError, match="UNSUPPORTED_SUBMICROSECOND"):
        replace(rows()[0], environment_captured_at="2026-01-30T09:00:00.0000001Z")
    with pytest.raises(GateError, match="TIMESTAMP_NEEDS_TZ"):
        replace(rows()[0], prediction_at="2026-02-01T12:00:00")
    with pytest.raises(GateError, match="INCOMPATIBLE_JURISDICTION"):
        evaluate(zone="UTC")


def test_too_small_or_too_large_holdout_fails_closed():
    with pytest.raises(GateError, match="BOUNDED_SYNTHETIC_HOLDOUT"):
        evaluate((rows()[0],))
    with pytest.raises(GateError, match="BOUNDED_SYNTHETIC_HOLDOUT"):
        evaluate(rows() * 17)
