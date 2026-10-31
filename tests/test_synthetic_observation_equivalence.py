"""Purely synthetic constructive proof; no personal, source or outcome data."""
from dataclasses import replace
import pytest

from politics_fantasy.procedural_index_contract import GateError
from politics_fantasy.synthetic_temporal_witness import KnowledgeInterval
from politics_fantasy.synthetic_observation_equivalence import (
    FictionalEpisode, FictionalFullWorld, prove_observational_nonidentification,
)

KNOWN = KnowledgeInterval("2026-10-03T00:00:00Z", "2026-10-04T00:00:00Z")
LATE = KnowledgeInterval("2026-10-31T00:00:00Z", "2026-11-01T00:00:00Z")
UNKNOWN = KnowledgeInterval(None, None)


def episode(name, recurrence=False, observed=KNOWN, capture="2026-10-04T00:00:00Z"):
    return FictionalEpisode("SYNTHETIC:"+name, "2020-04-01",
                            "2020-07-01" if recurrence else None,
                            observed, capture)


def worlds():
    # The only document visible to the analyst is A with nonrecurrence.
    a = episode("A")
    # Both populations contain one unseen registered entry B. In one world it
    # recurs; in the other it does not. Observations are identical.
    b0 = episode("B", False, UNKNOWN, None)
    b1 = episode("B", True, UNKNOWN, None)
    return (FictionalFullWorld("SYNTHETIC:WORLD0", (a,b0)),
            FictionalFullWorld("SYNTHETIC:WORLD1", (a,b1)))


def prove(a,b,**overrides):
    return prove_observational_nonidentification(
        left=a,right=b,cut_on=overrides.get("cut_on","2020-12-31"),
        as_of=overrides.get("as_of","2026-11-01T00:00:00Z"))


def test_identical_published_data_can_hide_different_system_persistence():
    a,b = worlds()
    result = prove(a,b)
    assert result["status"] == "CONSTRUCTIVE_SELECTION_NONIDENTIFICATION"
    assert result["same_locally_observed_projection"]
    assert result["full_world_recurrence_differs"]
    assert result["real_registered_population_denominator"] is None
    assert not result["real_system_feedback_identified"]
    assert result["oracle_rates"] is None
    assert "SYNTHETIC:B" not in str(result)


def test_observed_disagreement_destroys_equivalence():
    a,b=worlds()
    exposed=replace(b.episodes[1],locally_observed=KNOWN,
                    captured_at="2026-10-04T00:00:00Z")
    assert not prove(a,replace(b,episodes=(b.episodes[0],exposed)))[
        "constructive_nonidentification_witness"]


def test_same_oracle_rate_no_differential_witness():
    a,_=worlds()
    renamed=replace(a,world_id="SYNTHETIC:ANOTHER_WORLD")
    assert not prove(a,renamed)["full_world_recurrence_differs"]


def test_future_revisions_not_retroactively_visible_to_observer():
    a,b=worlds()
    hidden_late=episode("C",True,LATE,"2026-10-31T15:00:00Z")
    x=replace(a, episodes=a.episodes+(hidden_late,))
    y=replace(b, episodes=b.episodes+(hidden_late,))
    older=prove(x,y,as_of="2026-10-11T00:00:00Z")
    assert older["same_locally_observed_projection"]
    assert older["constructive_nonidentification_witness"]
    assert "SYNTHETIC:C" not in str(older)


@pytest.mark.parametrize("bad",[
    {"first_public_at":"2020-01-01T00:00:00Z"},
    {"episode_id":"REAL_PERSON"},
    {"oracle_reintroduced_on":"2019-01-01"},
    {"locally_observed":UNKNOWN},
])
def test_oracle_gate_blocks_real_ids_future_publication_or_unpaired_observation(bad):
    with pytest.raises(GateError):
        replace(episode("A"),**bad)


def test_full_day_vs_asof_and_duplicate_ids_are_rejected():
    a,b=worlds()
    with pytest.raises(GateError,match="COMPLETE_EVENT_DAY_REQUIRED"):
        prove(a,b,cut_on="2026-11-01")
    with pytest.raises(GateError,match="INVALID_SYNTHETIC_FULL_WORLD"):
        replace(a,episodes=(a.episodes[0],a.episodes[0]))
    with pytest.raises(GateError,match="TWO_DISTINCT"):
        prove(a,a)


def test_unknown_publication_and_true_hidden_outcomes_never_become_real_evidence():
    a,b=worlds()
    x=prove(a,b)
    assert x["first_public_at"] is None
    assert x["real_negative_or_pending_outcomes"] is None
    assert x["AB_scientific_cycles"]==0
    assert x["real_reintroduction_links_authenticated"] is False


def test_early_and_late_event_cuts_use_dated_oracle_event_not_fixed_boolean():
    a,b=worlds()
    early=prove(a,b,cut_on="2020-06-30")
    late=prove(a,b,cut_on="2020-12-31")
    assert early["same_locally_observed_projection"]
    assert early["full_world_recurrence_differs"] is False
    assert late["constructive_nonidentification_witness"]


def test_public_synthetic_document_cannot_observe_future_recurrence():
    early=KnowledgeInterval("2020-05-01T00:00:00Z","2020-05-01T00:00:00Z")
    with pytest.raises(GateError,match="OBSERVED_SYNTHETIC_RECURRENCE_FROM_FUTURE"):
        episode("FUTURE", True, early,"2020-05-01T00:00:00Z")
