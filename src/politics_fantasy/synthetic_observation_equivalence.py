"""R17 constructive counterexample: publication selection cannot identify persistence.

This deliberately compares TWO complete, fictional worlds that a local observer
cannot distinguish from their selected documents. It is not a real-data parser,
an empirical estimand, an official link, or a public first-publication witness.
Only synthetic identifiers and simulated binary recurrence states are allowed.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from .procedural_index_contract import GateError, day, utc
from .synthetic_registration_graph import SYNTHETIC_ID
from .synthetic_temporal_witness import KnowledgeInterval


MAX_EPISODES = 200


@dataclass(frozen=True)
class FictionalEpisode:
    episode_id: str
    registered_on: str
    oracle_reintroduced_on: str | None
    locally_observed: KnowledgeInterval
    captured_at: str | None
    # Historical public-first is unknown even for a locally visible item.
    first_public_at: None = None

    def __post_init__(self) -> None:
        if (not isinstance(self.episode_id, str)
                or not SYNTHETIC_ID.fullmatch(self.episode_id)
                or self.first_public_at is not None
                or not isinstance(self.locally_observed, KnowledgeInterval)):
            raise GateError("FICTIONAL_ORACLE_EPISODES_ONLY")
        day(self.registered_on)
        if self.oracle_reintroduced_on is not None:
            if (type(self.oracle_reintroduced_on) is not str
                    or day(self.oracle_reintroduced_on) < day(self.registered_on)):
                raise GateError("FICTIONAL_REINTRODUCTION_BEFORE_REGISTERED_ENTRY")
        bound = self.locally_observed.upper()
        if (self.captured_at is None) != (bound is None):
            raise GateError("MISSING_LOCAL_OBSERVATION_OR_CAPTURE")
        if self.captured_at is not None:
            stamp = utc(self.captured_at)
            if (stamp.date() < day(self.registered_on)
                    or (self.locally_observed.observed_not_before is not None
                        and stamp < utc(self.locally_observed.observed_not_before))):
                raise GateError("OBSERVATION_BEFORE_SYNTHETIC_REGISTRATION")
            if (self.oracle_reintroduced_on is not None
                    and day(self.oracle_reintroduced_on) > stamp.date()):
                raise GateError("OBSERVED_SYNTHETIC_RECURRENCE_FROM_FUTURE")

    def visible_at(self, as_of: str) -> bool:
        bound = self.locally_observed.upper()
        return (bound is not None and self.captured_at is not None
                and max(bound, utc(self.captured_at)) <= utc(as_of))


@dataclass(frozen=True)
class FictionalFullWorld:
    world_id: str
    episodes: tuple[FictionalEpisode, ...]

    def __post_init__(self) -> None:
        if (not isinstance(self.world_id, str)
                or not SYNTHETIC_ID.fullmatch(self.world_id)
                or type(self.episodes) is not tuple
                or not 1 <= len(self.episodes) <= MAX_EPISODES
                or any(not isinstance(x, FictionalEpisode) for x in self.episodes)
                or len({x.episode_id for x in self.episodes}) != len(self.episodes)):
            raise GateError("INVALID_SYNTHETIC_FULL_WORLD")


def prove_observational_nonidentification(
    *, left: FictionalFullWorld, right: FictionalFullWorld,
    cut_on: str, as_of: str,
) -> dict:
    """A constructive witness, not a numerical inference on political data.

    Compare the *same observed projection* while varying the synthetic hidden
    full population. If rates differ, no estimator using that projection alone
    can uniquely recover the full-population recurrence fraction.
    """
    cut = day(cut_on)
    observed_at = utc(as_of)
    if cut >= observed_at.date():
        raise GateError("COMPLETE_EVENT_DAY_REQUIRED_FOR_OBSERVATION_PROOF")
    if (not isinstance(left, FictionalFullWorld)
            or not isinstance(right, FictionalFullWorld)
            or left.world_id == right.world_id):
        raise GateError("TWO_DISTINCT_SYNTHETIC_WORLDS_REQUIRED")

    def project(world: FictionalFullWorld):
        relevant = [x for x in world.episodes if day(x.registered_on) <= cut]
        def recurs_by_cut(x: FictionalEpisode) -> bool:
            return (x.oracle_reintroduced_on is not None
                    and day(x.oracle_reintroduced_on) <= cut)
        exposed = sorted(
            (x.episode_id, x.registered_on, recurs_by_cut(x))
            for x in relevant if x.visible_at(as_of))
        oracle_rate = Fraction(sum(recurs_by_cut(x) for x in relevant),
                               len(relevant)) if relevant else None
        return exposed, oracle_rate

    visible_l, oracle_l = project(left)
    visible_r, oracle_r = project(right)
    same_projection = visible_l == visible_r
    distinct_oracle = oracle_l is not None and oracle_r is not None and oracle_l != oracle_r
    counterexample = same_projection and distinct_oracle
    return {
        "schema": "pfl.synthetic_observation_equivalence.v1",
        "status": ("CONSTRUCTIVE_SELECTION_NONIDENTIFICATION" if counterexample
                   else "NO_DIFFERENTIAL_COUNTEREXAMPLE_IN_SUPPLIED_FIXTURES"),
        "synthetic_only": True,
        "same_locally_observed_projection": same_projection,
        "full_world_recurrence_differs": distinct_oracle,
        "constructive_nonidentification_witness": counterexample,
        "published_selection_is_not_registration_frame": True,
        "historical_public_first_availability_authenticated": False,
        "real_registered_population_denominator": None,
        "real_negative_or_pending_outcomes": None,
        "real_reintroduction_links_authenticated": False,
        "real_system_feedback_identified": False,
        "AB_scientific_cycles": 0,
        # Suppress both real and fictional raw identifiers and oracle counts.
        "observed_episode_ids": None,
        "unobserved_episode_ids": None,
        "oracle_population_sizes": None,
        "oracle_rates": None,
        "first_public_at": None,
    }
