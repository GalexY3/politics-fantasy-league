"""R18 synthetic legal-day regression: UTC instant != Spanish civil date."""
import pytest

from politics_fantasy.denominator_lineage_contract import PopulationTarget
from politics_fantasy.procedural_index_contract import (
    GateError, legal_civil_date, legal_day_completed,
)
from politics_fantasy.procedural_stage_accounting import (
    EntryEpisode, PendingWitness, ReintroductionClaim, StageAct, audit_lab,
)
from politics_fantasy.synthetic_cohort_conservation import CohortCut, audit_cuts


HASH = "c" * 64
EARLY_NOVEMBER = "2026-11-01T00:15:00+01:00"


def frame(zone="Europe/Madrid", **kwargs):
    data = dict(institution="SYNTHETIC_REGISTRY", family="ILP",
                legislature_or_regime="2026",entry_rule="ALL_RECEIVED_REGISTRATION",
                unit="PARLIAMENTARY_INITIATIVE",window_first_day="2026-10-01",
                window_last_day="2026-11-30",legal_calendar_zone=zone)
    data.update(kwargs)
    return PopulationTarget(**data)


def test_same_instant_has_distinct_local_legal_days_in_mainland_and_canaries():
    assert legal_civil_date(EARLY_NOVEMBER,"Europe/Madrid").isoformat()=="2026-11-01"
    assert legal_civil_date(EARLY_NOVEMBER,"Atlantic/Canary").isoformat()=="2026-10-31"
    assert legal_civil_date(EARLY_NOVEMBER,"UTC").isoformat()=="2026-10-31"
    assert legal_civil_date("2026-10-31T23:15:00Z","Europe/Madrid").isoformat()=="2026-11-01"


def test_completed_legal_day_uses_next_midnight_not_utc_date():
    assert legal_day_completed(cut_on="2026-10-31",as_of=EARLY_NOVEMBER,
                               legal_calendar_zone="Europe/Madrid")
    assert not legal_day_completed(cut_on="2026-10-31",as_of=EARLY_NOVEMBER,
                                   legal_calendar_zone="Atlantic/Canary")
    assert CohortCut("2026-10-31",EARLY_NOVEMBER,"Europe/Madrid").cut_on=="2026-10-31"
    with pytest.raises(GateError,match="COHORT_CUT_EVENT_DAY_NOT_COMPLETED"):
        CohortCut("2026-10-31",EARLY_NOVEMBER,"Atlantic/Canary")


def test_dst_boundary_is_determined_by_iana_zone_and_not_fixed_offset():
    clock="2026-03-29T22:00:00Z"
    assert legal_day_completed(cut_on="2026-03-29",as_of=clock,
                               legal_calendar_zone="Europe/Madrid")
    assert not legal_day_completed(cut_on="2026-03-29",as_of=clock,
                                   legal_calendar_zone="Atlantic/Canary")


def test_local_document_pending_and_entry_at_legal_midnight_are_not_false_future():
    stage=StageAct("HEARD","2026-11-01","2026-11-01",EARLY_NOVEMBER,
                   HASH,"Europe/Madrid")
    pending=PendingWitness("2026-11-01",EARLY_NOVEMBER,HASH,"Europe/Madrid")
    case=EntryEpisode("SYNTHETIC:MIDNIGHT",frame(),"2026-11-01",
                      EARLY_NOVEMBER,HASH,"PAPER",(stage,),(pending,))
    assert case.entry_on=="2026-11-01"


def test_canaries_cannot_borrow_mainland_november_civil_day():
    with pytest.raises(GateError,match="STAGE_DATE_AFTER_DOCUMENT_OR_CAPTURE"):
        StageAct("HEARD","2026-11-01","2026-11-01",EARLY_NOVEMBER,
                 HASH,"Atlantic/Canary")
    with pytest.raises(GateError,match="PENDING_DATE_OR_PUBLICATION_INVALID"):
        PendingWitness("2026-11-01",EARLY_NOVEMBER,HASH,"Atlantic/Canary")
    with pytest.raises(GateError,match="ENTRY_NOT_IN_RISK_WINDOW_OR_CAPTURE"):
        EntryEpisode("SYNTHETIC:CANARIAS",frame("Atlantic/Canary"),
                     "2026-11-01",EARLY_NOVEMBER,HASH,"PAPER")


def test_missing_or_unrecognized_legal_calendar_fails_closed():
    with pytest.raises(GateError,match="LEGAL_CALENDAR_ZONE_REQUIRED"):
        legal_civil_date(EARLY_NOVEMBER,"Europe/London")
    with pytest.raises(GateError,match="INVALID_POPULATION_TARGET"):
        frame("Europe/London")
    with pytest.raises(GateError,match="INVALID_POPULATION_TARGET"):
        frame([])
    with pytest.raises(GateError,match="LEGAL_CALENDAR_ZONE_REQUIRED"):
        EntryEpisode("SYNTHETIC:UNKNOWN",frame(None),"2026-11-01",
                     EARLY_NOVEMBER,HASH,"PAPER")


def test_two_clock_fixture_rejects_mixed_legal_jurisdictions():
    episode=EntryEpisode("SYNTHETIC:MID",frame(),"2026-10-30",
                         "2026-10-30T12:00:00Z",HASH,"PAPER")
    early=CohortCut("2026-10-29",EARLY_NOVEMBER,"Europe/Madrid")
    late=CohortCut("2026-10-30",EARLY_NOVEMBER,"Atlantic/Canary")
    with pytest.raises(GateError,match="SYNTHETIC_STOCK_FLOW_SCOPE"):
        audit_cuts(frame=frame(),episodes=(episode,),early=early,late=late)


def test_stage_and_pending_witness_calendar_must_match_episode():
    stage=StageAct("HEARD","2026-10-30","2026-10-30",
                   EARLY_NOVEMBER,HASH,"Atlantic/Canary")
    with pytest.raises(GateError,match="STAGE_LEGAL_CALENDAR_MISMATCH"):
        EntryEpisode("SYNTHETIC:MIXED",frame(),"2026-10-29",
                     EARLY_NOVEMBER,HASH,"PAPER",(stage,))
    pend=PendingWitness("2026-10-30",EARLY_NOVEMBER,HASH,"Atlantic/Canary")
    with pytest.raises(GateError,match="PENDING_LEGAL_CALENDAR_MISMATCH"):
        EntryEpisode("SYNTHETIC:MIXED",frame(),"2026-10-29",
                     EARLY_NOVEMBER,HASH,"PAPER",(),(pend,))


def test_local_pending_at_asof_is_not_lost_when_utc_is_previous_day():
    pend=PendingWitness("2026-11-01",EARLY_NOVEMBER,HASH,"Europe/Madrid")
    episode=EntryEpisode("SYNTHETIC:PEND",frame(),"2026-10-30",
                         "2026-10-30T12:00:00Z",HASH,"PAPER",(),(pend,))
    report=audit_lab(frame=frame(),episodes=(episode,),
                     as_of="2026-11-01T00:16:00+01:00")
    assert report["observed_pending_at_last_witness"]==1
    assert report["unknown_followup"]==0
    assert report["scientific_cycles"]==0


def test_local_reintroduction_witness_is_not_rejected_by_utc_date():
    first=EntryEpisode("SYNTHETIC:OLD",frame(),"2026-10-05",
                       "2026-10-05T12:00:00Z",HASH,"PAPER")
    later=EntryEpisode("SYNTHETIC:NEW",frame(),"2026-11-01",
                       EARLY_NOVEMBER,HASH,"PAPER")
    cross=ReintroductionClaim(first.episode_id,later.episode_id,HASH,
                               locally_observed_at=EARLY_NOVEMBER)
    result=audit_lab(frame=frame(),episodes=(first,later,),claims=(cross,),
                     as_of="2026-11-01T00:17:00+01:00")
    assert result["reintroduction_claims_visible"]==1
