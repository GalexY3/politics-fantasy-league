"""R11: synthetic-only competing transitions and explicit pending witnesses."""
from dataclasses import replace
import pytest
from politics_fantasy.procedural_stage_accounting import (
    EntryEpisode,StageAct,PendingWitness,ReintroductionClaim,audit_lab,
)
from politics_fantasy.denominator_lineage_contract import PopulationTarget
from politics_fantasy.procedural_index_contract import GateError

SHA="a"*64
LATE="2026-11-02T08:01:00Z"
EARLY="2026-10-31T08:00:00Z"


def scope(**kw):
    s={"institution":"SYNTHETIC_CHAMBER","family":"ILP",
       "legislature_or_regime":"XI","entry_rule":"ALL_RECEIVED_REGISTRATION",
       "unit":"PARLIAMENTARY_INITIATIVE",
       "window_first_day":"2020-01-01","window_last_day":"2020-12-31",
       "legal_calendar_zone":"UTC"}
    s.update(kw)
    return PopulationTarget(**s)


def episode(name="SYNTHETIC:ONE",*,frame=None,acts=(),pending=(),channel="PAPER",
            date="2020-01-01",capture=EARLY):
    return EntryEpisode(name,frame or scope(),date,capture,SHA,channel,acts,pending)


def stage(kind,*,date="2020-02-01",document="2020-02-02",capture=EARLY):
    return StageAct(kind,date,document,capture,SHA,"UTC")


def pending(*,date="2020-03-01",capture=EARLY):
    return PendingWitness(date,capture,SHA,"UTC")


def test_unknown_without_pending_witness_is_not_right_censored():
    r=audit_lab(frame=scope(),episodes=(episode(),),as_of="2026-11-01T00:00:00Z")
    assert r["status"]=="LAB_ONLY_NOT_EMPIRICAL"
    assert r["unknown_followup"]==1 and r["observed_pending_at_last_witness"]==0
    assert r["pending_absence_is_not_right_censoring"]
    assert r["all_received_denominator"] is None


def test_explicit_pending_witness_needed_and_not_a_current_status_forecast():
    e=episode(pending=(pending(),))
    r=audit_lab(frame=scope(),episodes=(e,),as_of="2026-11-01T00:00:00Z")
    assert r["observed_pending_at_last_witness"]==1
    assert r["unknown_followup"]==0
    assert r["later_pending_status_not_inferred"]


def test_competing_terminal_causes_not_collapsed_to_success_failure():
    cases=(episode("SYNTHETIC:A",acts=(stage("INADMITTED"),)),
           episode("SYNTHETIC:B",acts=(stage("WITHDRAWN"),)),
           episode("SYNTHETIC:C",acts=(stage("TRANSFERRED_OUT"),)),
           episode("SYNTHETIC:D",acts=(stage("APPROVED"),)))
    r=audit_lab(frame=scope(),episodes=cases,as_of="2026-11-01T00:00:00Z")
    assert r["visible_episode_count"]==4
    assert {k:v for k,v in r["terminal_by_cause"].items() if v}=={
        "INADMITTED":1,"WITHDRAWN":1,"TRANSFERRED_OUT":1,"APPROVED":1}
    assert r["all_received_denominator"] is None


def test_future_local_capture_hides_even_event_that_already_occurred():
    e=episode(acts=(stage("REJECTED",capture=LATE),))
    past=audit_lab(frame=scope(),episodes=(e,),as_of="2026-11-01T00:00:00Z")
    assert past["unknown_followup"]==1
    assert past["terminal_by_cause"]["REJECTED"]==0
    later=audit_lab(frame=scope(),episodes=(e,),as_of="2026-11-02T08:01:01Z")
    assert later["terminal_by_cause"]["REJECTED"]==1
    assert later["unknown_followup"]==0


def test_episode_source_not_known_at_cut_suppresses_all_counts():
    e=episode(capture="2026-11-02T08:00:00Z")
    r=audit_lab(frame=scope(),episodes=(e,),as_of="2026-11-01T00:00:00Z")
    assert r["status"]=="NO_LAB_INPUT_KNOWN_AT_CUT"
    assert r["visible_episode_count"] is None
    assert r["terminal_by_cause"] is None
    assert r["unknown_followup"] is None
    assert r["first_public_at"] is None


@pytest.mark.parametrize("name",["PERSON_ID:123","REAL_0001","", "SYNTHETIC:hello world"])
def test_real_or_malformed_episode_id_not_ingested(name):
    with pytest.raises(GateError):
        episode(name)


def test_two_terminal_events_and_terminal_followed_by_hearing_rejected():
    for steps in ((stage("APPROVED"),stage("REJECTED",date="2020-03-01",document="2020-03-02")),
                  (stage("APPROVED"),stage("HEARD",date="2020-03-01",document="2020-03-02"))):
        with pytest.raises(GateError,match="POST_TERMINAL"):
            episode(acts=steps)


def test_pending_witness_after_terminal_is_inconsistent():
    with pytest.raises(GateError,match="PENDING_WITNESS_CONTRADICTS"):
        episode(acts=(stage("WITHDRAWN"),),pending=(pending(),))


def test_admitted_first_must_not_include_pre_admission_rejection():
    f=scope(entry_rule="ADMISSION_FIRST")
    with pytest.raises(GateError,match="ADMITTED_FIRST"):
        episode(frame=f,acts=(stage("INADMITTED"),))


def test_backdated_events_and_off_frame_entries_rejected():
    with pytest.raises(GateError,match="BACKDATED"):
        episode(acts=(stage("HEARD",date="2020-03-01",document="2020-03-02"),
                      stage("REJECTED",date="2020-02-01")))
    with pytest.raises(GateError,match="RISK_WINDOW"):
        episode(date="2019-12-31")


def test_entry_channels_different_but_not_inferred_new_intake():
    e=episode(channel="PAPER_ELECTRONIC_UNRECONCILED")
    r=audit_lab(frame=scope(),episodes=(e,),as_of="2026-11-01T00:00:00Z")
    assert r["all_received_denominator"] is None


def test_reintroduction_must_refer_to_two_explicit_distinct_episodes():
    a=episode("SYNTHETIC:A")
    b=episode("SYNTHETIC:B",date="2020-02-01")
    link=ReintroductionClaim(a.episode_id,b.episode_id,SHA,
                             locally_observed_at="2026-10-30T09:00:00Z")
    r=audit_lab(frame=scope(),episodes=(a,b),claims=(link,),
                as_of="2026-11-01T00:00:00Z")
    assert r["reintroduction_claims_visible"]==1
    assert r["reintroduction_claim_is_not_verified_identity"]
    duplicated=audit_lab(frame=scope(),episodes=(a,b),claims=(link,link),
                         as_of="2026-11-01T00:00:00Z")
    assert duplicated["reintroduction_claims_visible"]==1
    unobserved=ReintroductionClaim(a.episode_id,b.episode_id,SHA)
    r_unknown=audit_lab(frame=scope(),episodes=(a,b),claims=(unobserved,),
                        as_of="2026-11-01T00:00:00Z")
    assert r_unknown["reintroduction_claims_visible"]==0
    r_future=audit_lab(frame=scope(),episodes=(a,b),claims=(
        ReintroductionClaim(a.episode_id,b.episode_id,SHA,
                            locally_observed_at="2026-11-04T00:00:00Z"),),
        as_of="2026-11-01T00:00:00Z")
    assert r_future["reintroduction_claims_visible"]==0
    with pytest.raises(GateError):
        ReintroductionClaim(a.episode_id,a.episode_id,SHA)
    with pytest.raises(GateError):
        ReintroductionClaim(a.episode_id,b.episode_id,SHA,
                            independent_authority_verified=True)
    with pytest.raises(GateError,match="UNTRUSTED_REINTRODUCTION_LINK"):
        audit_lab(frame=scope(),episodes=(b,a),claims=(
            ReintroductionClaim(b.episode_id,a.episode_id,SHA),),
            as_of="2026-11-01T00:00:00Z")


def test_duplicate_episodes_and_mismatched_risk_sets_rejected():
    a=episode()
    with pytest.raises(GateError,match="DUPLICATE_EPISODES"):
        audit_lab(frame=scope(),episodes=(a,a),as_of="2026-11-01T00:00:00Z")
    with pytest.raises(GateError,match="SYNTHETIC_ONLY"):
        audit_lab(frame=scope(family="PETITIONS"),episodes=(a,),
                  as_of="2026-11-01T00:00:00Z")


def test_source_sha_is_only_a_claim_and_publication_not_invented():
    with pytest.raises(GateError,match="SHA"):
        replace(stage("HEARD"),document_sha_claim="badhash")
    with pytest.raises(GateError,match="PUBLICATION"):
        replace(stage("HEARD"),first_public_at="2020-02-02T00:00:00Z")
    with pytest.raises(GateError,match="DATE"):
        stage("APPROVED",date="2020-03-01",document="2020-02-01")
