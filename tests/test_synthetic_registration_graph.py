"""Registration-first N:M temporal graph — adversarial and wholly fictional."""
from dataclasses import replace

import pytest

from politics_fantasy.procedural_index_contract import GateError
from politics_fantasy.synthetic_temporal_witness import KnowledgeInterval
from politics_fantasy.synthetic_registration_graph import (
    OfficialStageKey, StageVersion, TypedStageEdge, audit_graph,
)

OLD="2026-10-11T00:00:00Z"
NEW="2026-11-01T00:00:00Z"
KNOWN_OLD=KnowledgeInterval("2026-10-02T00:00:00Z","2026-10-03T00:00:00Z")
KNOWN_LATE=KnowledgeInterval("2026-10-31T00:00:00Z","2026-11-01T00:00:00Z")


def key(stage,name,inst="SYNTHETIC:ASSEMBLY",regime="SYNTHETIC:XI",
        fam="SYNTHETIC:ILP"):
    return OfficialStageKey(inst,regime,fam,stage,"SYNTHETIC:"+name)


def record(k,*,revision="SYNTHETIC:V1",event="2020-01-01",doc="2020-01-02",
           known=KNOWN_OLD,captured="2026-10-03T12:00:00Z",editor=None):
    return StageVersion(k,revision,event,doc,editor,known,captured,"a"*64)


def edge(origin,dest,*,role="REGISTER_TO_FILE",name="E1",
         known=KNOWN_OLD,captured="2026-10-03T12:00:00Z",
         doc="2020-01-03",editor=None):
    return TypedStageEdge("SYNTHETIC:"+name,origin,dest,role,doc,editor,
                          known,captured,"b"*64)


def audit(records,edges=(),*,asof=NEW,cut="2020-12-31"):
    return audit_graph(records=tuple(records),edges=tuple(edges),
                       cut_on=cut,as_of=asof)


def test_two_distinct_registered_intakes_one_file_not_additive_population():
    a,b=key("REGISTRATION","A"),key("REGISTRATION","B")
    c=key("FILE","C")
    x=audit([record(a),record(b),record(c)],
            [edge(a,c),edge(b,c,name="E2")])
    assert x["visible_stages"]["REGISTRATION"]==2
    assert x["visible_stages"]["FILE"]==1
    assert x["multi_entry_files"]==1
    assert x["multifile_registrations"]==0
    assert x["visible_claimed_edges"]==2
    assert x["independent_all_received_denominator"] is None
    assert x["registered_at_risk_population_certified"] is False
    assert x["actual_pending_at_cut"] is None
    assert x["historical_first_public_at"] is None
    assert "SYNTHETIC:A" not in str(x)


def test_one_register_to_two_files_not_two_new_registrations():
    a=key("REGISTRATION","A")
    b,c=key("FILE","B"),key("FILE","C")
    x=audit([record(a),record(b),record(c)],
            [edge(a,b),edge(a,c,name="E2")])
    assert x["visible_stages"]["REGISTRATION"]==1
    assert x["multifile_registrations"]==1
    assert x["visible_stages"]["FILE"]==2
    assert x["independent_all_received_denominator"] is None


def test_cross_institutional_transfer_requires_explicit_typed_file_edge():
    a=key("FILE","A",inst="SYNTHETIC:CHAMBER_A")
    b=key("FILE","B",inst="SYNTHETIC:CHAMBER_B")
    with pytest.raises(GateError,match="SPURIOUS_CROSS_FRAME_JOIN"):
        edge(key("REGISTRATION","X",inst="SYNTHETIC:CHAMBER_A"),
             b,role="REGISTER_TO_FILE")
    t=edge(a,b,role="EXPLICIT_TRANSFER_WITH_DUAL_OFFICIAL_IDS")
    x=audit([record(a),record(b)],[t])
    assert x["claimed_transfer_edges"]==1
    assert x["official_cross_institution_links_authenticated"] is False
    assert x["source_counts_additive"] is False


def test_same_textual_id_across_stages_is_not_link():
    a,b=key("REGISTRATION","SAME"),key("FILE","SAME")
    x=audit([record(a),record(b)])
    assert x["visible_claimed_edges"]==0
    assert x["unlinked_visible_registrations"]==1
    assert x["missing_link_is_not_rejection"]


def test_future_link_does_not_retroactively_rewrite_registration_graph():
    a,b=key("REGISTRATION","A"),key("FILE","B")
    late=edge(a,b,known=KNOWN_LATE,captured="2026-10-31T16:00:00Z",
              editor="2026-10-10T13:00:00Z")
    before=audit([record(a),record(b)],[late],asof=OLD)
    after=audit([record(a),record(b)],[late],asof=NEW)
    assert before["visible_stages"]["REGISTRATION"]==1
    assert before["visible_claimed_edges"]==0
    assert before["unlinked_visible_registrations"]==1
    assert after["visible_claimed_edges"]==1
    assert after["unlinked_visible_registrations"]==0
    assert after["historical_first_public_at"] is None


def test_late_source_revisions_do_not_retroactively_erase_early_source():
    a=key("FILE","X")
    old=record(a)
    retro=record(a,revision="SYNTHETIC:V2",event="2020-02-01",
                 doc="2020-02-02",known=KNOWN_LATE,
                 captured="2026-10-31T18:00:00Z",
                 editor="2026-10-10T00:00:00Z")
    before=audit([old,retro],asof=OLD)
    after=audit([old,retro],asof=NEW)
    assert before["visible_stage_total"]==1
    assert before["revision_keys"]==1
    assert after["visible_stage_total"]==1
    assert after["revision_keys"]==2
    assert after["originals_authenticated"] is False


def test_future_conflicting_revision_does_not_taint_old_cut():
    a=key("ACTION","X")
    old=record(a)
    later=record(a,known=KNOWN_LATE,captured="2026-10-31T18:00:00Z",
                 event="2020-05-01",doc="2020-05-02")
    assert audit([old,later],asof=OLD)["status"]=="SYNTHETIC_DOCUMENTARY_GRAPH_ONLY"
    newer=audit([old,later],asof=NEW)
    assert newer["status"]=="VISIBLE_CONFLICTING_STAGE_REVISION_QUARANTINED"
    assert newer["visible_stage_total"] is None
    assert newer["visible_claimed_edges"] is None


def test_future_conflicting_edge_only_quarantines_new_cut():
    a,b=key("REGISTRATION","A"),key("FILE","B")
    early=edge(a,b)
    later=edge(a,b,known=KNOWN_LATE,captured="2026-10-31T15:00:00Z",
               doc="2020-02-01")
    assert audit([record(a),record(b)],[early,later],asof=OLD)[
        "visible_claimed_edges"]==1
    x=audit([record(a),record(b)],[early,later],asof=NEW)
    assert x["status"]=="VISIBLE_CONFLICTING_EDGE_CLAIM_QUARANTINED"
    assert x["orphan_claims_at_cut"] is None


def test_future_source_name_and_hash_never_propagate_into_old_metadata():
    future=record(key("FILE","SECRET_FUTURE",inst="SYNTHETIC:FUTURE_INSTITUTION"),
        known=KNOWN_LATE,captured="2026-10-31T14:00:00Z")
    old=audit([future],asof=OLD)
    assert old["status"]=="NO_SYNTHETIC_GRAPH_KNOWN_AT_CUT"
    assert old["visible_stages"] is None
    assert old["revision_keys"] is None
    assert "FUTURE" not in str(old)
    assert "aaa" not in str(old)


def test_orphan_edge_is_unknown_link_not_rejection_or_inadmission():
    a,b=key("REGISTRATION","A"),key("FILE","B")
    visible=audit([record(a)],[edge(a,b)])
    assert visible["orphan_claims_at_cut"]==1
    assert visible["real_negative_outcomes"] is None
    assert visible["actual_pending_at_cut"] is None
    assert visible["missing_link_is_not_rejection"]


@pytest.mark.parametrize("wrong",[
    "FUZZY_TITLE_MATCH", "SAME_PERSON_INFERRED", "GENERIC_EXTERNAL_CONTEXT",
    "DECISION_TO_PUBLICATION",
])
def test_fuzzy_inferences_and_mismatched_stages_rejected(wrong):
    with pytest.raises(GateError):
        edge(key("REGISTRATION","A"),key("FILE","B"),role=wrong)


def test_duplicate_edge_document_does_not_corroborate_itself():
    a,b=key("REGISTRATION","A"),key("FILE","B")
    e=edge(a,b)
    x=audit([record(a),record(b)],[e,replace(e,edge_id="SYNTHETIC:ANOTHER")])
    assert x["status"]=="DUPLICATE_EDGE_DOCUMENT_QUARANTINED"
    assert x["visible_claimed_edges"] is None


def test_id_or_claimed_sha_cannot_be_real_or_verified():
    with pytest.raises(GateError):
        key("FILE","REAL_ID",inst="REAL_INSTITUTION")
    a=key("FILE","A")
    with pytest.raises(GateError):
        replace(record(a),original_sha_claim="NO")
    with pytest.raises(GateError):
        replace(record(a),original_authenticated=True)
    with pytest.raises(GateError):
        replace(record(a),first_public_at="2026-10-10T00:00:00Z")


def test_uncertain_and_unbounded_observation_windows_fail_closed():
    a=key("FILE","A")
    unknown=record(a,known=KnowledgeInterval(None,None),captured=None)
    assert audit([unknown],asof="2040-01-01T00:00:00Z")[
        "visible_stage_total"] is None
    with pytest.raises(GateError,match="CAPTURE_BEFORE_FIRST_OBSERVATION_LOWER_BOUND"):
        record(a,known=KNOWN_LATE,captured="2026-10-30T10:00:00Z")


def test_event_cut_distinct_from_asof_disallows_future_legal_stages():
    a=key("REGISTRATION","A")
    b=key("FILE","B")
    x=audit([record(a),record(b,event="2021-01-01",doc="2021-01-02")],
            asof=NEW,cut="2020-12-31")
    assert x["visible_stages"]["REGISTRATION"]==1
    assert x["visible_stages"]["FILE"]==0
    with pytest.raises(GateError,match="LEGAL_EVENT_CUT_AFTER_KNOWLEDGE"):
        audit([record(a)],asof=OLD,cut="2030-01-01")


def test_same_day_legal_cut_requires_day_to_have_finished():
    a=key("REGISTRATION","A")
    known=KnowledgeInterval("2026-10-03T00:00:00Z","2026-10-03T00:00:01Z")
    same_day=record(a,event="2026-10-03",doc="2026-10-03",
                    known=known,captured="2026-10-03T00:00:01Z")
    with pytest.raises(GateError,match="LEGAL_EVENT_DAY_NOT_COMPLETED_AT_KNOWLEDGE"):
        audit([same_day],asof="2026-10-03T00:00:02Z",cut="2026-10-03")
    # The node may be observed that day, but the full-day cut is valid only
    # once the *next* UTC day begins. It does not become empirical evidence.
    completed=audit([same_day],asof="2026-10-04T00:00:00Z",cut="2026-10-03")
    assert completed["status"]=="SYNTHETIC_DOCUMENTARY_GRAPH_ONLY"
    assert completed["visible_stages"]["REGISTRATION"]==1
    assert completed["independent_all_received_denominator"] is None


def test_r21_explicit_issuer_local_edge_ids_are_not_global_identity():
    north_reg=key("REGISTRATION","N_IN",inst="SYNTHETIC:NORTH")
    north_file=key("FILE","N_FILE",inst="SYNTHETIC:NORTH")
    south_reg=key("REGISTRATION","S_IN",inst="SYNTHETIC:SOUTH")
    south_file=key("FILE","S_FILE",inst="SYNTHETIC:SOUTH")
    n=replace(edge(north_reg,north_file,name="LOCAL_1"),
              edge_id_scope="ISSUER_FRAME_LOCAL")
    s=replace(edge(south_reg,south_file,name="LOCAL_1"),
              edge_id_scope="ISSUER_FRAME_LOCAL")
    nodes=[record(k) for k in (north_reg,north_file,south_reg,south_file)]
    scoped=audit(nodes,[n,s])
    assert scoped["status"]=="SYNTHETIC_DOCUMENTARY_GRAPH_ONLY"
    assert scoped["visible_claimed_edges"]==2
    assert scoped["visible_stages"]["REGISTRATION"]==2
    assert scoped["independent_all_received_denominator"] is None
    assert scoped["official_cross_institution_links_authenticated"] is False
    # No silent downgrade of unscoped legacy claims: global ID collision
    # remains quarantined unless a producer explicitly declares local scope.
    unscoped=audit(nodes,[replace(n,edge_id_scope="GLOBAL_SYNTHETIC"),
                          replace(s,edge_id_scope="GLOBAL_SYNTHETIC")])
    assert unscoped["status"]=="VISIBLE_CONFLICTING_EDGE_CLAIM_QUARANTINED"


def test_r21_issuer_local_conflict_within_same_frame_still_quarantines():
    a=key("REGISTRATION","A")
    b=key("FILE","B")
    c=key("FILE","C")
    old=replace(edge(a,b,name="LOCAL_1"),edge_id_scope="ISSUER_FRAME_LOCAL")
    conflict=replace(edge(a,c,name="LOCAL_1"),edge_id_scope="ISSUER_FRAME_LOCAL")
    x=audit([record(a),record(b),record(c)],[old,conflict])
    assert x["status"]=="VISIBLE_CONFLICTING_EDGE_CLAIM_QUARANTINED"
    assert x["visible_claimed_edges"] is None


def test_r21_edge_namespace_must_be_explicitly_supported():
    a,b=key("REGISTRATION","A"),key("FILE","B")
    with pytest.raises(GateError,match="SYNTHETIC_STAGE_EDGE_ONLY"):
        replace(edge(a,b),edge_id_scope="FUZZY_ALIAS_NAMESPACE")
    with pytest.raises(GateError,match="SYNTHETIC_STAGE_EDGE_ONLY"):
        replace(edge(a,b),edge_id_scope=[])
