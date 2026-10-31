"""R13 fictitious stock/flow: missing is unknown, not censor or rejection."""
from dataclasses import replace

import pytest

from politics_fantasy.denominator_lineage_contract import PopulationTarget
from politics_fantasy.procedural_index_contract import GateError
from politics_fantasy.procedural_stage_accounting import (
    EntryEpisode,PendingWitness,StageAct,ReintroductionClaim,
)
from politics_fantasy.synthetic_cohort_conservation import CohortCut,audit_cuts

HASH="a"*64
CAP="2026-10-31T08:00:00Z"
CAP_LATE="2026-11-02T09:00:00Z"
KNOW="2026-11-03T00:00:00Z"


def frame(**values):
    d=dict(institution="SYNTHETIC_SENATE",family="PETITIONS",
           legislature_or_regime="X",entry_rule="ALL_RECEIVED_REGISTRATION",
           unit="INDIVIDUAL_COMPLAINT",
           window_first_day="2020-01-01",window_last_day="2020-12-31")
    d.update(values)
    return PopulationTarget(**d)


def case(name="ONE",*,entry="2020-01-01",acts=(),pending=(),captured=CAP,
         form=None,channel="PAPER"):
    return EntryEpisode("SYNTHETIC:"+name,form or frame(),
                        entry,captured,HASH,channel,acts,pending)


def act(state,when,observed=CAP):
    return StageAct(state,when,when,observed,HASH)


def pend(when,observed=CAP):
    return PendingWitness(when,observed,HASH)


def cuts(first="2020-03-01",second="2020-06-01",asof=KNOW):
    return CohortCut(first,asof),CohortCut(second,asof)


def check(cases,*,first="2020-03-01",second="2020-06-01",asof=KNOW,links=()):
    a,b=cuts(first,second,asof)
    return audit_cuts(frame=frame(),episodes=tuple(cases),early=a,late=b,
                      reintroductions=tuple(links))


def test_partition_only_synthetic_visible_episode_not_real_denominator():
    p=case(pending=(pend("2020-03-01"),))
    t=case("T",acts=(act("INADMITTED","2020-02-01"),))
    u=case("U")
    x=check((p,t,u))
    assert x["early"]["registered_episodes_visible"]==3
    assert x["early"]["known_terminal_by_cause"]["INADMITTED"]==1
    assert x["early"]["positive_pending_on_exact_cut"]==1
    assert x["early"]["unknown_followup_or_older_pending"]==1
    assert x["late"]["positive_pending_on_exact_cut"]==0
    assert x["late"]["unknown_followup_or_older_pending"]==2
    assert x["all_received_denominator"] is None
    assert x["right_censored_real_cases"] is None
    assert not x["stock_conservation_certified"]
    assert x["no_missingness_imputation"]


def test_event_time_and_observation_time_separate_at_shared_knowledge_horizon():
    e=case(acts=(act("WITHDRAWN","2020-05-01",observed=CAP_LATE),))
    past=check((e,),asof="2026-11-01T00:00:00Z")
    newer=check((e,),asof=KNOW)
    assert past["late"]["known_terminal_by_cause"]["WITHDRAWN"]==0
    assert past["late"]["unknown_followup_or_older_pending"]==1
    assert newer["late"]["known_terminal_by_cause"]["WITHDRAWN"]==1
    assert newer["early"]["known_terminal_by_cause"]["WITHDRAWN"]==0
    assert newer["documented_terminal_transitions_between_cuts"]["WITHDRAWN"]==1
    assert newer["historical_first_public_at"] is None


def test_positive_pending_at_earlier_date_does_not_forward_fill():
    x=check((case(pending=(pend("2020-03-01"),)),))
    assert x["early"]["positive_pending_on_exact_cut"]==1
    assert x["late"]["positive_pending_on_exact_cut"]==0
    assert x["late"]["unknown_followup_or_older_pending"]==1
    assert x["old_pending_not_carried_forward_to_later_cut"]


def test_same_day_positive_pending_and_terminal_conflict_at_cut_rejected():
    with pytest.raises(GateError,match="PENDING_WITNESS_CONTRADICTS"):
        case(acts=(act("APPROVED","2020-03-01"),),
             pending=(pend("2020-03-01"),))


def test_entry_between_cuts_is_not_earlier_case_or_reopened_old_case():
    old=case("OLD")
    recent=case("NEW",entry="2020-05-01")
    x=check((old,recent))
    assert x["early"]["registered_episodes_visible"]==1
    assert x["late"]["registered_episodes_visible"]==2
    assert x["newly_registered_between_cuts"]==1
    assert x["reintroduction_claims_known_at_later_cut"]==0


def test_newly_registered_and_closed_within_interval_not_mixed_with_old_stock():
    e=case("NEW",entry="2020-05-01",
           acts=(act("LAPSED","2020-05-15"),))
    old=case("OLD")
    x=check((old,e))
    assert x["newly_registered_between_cuts"]==1
    assert x["documented_terminal_transitions_between_cuts"]["LAPSED"]==0
    assert x["terminal_claims_among_newly_registered"]["LAPSED"]==1
    assert x["late"]["known_terminal_by_cause"]["LAPSED"]==1


def test_reintroduction_requires_explicit_distinct_episodes():
    earlier=case("A")
    later=case("B",entry="2020-05-01")
    link=ReintroductionClaim(earlier.episode_id,later.episode_id,HASH)
    x=check((earlier,later),links=(link,))
    assert x["reintroduction_claims_known_at_later_cut"]==1
    assert x["late"]["registered_episodes_visible"]==2
    assert x["right_censored_real_cases"] is None
    with pytest.raises(GateError,match="REINTRODUCTION_REFERENCES"):
        check((earlier,),links=(link,))


def test_wrong_direction_reintroduction_fails():
    earlier=case("A")
    later=case("B",entry="2020-05-01")
    link=ReintroductionClaim(later.episode_id,earlier.episode_id,HASH)
    with pytest.raises(GateError,match="REINTRODUCTION_NOT_FORWARD"):
        check((earlier,later),links=(link,))


def test_future_capture_conceals_even_rows_for_old_dates():
    result=check((case(captured=CAP_LATE),),asof="2026-11-01T00:00:00Z")
    assert result["status"]=="NO_SYNTHETIC_COHORT_SOURCE_KNOWN_AS_OF"
    assert result["early"] is None and result["late"] is None
    assert result["newly_registered_between_cuts"] is None
    assert result["documented_terminal_transitions_between_cuts"] is None


def test_partial_future_capture_is_not_stated_as_all_received():
    first=case("KNOWN")
    hidden=case("HIDDEN",captured=CAP_LATE)
    x=check((first,hidden),asof="2026-11-01T00:00:00Z")
    assert x["early"]["registered_episodes_visible"]==1
    assert x["all_received_denominator"] is None
    assert x["source_original_sha_verified"] is False


def test_two_asof_times_cannot_be_compared_as_same_reporting_panel():
    early=CohortCut("2020-03-01","2026-11-01T00:00:00Z")
    late=CohortCut("2020-06-01",KNOW)
    with pytest.raises(GateError,match="SYNTHETIC_STOCK_FLOW_SCOPE"):
        audit_cuts(frame=frame(),episodes=(case(),),early=early,late=late)


def test_reversed_or_identical_event_cuts_fail():
    for first,second in (("2020-06-01","2020-03-01"),
                         ("2020-03-01","2020-03-01")):
        with pytest.raises(GateError,match="SYNTHETIC_STOCK_FLOW_SCOPE"):
            check((case(),),first=first,second=second)


def test_event_time_after_capture_invalid():
    with pytest.raises(GateError,match="COHORT_CUT_EVENT_TIME_AFTER_CAPTURE"):
        CohortCut("2027-01-01","2026-10-31T00:00:00Z")


def test_mixing_real_scope_or_family_refused():
    real=frame(institution="REAL_SENATE")
    with pytest.raises(GateError,match="SYNTHETIC_STOCK_FLOW_SCOPE"):
        audit_cuts(frame=real,episodes=(),early=cuts()[0],late=cuts()[1])
    with pytest.raises(GateError,match="SYNTHETIC_STOCK_FLOW_SCOPE"):
        check((case(form=frame(family="ILP")),))


def test_duplicate_episodes_for_two_channels_cannot_fake_two_intakes():
    x=case()
    with pytest.raises(GateError,match="DUPLICATE_COHORT_EPISODE_ID"):
        check((x,replace(x,channel="ELECTRONIC")))


def test_multiple_terminal_causes_partition_without_success_collapse():
    a=case("A",acts=(act("APPROVED","2020-04-01"),))
    b=case("B",acts=(act("INADMITTED","2020-05-01"),))
    c=case("C",acts=(act("WITHDRAWN","2020-05-01"),))
    x=check((a,b,c))
    assert x["early"]["unknown_followup_or_older_pending"]==3
    assert x["late"]["known_terminal_by_cause"]["APPROVED"]==1
    assert x["late"]["known_terminal_by_cause"]["INADMITTED"]==1
    assert x["late"]["known_terminal_by_cause"]["WITHDRAWN"]==1
    assert sum(x["documented_terminal_transitions_between_cuts"].values())==3
    assert x["AB_cycles_executed"]==0


def test_illegal_resubmission_after_terminal_not_reactivated_in_same_episode():
    with pytest.raises(GateError,match="POST_TERMINAL_ACT"):
        case(acts=(act("WITHDRAWN","2020-03-01"),
                   act("RESUBMITTED","2020-04-01")))


def test_no_real_data_or_outcomes_promoted_and_empty_is_unknown():
    x=check(())
    assert x["status"]=="NO_SYNTHETIC_COHORT_SOURCE_KNOWN_AS_OF"
    assert x["right_censored_real_cases"] is None
    assert x["independent_auditor_denominator"] is None
    assert not x["R5_empirical_gate_passed"]
