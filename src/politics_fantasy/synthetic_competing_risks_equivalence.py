"""R18 constructive partial-identification limit under selected documentation.

Two entirely fictional worlds can share the *same complete registration frame*
and exactly the same captured, published outcome projection, yet have different
cause-specific event counts at a legally completed cutoff. In particular, an
independent N alone would not identify competing risks with selective outcomes.

This is a mathematical counterexample. It is neither an estimator, an empirical
Spanish source, a causal discovery, nor a public historical availability claim.
"""
from __future__ import annotations

from dataclasses import dataclass

from .procedural_index_contract import (
    GateError, day, utc, legal_day_completed, legal_civil_date,
)
from .synthetic_registration_graph import SYNTHETIC_ID

CAUSES = frozenset({"APPROVED", "REJECTED", "WITHDRAWN", "LAPSED"})
MAX_CASES = 200


@dataclass(frozen=True)
class FictionalRiskEpisode:
    episode_id: str
    registered_on: str
    terminal_on: str | None
    terminal_cause: str | None
    locally_captured_at: str | None
    legal_calendar_zone: str
    first_public_at: None = None

    def __post_init__(self) -> None:
        if (type(self.episode_id) is not str
                or SYNTHETIC_ID.fullmatch(self.episode_id) is None
                or self.first_public_at is not None):
            raise GateError("ONLY_SYNTHETIC_RISK_EPISODES")
        start = day(self.registered_on)
        if (self.terminal_on is None) != (self.terminal_cause is None):
            raise GateError("TERMINAL_DAY_AND_CAUSE_MUST_AGREE")
        if self.terminal_on is not None:
            if self.terminal_cause not in CAUSES or day(self.terminal_on) < start:
                raise GateError("INVALID_SYNTHETIC_TERMINAL")
        # Require an explicit jurisdiction even for hidden episodes; there is
        # no implicit conversion from UTC-day to the institution's civil day.
        legal_civil_date("2026-01-01T00:00:00Z",self.legal_calendar_zone)
        if self.locally_captured_at is not None:
            captured = utc(self.locally_captured_at)
            if (self.terminal_on is None
                    or legal_civil_date(self.locally_captured_at,self.legal_calendar_zone)
                       < day(self.terminal_on)):
                raise GateError("CAPTURE_CANNOT_PRECEDE_DOCUMENTED_TERMINAL")

    def visible_at(self, as_of: str) -> bool:
        return self.locally_captured_at is not None and utc(self.locally_captured_at) <= utc(as_of)


@dataclass(frozen=True)
class FictionalRiskWorld:
    world_id: str
    episodes: tuple[FictionalRiskEpisode, ...]

    def __post_init__(self) -> None:
        if (type(self.world_id) is not str
                or SYNTHETIC_ID.fullmatch(self.world_id) is None
                or type(self.episodes) is not tuple
                or not 1 <= len(self.episodes) <= MAX_CASES
                or any(type(e) is not FictionalRiskEpisode for e in self.episodes)
                or len({e.episode_id for e in self.episodes}) != len(self.episodes)):
            raise GateError("INVALID_SYNTHETIC_RISK_WORLD")


def compare_competing_risk_worlds(*, left: FictionalRiskWorld,
                                  right: FictionalRiskWorld, cut_on: str,
                                  as_of: str, legal_calendar_zone: str) -> dict:
    """Compute a redacted constructive proof, never release hidden oracle counts."""
    if (not isinstance(left, FictionalRiskWorld)
            or not isinstance(right, FictionalRiskWorld)
            or left.world_id == right.world_id):
        raise GateError("DISTINCT_FICTIONAL_WORLDS_REQUIRED")
    if any(ep.legal_calendar_zone != legal_calendar_zone
           for w in (left,right) for ep in w.episodes):
        raise GateError("MIXED_RISK_FRAME_LEGAL_CALENDARS")
    if not legal_day_completed(cut_on=cut_on, as_of=as_of,
                               legal_calendar_zone=legal_calendar_zone):
        raise GateError("LEGAL_EVENT_CUT_NOT_YET_COMPLETE")
    cut = day(cut_on)

    def project(world):
        frame = sorted((e.episode_id, e.registered_on)
                       for e in world.episodes if day(e.registered_on) <= cut)
        observed = sorted((e.episode_id, e.registered_on,
                           e.terminal_on, e.terminal_cause)
                          for e in world.episodes if day(e.registered_on) <= cut
                          and e.visible_at(as_of) and e.terminal_on is not None
                          and day(e.terminal_on) <= cut)
        # Each registered case contributes to exactly one terminal cause at
        # this event cut, or to the still-unresolved oracle class.
        terminal = tuple(sum(e.terminal_cause == cause
                             and e.terminal_on is not None
                             and day(e.terminal_on) <= cut
                             and day(e.registered_on) <= cut
                             for e in world.episodes) for cause in sorted(CAUSES))
        return frame, observed, terminal

    frame_l, observed_l, oracle_l = project(left)
    frame_r, observed_r, oracle_r = project(right)
    same_frame = frame_l == frame_r
    same_observed = observed_l == observed_r
    different_causes = oracle_l != oracle_r
    witness = same_frame and same_observed and different_causes
    return {
        "schema": "pfl.synthetic_competing_risks_equivalence.v1",
        "synthetic_only": True,
        "status": ("CONSTRUCTIVE_COMPETING_RISK_NONIDENTIFICATION" if witness
                   else "NO_COUNTEREXAMPLE_IN_SUPPLIED_FIXTURES"),
        "legal_calendar_zone": legal_calendar_zone,
        "complete_synthetic_registration_frame_identical": same_frame,
        "selected_outcome_projection_identical": same_observed,
        "oracle_cause_specific_incidence_differs": different_causes,
        "constructive_nonidentification_witness": witness,
        "an_independent_N_alone_would_not_resolve_outcome_selection": witness,
        "first_public_at": None,
        "real_independent_denominator_verified": False,
        "real_terminal_decisions_read": False,
        "real_pending_or_censoring_count": None,
        "causal_effect_or_real_hazard_identified": False,
        "hidden_case_ids": None,
        "oracle_case_counts": None,
        "oracle_cause_rates": None,
        "AB_scientific_cycles": 0,
    }
