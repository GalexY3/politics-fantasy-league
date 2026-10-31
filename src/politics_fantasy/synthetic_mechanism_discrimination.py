"""C20 synthetic mechanism-rival discrimination; NOT a real forecast.

Five frozen, intentionally simple probability rules are compared on a wholly
fictional holdout. Internal memory and external conditions are distinct
features, each with its own availability clock. Brier differences say nothing
about causal effects or the predictive quality of Spanish political models.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
import json

from .procedural_index_contract import (
    GateError, utc, day, legal_day_completed, legal_civil_date,
)
from .synthetic_registration_graph import SYNTHETIC_ID

MODEL_VERSION = "pfl.synthetic_mechanism_rivals.v1"
MODEL_NAMES = (
    "B0_CALENDAR",
    "B1_CALENDAR_AND_INSTITUTION",
    "B2_INTERNAL_MEMORY",
    "B2_ENVIRONMENT",
    "B2_INTERNAL_AND_ENVIRONMENT",
)
MAX_ROWS = 64
MODEL_RULE = {
    "prior": "1/2",
    "calendar": "1/10 per (level-1)",
    "institution": "1/10 per (level-1)",
    "internal": "1/10 per signal",
    "environment": "1/10 per signal",
    "model_names": MODEL_NAMES,
    "version": MODEL_VERSION,
}
MODEL_RULE_SHA256 = sha256(
    json.dumps(MODEL_RULE, sort_keys=True, separators=(",", ":")).encode()
).hexdigest()


@dataclass(frozen=True)
class FictionalForecastRow:
    case_id: str
    holdout_group: str
    prediction_at: str
    target_event_on: str
    outcome_captured_at: str
    outcome_binary: int
    calendar_level: int
    institutional_level: int
    internal_history_signal: int
    environmental_signal: int
    calendar_captured_at: str
    institutional_captured_at: str
    internal_captured_at: str
    environment_captured_at: str
    legal_calendar_zone: str
    first_public_at: None = None
    official_source_authenticated: bool = False
    official_rights_verified: bool = False
    person_identifier: None = None

    def __post_init__(self) -> None:
        if (type(self.case_id) is not str
                or SYNTHETIC_ID.fullmatch(self.case_id) is None
                or type(self.holdout_group) is not str
                or SYNTHETIC_ID.fullmatch(self.holdout_group) is None):
            raise GateError("C20_SYNTHETIC_IDS_ONLY")
        if (self.first_public_at is not None
                or self.official_source_authenticated is not False
                or self.official_rights_verified is not False
                or self.person_identifier is not None):
            raise GateError("C20_REAL_EVIDENCE_CANNOT_BE_ENTERED")
        if (type(self.outcome_binary) is not int
                or self.outcome_binary not in (0, 1)
                or type(self.calendar_level) is not int
                or self.calendar_level not in (0, 1, 2)
                or type(self.institutional_level) is not int
                or self.institutional_level not in (0, 1, 2)
                or type(self.internal_history_signal) is not int
                or self.internal_history_signal not in (-1, 0, 1)
                or type(self.environmental_signal) is not int
                or self.environmental_signal not in (-1, 0, 1)):
            raise GateError("C20_BOUNDED_BINARY_SYNTHETIC_FEATURES_REQUIRED")
        prediction = utc(self.prediction_at)
        outcome_at = utc(self.outcome_captured_at)
        if legal_civil_date(self.prediction_at, self.legal_calendar_zone) >= day(self.target_event_on):
            raise GateError("C20_TARGET_MUST_FOLLOW_PREDICTION_LOCAL_DAY")
        if (outcome_at <= prediction or not legal_day_completed(
                cut_on=self.target_event_on,
                as_of=self.outcome_captured_at,
                legal_calendar_zone=self.legal_calendar_zone)):
            raise GateError("C20_FUTURE_TARGET_CANNOT_BE_KNOWN_BEFORE_DAY_END")
        for feature_seen in (
            self.calendar_captured_at,
            self.institutional_captured_at,
            self.internal_captured_at,
            self.environment_captured_at,
        ):
            if utc(feature_seen) > prediction:
                raise GateError("C20_FEATURE_FROM_FUTURE_LEAKAGE")


def _forecast(row: FictionalForecastRow) -> dict[str, Fraction]:
    p0 = Fraction(1, 2) + Fraction(row.calendar_level - 1, 10)
    p1 = p0 + Fraction(row.institutional_level - 1, 10)
    internal = Fraction(row.internal_history_signal, 10)
    environment = Fraction(row.environmental_signal, 10)
    probabilities = {
        "B0_CALENDAR": p0,
        "B1_CALENDAR_AND_INSTITUTION": p1,
        "B2_INTERNAL_MEMORY": p1 + internal,
        "B2_ENVIRONMENT": p1 + environment,
        "B2_INTERNAL_AND_ENVIRONMENT": p1 + internal + environment,
    }
    if any(not 0 < p < 1 for p in probabilities.values()):
        raise GateError("C20_INVALID_FROZEN_MODEL_PROBABILITY")
    return probabilities


def compare_synthetic_mechanism_rivals(
    *, rows: tuple[FictionalForecastRow, ...],
    evaluation_as_of: str, legal_calendar_zone: str,
    declared_model_sha256: str,
) -> dict:
    """Exact Brier evaluation of frozen fictional rules, with temporal gates.

    This is a technical contrast, never an empirical claim of identification.
    Distinguish divergent forecast vectors from unequal realized scores.
    """
    if (type(rows) is not tuple or not 2 <= len(rows) <= MAX_ROWS
            or any(type(x) is not FictionalForecastRow for x in rows)):
        raise GateError("C20_BOUNDED_SYNTHETIC_HOLDOUT_REQUIRED")
    if type(declared_model_sha256) is not str or declared_model_sha256 != MODEL_RULE_SHA256:
        raise GateError("C20_MODEL_CONTRACT_SHA_MISMATCH")
    if len({x.case_id for x in rows}) != len(rows):
        raise GateError("C20_DUPLICATED_SYNTHETIC_CASE")
    if len({x.holdout_group for x in rows}) != 1:
        raise GateError("C20_HOLDOUT_GROUP_MIXING")
    at = utc(evaluation_as_of)
    if any(x.legal_calendar_zone != legal_calendar_zone for x in rows):
        raise GateError("C20_INCOMPATIBLE_JURISDICTION")
    if any(utc(x.outcome_captured_at) > at for x in rows):
        raise GateError("C20_OUTCOMES_NOT_YET_KNOWN_AT_EVALUATION")
    if any(utc(x.prediction_at) >= at for x in rows):
        raise GateError("C20_FUTURE_PREDICTION_IN_HOLDOUT")
    predictions = tuple(_forecast(x) for x in rows)
    brier = {}
    for model in MODEL_NAMES:
        loss = sum(
            ((pred[model] - row.outcome_binary) ** 2
             for row, pred in zip(rows, predictions)),
            Fraction(0),
        ) / len(rows)
        brier[model] = str(loss)
    internal_diffs = any(
        f["B2_INTERNAL_MEMORY"] != f["B2_ENVIRONMENT"]
        for f in predictions
    )
    score_difference = (
        Fraction(brier["B2_INTERNAL_MEMORY"])
        != Fraction(brier["B2_ENVIRONMENT"])
    )
    return {
        "schema": MODEL_VERSION,
        "evidence_class": "SYNTHETIC_HOLDOUT_TECHNICAL_CHECK_ONLY",
        "model_rule_sha256": MODEL_RULE_SHA256,
        "holdout_n": len(rows),
        "mean_brier_exact": brier,
        "internal_and_environment_forecasts_differ": internal_diffs,
        "internal_and_environment_brier_differs": score_difference,
        "causal_mechanism_identified": False,
        "competent_empirical_baselines_validated": False,
        "real_historical_first_public_at": None,
        "real_population_denominator": None,
        "source_rights_verified": False,
        "real_outcomes_accessed": False,
        "political_actor_ratings": None,
        "AB_scientific_cycles": 0,
    }
