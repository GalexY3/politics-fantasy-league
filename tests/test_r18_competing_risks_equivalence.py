"""Entirely fictitious counterexample; all secret/oracle rates remain redacted."""
from dataclasses import replace

import pytest

from politics_fantasy.procedural_index_contract import GateError
from politics_fantasy.synthetic_competing_risks_equivalence import (
    FictionalRiskEpisode, FictionalRiskWorld, compare_competing_risk_worlds,
)

CAP="2026-11-01T01:15:00+01:00"
ASOF="2026-11-01T01:20:00+01:00"


def episode(name,terminal=None,cause=None,captured=None):
    return FictionalRiskEpisode("SYNTHETIC:"+name,"2026-10-01",terminal,cause,
                                captured,"Europe/Madrid")


def pair():
    common=episode("PUBLISHED","2026-10-20","APPROVED",CAP)
    hidden1=episode("NOT_PUBLISHED","2026-10-21","APPROVED")
    hidden2=episode("NOT_PUBLISHED","2026-10-22","REJECTED")
    return (FictionalRiskWorld("SYNTHETIC:A",(common,hidden1)),
            FictionalRiskWorld("SYNTHETIC:B",(common,hidden2)))


def proof(left=None,right=None,**kwargs):
    a,b=pair()
    return compare_competing_risk_worlds(
        left=left or a,right=right or b,cut_on="2026-10-31",as_of=ASOF,
        legal_calendar_zone="Europe/Madrid",**kwargs)


def test_identical_full_registration_frame_and_observations_hide_rival_cause():
    result=proof()
    assert result["constructive_nonidentification_witness"]
    assert result["complete_synthetic_registration_frame_identical"]
    assert result["selected_outcome_projection_identical"]
    assert result["oracle_cause_specific_incidence_differs"]
    assert result["an_independent_N_alone_would_not_resolve_outcome_selection"]
    assert result["AB_scientific_cycles"]==0


def test_hidden_oracle_values_and_person_identifiers_never_appear_in_report():
    result=proof()
    assert result["hidden_case_ids"] is None
    assert result["oracle_case_counts"] is None
    assert result["oracle_cause_rates"] is None
    assert result["first_public_at"] is None
    assert not result["real_terminal_decisions_read"]
    assert not result["causal_effect_or_real_hazard_identified"]
    assert "SYNTHETIC:PUBLISHED" not in str(result)
    assert "SYNTHETIC:NOT_PUBLISHED" not in str(result)


def test_distinct_visible_endings_destroy_observational_equivalence():
    left,right=pair()
    new=replace(right.episodes[1],locally_captured_at=CAP)
    altered=replace(right,episodes=(right.episodes[0],new))
    result=proof(left=left,right=altered)
    assert not result["selected_outcome_projection_identical"]
    assert not result["constructive_nonidentification_witness"]


def test_different_registered_frame_not_a_witness_under_complete_same_N():
    left,right=pair()
    renamed=replace(right.episodes[1],episode_id="SYNTHETIC:OTHER")
    result=proof(left=left,right=replace(right,episodes=(right.episodes[0],renamed)))
    assert not result["complete_synthetic_registration_frame_identical"]
    assert not result["constructive_nonidentification_witness"]


def test_hidden_terminal_after_event_cut_does_not_change_risk_at_cut():
    left,right=pair()
    later=replace(right.episodes[1],terminal_on="2026-11-02",terminal_cause="REJECTED")
    noevent=replace(left.episodes[1],terminal_on=None,terminal_cause=None)
    result=proof(left=replace(left,episodes=(left.episodes[0],noevent)),
                 right=replace(right,episodes=(right.episodes[0],later)))
    assert not result["oracle_cause_specific_incidence_differs"]
    assert not result["constructive_nonidentification_witness"]


def test_missing_terminal_cause_is_not_implicitly_rejected():
    with pytest.raises(GateError,match="TERMINAL_DAY_AND_CAUSE_MUST_AGREE"):
        episode("MISSING","2026-10-31",None)
    with pytest.raises(GateError,match="TERMINAL_DAY_AND_CAUSE_MUST_AGREE"):
        episode("MISSING",None,"APPROVED")


def test_capture_precedes_outcome_is_invalid_even_for_fictional_docs():
    with pytest.raises(GateError,match="CAPTURE_CANNOT_PRECEDE_DOCUMENTED_TERMINAL"):
        episode("FUTURE","2026-11-02","APPROVED",CAP)


def test_incomplete_local_cut_is_not_replayed_as_known():
    a,b=pair()
    with pytest.raises(GateError,match="LEGAL_EVENT_CUT_NOT_YET_COMPLETE"):
        compare_competing_risk_worlds(
            left=a,right=b,cut_on="2026-10-31",as_of="2026-10-31T23:30:00+01:00",
            legal_calendar_zone="Europe/Madrid")


def test_no_real_case_ids_or_forged_first_public_allowed():
    with pytest.raises(GateError,match="ONLY_SYNTHETIC_RISK_EPISODES"):
        FictionalRiskEpisode("REAL_123","2026-10-01",None,None,None,"Europe/Madrid")
    with pytest.raises(GateError,match="ONLY_SYNTHETIC_RISK_EPISODES"):
        replace(episode("X"),first_public_at="2026-10-01T00:00:00Z")


def test_same_world_is_not_independent_counterexample():
    a,_=pair()
    with pytest.raises(GateError,match="DISTINCT_FICTIONAL_WORLDS_REQUIRED"):
        proof(left=a,right=a)


def test_mixed_juridical_calendars_rejected_with_identical_source_ids():
    a,b=pair()
    changed=replace(b.episodes[1],legal_calendar_zone="Atlantic/Canary")
    with pytest.raises(GateError,match="MIXED_RISK_FRAME_LEGAL_CALENDARS"):
        proof(left=a,right=replace(b,episodes=(b.episodes[0],changed)))


def test_local_midnight_capture_not_rejected_by_utc_day():
    observed="2026-11-01T00:15:00+01:00"
    doc=episode("MIDNIGHT","2026-11-01","APPROVED",observed)
    assert doc.visible_at("2026-11-01T00:16:00+01:00")
