"""No real cases or outcomes; all arithmetic witnesses are constructed."""
import pytest

from politics_fantasy.procedural_index_contract import GateError
from politics_fantasy.procedural_selection_bounds import SyntheticEventCut


def scenario(**overrides):
    d=dict(as_of="2024-12-31T23:59:59Z",
           synthetic_frame_id="SYNTHETIC:PARLAMENT",
           observed_source_local_cases=70,attested_event_by_cut=12,
           attested_no_event_by_cut=38,
           synthetic_independent_register_total=100)
    return SyntheticEventCut(**(d|overrides))


def test_exact_worst_case_bounds_with_missing_and_unresolved_cases():
    r=scenario().report()
    assert (r["lower_rate"],r["upper_rate"])==(0.12,0.62)
    assert r["unobserved_frame_cases"]==30
    assert r["unresolved_observed"]==20
    assert not r["real_denominator_attested"]
    assert not r["incidence_hazard_or_causality_identified"]
    assert r["first_public_at"] is None


def test_without_independent_register_no_numerical_bounds_even_with_full_editorial_rows():
    r=scenario(synthetic_independent_register_total=None).report()
    assert r["status"]=="DENOMINATOR_NOT_IDENTIFIED"
    assert r["lower_rate"] is None and r["upper_rate"] is None
    assert r["risk_population_total"] is None


def test_known_no_event_by_cut_distinct_from_unknown_or_pending():
    a=scenario(attested_no_event_by_cut=0).report()
    b=scenario(attested_no_event_by_cut=88,observed_source_local_cases=100).report()
    assert a["upper_rate"]==1.0
    assert b["upper_rate"]==0.12
    assert b["lower_rate"]==0.12
    assert b["pending_is_not_terminal_failure"]


@pytest.mark.parametrize("change,code",[
    ({"observed_source_local_cases":101},"CAPTURE_EXCEEDS_HYPOTHETICAL_RISK_SET"),
    ({"attested_event_by_cut":70},"CROSS_CLASSIFIED_EVENTS_OR_EXCESS_OBSERVATIONS"),
    ({"attested_no_event_by_cut":-1},"INVALID_SYNTHETIC_COUNT"),
    ({"observed_source_local_cases":True},"INVALID_SYNTHETIC_COUNT"),
    ({"synthetic_independent_register_total":0},"INVALID_SYNTHETIC_DENOMINATOR"),
    ({"synthetic_frame_id":"CONGRESO_XV"},"REAL_COUNTS_NOT_ADMITTED_TO_SYNTHETIC_BOUNDS"),
    ({"evidence_class":"REAL_OFFICIAL"},"REAL_COUNTS_NOT_ADMITTED_TO_SYNTHETIC_BOUNDS"),
    ({"as_of":"2024-12-31"},"INVALID_TIMESTAMP"),
])
def test_adversarial_gate(change,code):
    with pytest.raises(GateError,match=code):
        scenario(**change)
