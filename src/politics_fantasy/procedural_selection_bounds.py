"""Synthetic partial identification of event-by-cut rates under selection.

This is a didactic *instrument*, not an estimator over PFL's current sources.
Nothing here can authenticate a real total, certify outcomes, infer a hazard,
or turn the absence of a record into failure. It illustrates the exact
scientific consequence of a missing all-received risk-set denominator.

If N were independently attested and the event-by-cut status of Y cases were
known, with Z known not to have the event by the same cut, then the worst-case
prevalence is [Y/N, (N-Z)/N]; all other statuses are unknown. The interval is
not a confidence interval, causal effect or incidence rate.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from .procedural_index_contract import GateError, utc, day


@dataclass(frozen=True)
class SyntheticEventCut:
    as_of: str
    cut_on: str
    synthetic_frame_id: str
    observed_source_local_cases: int
    attested_event_by_cut: int
    attested_no_event_by_cut: int
    # A test fixture may supply a true external N. No real or editorial
    # denominator is eligible for this module.
    synthetic_independent_register_total: int | None = None
    evidence_class: str = "SYNTHETIC_LAB_ONLY"

    def __post_init__(self) -> None:
        knowledge=utc(self.as_of)
        if day(self.cut_on)>=knowledge.date():
            raise GateError("COMPLETE_SYNTHETIC_EVENT_CUT_REQUIRED")
        if (self.evidence_class != "SYNTHETIC_LAB_ONLY"
                or not isinstance(self.synthetic_frame_id, str)
                or not self.synthetic_frame_id.startswith("SYNTHETIC:")):
            raise GateError("REAL_COUNTS_NOT_ADMITTED_TO_SYNTHETIC_BOUNDS")
        for value in (self.observed_source_local_cases, self.attested_event_by_cut,
                      self.attested_no_event_by_cut):
            if type(value) is not int or not 0 <= value <= 10_000_000:
                raise GateError("INVALID_SYNTHETIC_COUNT")
        n = self.synthetic_independent_register_total
        if n is not None and (type(n) is not int or not 0 < n <= 10_000_000):
            raise GateError("INVALID_SYNTHETIC_DENOMINATOR")
        if (self.attested_event_by_cut + self.attested_no_event_by_cut
                > self.observed_source_local_cases):
            raise GateError("CROSS_CLASSIFIED_EVENTS_OR_EXCESS_OBSERVATIONS")
        if n is not None and self.observed_source_local_cases > n:
            raise GateError("CAPTURE_EXCEEDS_HYPOTHETICAL_RISK_SET")

    def report(self) -> dict:
        n = self.synthetic_independent_register_total
        common = {
            "schema": "pfl.synthetic_procedural_selection_bounds.v1",
            "status": "SYNTHETIC_PARTIAL_IDENTIFICATION" if n is not None
                      else "DENOMINATOR_NOT_IDENTIFIED",
            "evidence_class": self.evidence_class,
            "synthetic_frame_id": self.synthetic_frame_id,
            "as_of": self.as_of,
            "cut_on": self.cut_on,
            "individual_event_time_witnesses_verified": False,
            "event_by_cut_labels_are_synthetic_fixture_assumptions": True,
            "observed_source_local_cases": self.observed_source_local_cases,
            "attested_event_by_cut": self.attested_event_by_cut,
            "attested_no_event_by_cut": self.attested_no_event_by_cut,
            "unresolved_observed": (self.observed_source_local_cases
                                    - self.attested_event_by_cut
                                    - self.attested_no_event_by_cut),
            "unobserved_are_not_non_events": True,
            "pending_is_not_terminal_failure": True,
            "first_public_at": None,
            "incidence_hazard_or_causality_identified": False,
            "real_denominator_attested": False,
            "empirical_political_outcomes_analyzed": False,
            "scientific_cycles": 0,
        }
        if n is None:
            return {**common, "risk_population_total": None,
                    "unobserved_frame_cases": None,
                    "lower_fraction": None, "upper_fraction": None,
                    "lower_rate": None, "upper_rate": None}
        lo = Fraction(self.attested_event_by_cut, n)
        hi = Fraction(n - self.attested_no_event_by_cut, n)
        return {
            **common, "risk_population_total": n,
            "unobserved_frame_cases": n-self.observed_source_local_cases,
            "lower_fraction": f"{lo.numerator}/{lo.denominator}",
            "upper_fraction": f"{hi.numerator}/{hi.denominator}",
            "lower_rate": float(lo), "upper_rate": float(hi),
            "bounds_are_synthetic_worst_case_not_statistical_uncertainty": True,
        }
