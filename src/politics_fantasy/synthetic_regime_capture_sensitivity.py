"""R19 / C14 — artificial regime/channel sensitivity to selective observation.

This is an exact, *assumption-conditional* partial-identification exercise.
It is not an estimator for official political sources. A change in an observed
stock/flow may be produced by altered channel coverage, institutional remit or
actual entry volume. The module never verifies coverage, legal competence,
first_public_at, individual episodes, or a real all-received denominator.

Under the deterministic *fictional* premise L <= observed/received <= U,
observed M yields ceil(M/U) <= received <= floor(M/L). L=0 leaves its upper
bound unknown. Different period/channel coverage assumptions may be compatible
with exactly the same observed publications and disagree about the sign of an
entry trend. Statistical uncertainty and causal attribution are not included.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from fractions import Fraction

from .procedural_index_contract import (
    GateError, LEGAL_CIVIL_ZONES, day, legal_civil_date, legal_day_completed, utc,
)

CHANNELS = frozenset({"PAPER", "ELECTRONIC"})
REGIMES = frozenset({"BEFORE_REFORM", "AFTER_REFORM"})
MAX_VISIBLE = 1_000_000
TREND_SIGNS = frozenset({
    "RISING_UNDER_ASSUMPTIONS", "FALLING_UNDER_ASSUMPTIONS",
    "EQUAL_UNDER_ASSUMPTIONS", "NOT_SIGN_IDENTIFIED_UNDER_ASSUMPTIONS",
})


def _ceiling_ratio(n: int, share: Fraction) -> int:
    ratio = Fraction(n, 1) / share
    return -(-ratio.numerator // ratio.denominator)


def _trend_from_bounds(old_low: int, old_high: int | None,
                       new_low: int, new_high: int | None) -> str:
    if old_high is not None and new_low > old_high:
        return "RISING_UNDER_ASSUMPTIONS"
    if new_high is not None and old_low > new_high:
        return "FALLING_UNDER_ASSUMPTIONS"
    if old_low == old_high == new_low == new_high:
        return "EQUAL_UNDER_ASSUMPTIONS"
    return "NOT_SIGN_IDENTIFIED_UNDER_ASSUMPTIONS"


@dataclass(frozen=True)
class FictionalCaptureStratum:
    """A deliberately *fictional* reporting cell, not an official extract."""

    fixture_id: str
    regime: str
    channel: str
    first_day: str
    last_day: str
    locally_captured_at: str
    observed_published: int
    assumed_min_capture_share: Fraction
    assumed_max_capture_share: Fraction
    legal_calendar_zone: str
    first_public_at: None = None
    independent_registry_total: None = None

    def __post_init__(self) -> None:
        if (type(self.fixture_id) is not str
                or not self.fixture_id.startswith("SYNTHETIC:")
                or len(self.fixture_id) > 100 or self.regime not in REGIMES
                or self.channel not in CHANNELS
                or type(self.observed_published) is not int
                or not 0 <= self.observed_published <= MAX_VISIBLE
                or self.first_public_at is not None
                or self.independent_registry_total is not None):
            raise GateError("FICTIONAL_CAPTURE_STRATA_ONLY")
        if day(self.first_day) > day(self.last_day):
            raise GateError("INVERTED_SYNTHETIC_REGIME_WINDOW")
        if (type(self.assumed_min_capture_share) is not Fraction
                or type(self.assumed_max_capture_share) is not Fraction
                or not 0 <= self.assumed_min_capture_share
                <= self.assumed_max_capture_share <= 1):
            raise GateError("EXACT_SYNTHETIC_COVERAGE_SHARES_REQUIRED")
        if (self.observed_published > 0
                and self.assumed_max_capture_share == 0):
            raise GateError("POSITIVE_OBSERVATION_IMPOSSIBLE_AT_ZERO_COVERAGE")
        # A retrospective assertion about an *entire* civil window requires a
        # capture only after its LAST jurisdictional day has completed.
        legal_civil_date(self.locally_captured_at, self.legal_calendar_zone)
        if not legal_day_completed(cut_on=self.last_day,
                                   as_of=self.locally_captured_at,
                                   legal_calendar_zone=self.legal_calendar_zone):
            raise GateError("REGIME_WINDOW_NOT_COMPLETE_AT_CAPTURE")

    def partial_intake_bounds(self) -> tuple[int, int | None]:
        """Worst-case integer range under *supplied*, not proven, coverage."""
        if self.assumed_max_capture_share == 0:
            return 0, None
        low = _ceiling_ratio(self.observed_published,
                             self.assumed_max_capture_share)
        high = (None if self.assumed_min_capture_share == 0 else
                int(Fraction(self.observed_published, 1)
                    / self.assumed_min_capture_share))
        if high is not None and high < low:
            raise GateError("INFEASIBLE_INTEGER_COVERAGE_WINDOW")
        return low, high


def audit_regime_capture(*, strata: tuple[FictionalCaptureStratum, ...],
                         reform_on: str, as_of: str,
                         legal_calendar_zone: str) -> dict:
    """Find exact synthetic bounds, not real causal/temporal effects."""
    if (type(strata) is not tuple or len(strata) != 4
            or any(type(c) is not FictionalCaptureStratum for c in strata)):
        raise GateError("FOUR_SYNTHETIC_REGIME_CHANNEL_CELLS_REQUIRED")
    if len({c.fixture_id for c in strata}) != 4:
        raise GateError("REPLAYED_SYNTHETIC_STRATUM_ID")
    observed_cells = {(c.regime, c.channel) for c in strata}
    if observed_cells != {(r, ch) for r in REGIMES for ch in CHANNELS}:
        raise GateError("MISSING_OR_DUPLICATE_SYNTHETIC_CHANNEL")
    cut = day(reform_on)
    at = utc(as_of)
    for c in strata:
        if c.legal_calendar_zone != legal_calendar_zone:
            raise GateError("MIXED_REGIME_LEGAL_CALENDARS")
        if utc(c.locally_captured_at) > at:
            raise GateError("FUTURE_STRATUM_CAPTURE_ASOF_LOOKAHEAD")
        if (c.regime == "BEFORE_REFORM" and day(c.last_day) >= cut
                or c.regime == "AFTER_REFORM" and day(c.first_day) < cut):
            raise GateError("REGIME_WINDOW_SPANS_COMPETENCE_CHANGE")
    for regime in REGIMES:
        group = [c for c in strata if c.regime == regime]
        if len({(c.first_day, c.last_day) for c in group}) != 1:
            raise GateError("INCOMPATIBLE_CHANNEL_EXPOSURE_WINDOWS")
    pre = next(c for c in strata if c.regime == "BEFORE_REFORM")
    post = next(c for c in strata if c.regime == "AFTER_REFORM")
    if (day(pre.last_day) + timedelta(days=1) != cut
            or day(post.first_day) != cut):
        raise GateError("NONCONTIGUOUS_REGIME_EXPOSURE_WINDOWS")
    if ((day(pre.last_day) - day(pre.first_day))
            != (day(post.last_day) - day(post.first_day))):
        raise GateError("UNEQUAL_REGIME_EXPOSURE_DAYS_NOT_COMPARABLE")
    periods = {}
    for regime in sorted(REGIMES):
        cells = [c for c in strata if c.regime == regime]
        bounds = [c.partial_intake_bounds() for c in cells]
        lower = sum(lo for lo, _ in bounds)
        upper = (sum(hi for _, hi in bounds)
                 if all(hi is not None for _, hi in bounds) else None)
        periods[regime] = {
            "visible_source_local_documents": sum(c.observed_published for c in cells),
            "hypothetical_intake_lower": lower,
            "hypothetical_intake_upper": upper,
            "missingness_or_right_censoring_attested": False,
            "all_received_population_certified": False,
        }
    before = periods["BEFORE_REFORM"]
    after = periods["AFTER_REFORM"]
    old_low, old_high = before["hypothetical_intake_lower"], before["hypothetical_intake_upper"]
    new_low, new_high = after["hypothetical_intake_lower"], after["hypothetical_intake_upper"]
    sign = _trend_from_bounds(old_low, old_high, new_low, new_high)
    return {
        "schema": "pfl.synthetic_regime_capture_sensitivity.v1",
        "evidence_class": "SYNTHETIC_LAB_ONLY",
        "legal_calendar_zone": legal_calendar_zone,
        "reform_on": reform_on,
        "as_of": as_of,
        "periods": periods,
        "hypothetical_trend_sign": sign,
        "capture_shares_are_proven_real": False,
        "real_registration_population_attested": False,
        "real_negative_pending_or_censored_attested": False,
        "first_public_at": None,
        "real_causal_mechanism_identified": False,
        "cross_regime_case_links_certified": False,
        "regime_change_is_causal_exposure": False,
        "AB_scientific_cycles": 0,
        "personal_case_ids_or_outcomes": None,
    }


def _check_synthetic_capture_report(report: dict) -> None:
    """Reject mutated or malformed lab summaries before an equivalence claim.

    This checks internal arithmetic, not authenticity of an external source.
    It does not certify that any assumed capture fractions are empirically true.
    """
    if (type(report) is not dict or set(report) != {
            "schema", "evidence_class", "legal_calendar_zone", "reform_on",
            "as_of", "periods", "hypothetical_trend_sign",
            "capture_shares_are_proven_real", "real_registration_population_attested",
            "real_negative_pending_or_censored_attested", "first_public_at",
            "real_causal_mechanism_identified", "cross_regime_case_links_certified",
            "regime_change_is_causal_exposure", "AB_scientific_cycles",
            "personal_case_ids_or_outcomes",
        } or report["schema"] != "pfl.synthetic_regime_capture_sensitivity.v1"
            or report["evidence_class"] != "SYNTHETIC_LAB_ONLY"):
        raise GateError("ONLY_SYNTHETIC_CAPTURE_REPORTS_COMPARABLE")
    if (type(report["legal_calendar_zone"]) is not str
            or report["legal_calendar_zone"] not in LEGAL_CIVIL_ZONES
            or type(report["reform_on"]) is not str
            or type(report["as_of"]) is not str
            or type(report["hypothetical_trend_sign"]) is not str
            or report["hypothetical_trend_sign"] not in TREND_SIGNS
            or any(report[k] is not False for k in (
                "capture_shares_are_proven_real",
                "real_registration_population_attested",
                "real_negative_pending_or_censored_attested",
                "real_causal_mechanism_identified", "cross_regime_case_links_certified",
                "regime_change_is_causal_exposure",
            )) or report["first_public_at"] is not None
            or report["personal_case_ids_or_outcomes"] is not None
            or type(report["AB_scientific_cycles"]) is not int
            or report["AB_scientific_cycles"] != 0):
        raise GateError("INVALID_SYNTHETIC_REPORT_PROVENANCE")
    day(report["reform_on"])
    utc(report["as_of"])
    periods = report["periods"]
    if type(periods) is not dict or set(periods) != REGIMES:
        raise GateError("INVALID_SYNTHETIC_REPORT_PERIODS")
    for regime in REGIMES:
        p = periods[regime]
        if (type(p) is not dict or set(p) != {
                "visible_source_local_documents", "hypothetical_intake_lower",
                "hypothetical_intake_upper", "missingness_or_right_censoring_attested",
                "all_received_population_certified",
        } or p["missingness_or_right_censoring_attested"] is not False
                or p["all_received_population_certified"] is not False):
            raise GateError("INVALID_SYNTHETIC_REPORT_PERIODS")
        m, lo, hi = (p["visible_source_local_documents"],
                     p["hypothetical_intake_lower"], p["hypothetical_intake_upper"])
        if (type(m) is not int or type(lo) is not int or m < 0
                or m > 2 * MAX_VISIBLE or lo < m
                or (hi is not None and (type(hi) is not int or hi < lo))):
            raise GateError("INCONSISTENT_SYNTHETIC_REPORT_BOUNDS")
    old, new = periods["BEFORE_REFORM"], periods["AFTER_REFORM"]
    derived = _trend_from_bounds(old["hypothetical_intake_lower"],
                                 old["hypothetical_intake_upper"],
                                 new["hypothetical_intake_lower"],
                                 new["hypothetical_intake_upper"])
    if report["hypothetical_trend_sign"] != derived:
        raise GateError("INCONSISTENT_SYNTHETIC_REPORT_TREND")


def compare_capture_hypotheses(*, left: dict, right: dict) -> dict:
    """Same published counts can coexist with different *fictional* trends."""
    _check_synthetic_capture_report(left)
    _check_synthetic_capture_report(right)
    if (left["reform_on"] != right["reform_on"]
            or left["as_of"] != right["as_of"]
            or left["legal_calendar_zone"] != right["legal_calendar_zone"]):
        raise GateError("NONCOMPARABLE_HYPOTHETICAL_PERIODS")
    projection_equal = all(
        left["periods"][r]["visible_source_local_documents"]
        == right["periods"][r]["visible_source_local_documents"]
        for r in REGIMES
    )
    diverge = left["hypothetical_trend_sign"] != right["hypothetical_trend_sign"]
    return {
        "schema": "pfl.synthetic_regime_observational_equivalence.v1",
        "status": ("REGIME_SELECTION_ALTERNATIVES_UNRESOLVED"
                   if projection_equal and diverge
                   else "NO_DIFFERENTIAL_WITNESS_FROM_THESE_FIXTURES"),
        "same_visible_projection": projection_equal,
        "different_hypothetical_trend_sign": diverge,
        "fictional_registration_trend_not_identified_from_publications": projection_equal and diverge,
        "real_reform_effect_identified": False,
        "real_source_coverage_verified": False,
        "AB_scientific_cycles": 0,
    }
