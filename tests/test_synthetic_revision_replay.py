"""R12: no future revisions, no joins by names, and no paper-only denominators."""
from dataclasses import replace

import pytest

from politics_fantasy.denominator_lineage_contract import PopulationTarget
from politics_fantasy.procedural_index_contract import GateError
from politics_fantasy.synthetic_revision_replay import (
    SourceRevision, DualIdClaim, EventClaim, replay,
)

S="f"*64
EARLY="2026-10-30T10:30:30Z"
LATE="2026-11-02T12:30:30Z"
REG="SYNTHETIC:REG:REGISTER:PAPER:1"
REG2="SYNTHETIC:REG:REGISTER:PAPER:2"
CASE="SYNTHETIC:CASE:MESA:ILP:1"
CASE2="SYNTHETIC:CASE:MESA:ILP:2"


def frame(**changes):
    x=dict(institution="SYNTHETIC_PARLIAMENT",family="ILP",
           legislature_or_regime="XIV",entry_rule="ALL_RECEIVED_REGISTRATION",
           unit="PARLIAMENTARY_INITIATIVE",
           window_first_day="2020-01-01",window_last_day="2020-12-31")
    x.update(changes)
    return PopulationTarget(**x)


def rev(role,_,*,captured=EARLY,precision="SECOND",entries=(),cases=(),links=(),
        events=(),scope=None,source=None):
    return SourceRevision("SYNTHETIC:REV:"+_,
                          source or "SYNTHETIC:SOURCE:"+role,scope or frame(),
                          role,captured,precision,S,entries,cases,links,events)


def test_cut_hides_even_revision_names_and_all_diagnostics():
    src=rev("ENTRY_BOOK","A",entries=(REG,))
    old=replay(target=frame(),revisions=(src,),as_of="2020-01-01T00:00:00Z")
    assert old["status"]=="NO_LOCAL_SNAPSHOT_KNOWN_AT_CUT"
    assert old["visible_entry_ids"] is None
    assert old["source_revisions_visible"] is None
    assert old["orphan_link_claims"] is None
    assert old["first_public_at"] is None


def test_second_precision_protects_capture_boundary():
    src=rev("ENTRY_BOOK","A",entries=(REG,),captured=EARLY)
    assert replay(target=frame(),revisions=(src,),as_of=EARLY)["visible_entry_ids"] is None
    assert replay(target=frame(),revisions=(src,),as_of="2026-10-30T10:30:31Z")["visible_entry_ids"]==1


def test_independent_roles_require_explicit_two_key_link():
    entries=rev("ENTRY_BOOK","A",entries=(REG,REG2))
    cases=rev("CASE_LEDGER","B",cases=(CASE,))
    link=rev("EXPLICIT_DUAL_ID","C",links=(DualIdClaim(REG,CASE),))
    preview=replay(target=frame(),revisions=(entries,cases,link),
                   as_of="2026-11-01T00:00:00Z")
    assert preview["visible_entry_ids"]==2
    assert preview["visible_case_ids"]==1
    assert preview["dual_id_edges_valid_in_visible_frames"]==1
    assert preview["registered_without_documented_case_link"]==1
    assert preview["unlinked_is_not_inadmitted"]
    assert preview["independent_all_received_denominator"] is None
    assert preview["actual_population_membership"] is None


def test_future_link_source_hidden_despite_event_date_much_earlier():
    source=rev("ENTRY_BOOK","A",entries=(REG,))
    cas=rev("CASE_LEDGER","B",cases=(CASE,))
    link=rev("EXPLICIT_DUAL_ID","C",captured=LATE,
             links=(DualIdClaim(REG,CASE),))
    r1=replay(target=frame(),revisions=(source,cas,link),
              as_of="2026-11-01T00:00:00Z")
    r2=replay(target=frame(),revisions=(source,cas,link),
              as_of="2026-11-02T12:30:31Z")
    assert r1["dual_id_edges_valid_in_visible_frames"]==0
    assert r2["dual_id_edges_valid_in_visible_frames"]==1


def test_latest_same_source_revision_replaces_not_adds_entires():
    first=rev("ENTRY_BOOK","A",entries=(REG,REG2))
    second=replace(rev("ENTRY_BOOK","B",source=first.source_id,captured=LATE,
               entries=(REG2,)),original_sha_claim="e"*64)
    r1=replay(target=frame(),revisions=(first,second),
              as_of="2026-11-01T00:00:00Z")
    r2=replay(target=frame(),revisions=(first,second),
              as_of="2026-11-02T12:30:31Z")
    assert r1["visible_entry_ids"]==2
    assert r2["visible_entry_ids"]==1
    assert r2["repeated_revisions_not_new_cases"]
    assert r2["terminal_claims_by_type"]["REJECTED"]==0
    assert r2["unobserved_is_not_rejection_withdrawal_or_censor"]


def test_event_not_visible_until_its_revision_is_captured():
    case=rev("CASE_LEDGER","A",cases=(CASE,))
    e=rev("DECISION_EVENTS","B",captured=LATE,events=(
        EventClaim(CASE,"REJECTED","2020-02-01","2020-02-02"),))
    early=replay(target=frame(),revisions=(case,e),
                 as_of="2026-11-01T00:00:00Z")
    later=replay(target=frame(),revisions=(case,e),
                 as_of="2026-11-02T12:30:31Z")
    assert early["terminal_claims_by_type"]["REJECTED"]==0
    assert later["terminal_claims_by_type"]["REJECTED"]==1
    assert later["historical_public_predictor_certified"] is False


def test_disagreeing_terminal_claims_quarantined_not_double_counted():
    case=rev("CASE_LEDGER","A",cases=(CASE,))
    events=rev("DECISION_EVENTS","B",events=(
        EventClaim(CASE,"REJECTED","2020-02-01","2020-02-02"),
        EventClaim(CASE,"APPROVED","2020-03-01","2020-03-02"),))
    result=replay(target=frame(),revisions=(case,events),
                  as_of="2026-11-01T00:00:00Z")
    assert result["contradictory_terminal_claims_quarantined"]==1
    assert not any(result["terminal_claims_by_type"].values())


def test_pending_at_document_date_not_still_pending_at_later_cut():
    case=rev("CASE_LEDGER","A",cases=(CASE,))
    events=rev("DECISION_EVENTS","B",events=(
        EventClaim(CASE,"PENDING_AT_DOCUMENT_DATE","2020-02-01","2020-02-02"),))
    r=replay(target=frame(),revisions=(case,events),as_of="2026-11-01T00:00:00Z")
    assert r["pending_at_document_date_claims"]==1
    assert r["pending_at_document_date_not_followup_cut"]


@pytest.mark.parametrize("bad",["REAL:1","SYNTHETIC:CASE:5","<img>","SYNTHETIC:REG:0<script>","SYNTHETIC:REG:1"])
def test_register_namespace_and_injection_refused(bad):
    with pytest.raises(GateError):
        DualIdClaim(bad,CASE)


def test_orphan_link_counts_are_not_failures():
    source=rev("ENTRY_BOOK","A",entries=(REG,))
    candidate=rev("EXPLICIT_DUAL_ID","B",links=(DualIdClaim(REG,CASE),))
    r=replay(target=frame(),revisions=(source,candidate),
             as_of="2026-11-01T00:00:00Z")
    assert r["orphan_link_claims"]==1
    assert r["registered_without_documented_case_link"]==1
    assert r["terminal_claims_by_type"]["INADMITTED"]==0


def test_identical_numeric_registry_ids_in_different_channels_do_not_join():
    electronic="SYNTHETIC:REG:REGISTER:ELECTRONIC:1"
    entries=rev("ENTRY_BOOK","A",entries=(REG,electronic))
    cases=rev("CASE_LEDGER","B",cases=(CASE,))
    link=rev("EXPLICIT_DUAL_ID","C",links=(DualIdClaim(REG,CASE),))
    r=replay(target=frame(),revisions=(entries,cases,link),
             as_of="2026-11-01T00:00:00Z")
    assert r["visible_entry_ids"]==2
    assert r["dual_id_edges_valid_in_visible_frames"]==1
    assert r["registered_without_documented_case_link"]==1


def test_source_role_grain_must_not_mix_documents():
    with pytest.raises(GateError,match="HETEROGENEOUS_EVENT"):
        rev("ENTRY_BOOK","A",entries=(REG,),cases=(CASE,))


def test_cross_family_scope_never_replayed_together():
    other=rev("ENTRY_BOOK","A",scope=frame(family="PETICIONES"),entries=(REG,))
    with pytest.raises(GateError,match="REAL_OR_MIXED"):
        replay(target=frame(),revisions=(other,),as_of="2026-11-01T00:00:00Z")


def test_identical_revision_ids_and_conflicting_same_capture_refused():
    src=rev("ENTRY_BOOK","A",entries=(REG,))
    with pytest.raises(GateError,match="DUPLICATE_REVISION_ID"):
        replay(target=frame(),revisions=(src,src),as_of="2026-11-01T00:00:00Z")
    rival=rev("ENTRY_BOOK","B",source=src.source_id,entries=(REG2,))
    with pytest.raises(GateError,match="CONFLICTING_REVISIONS"):
        replay(target=frame(),revisions=(src,rival),as_of="2026-11-01T00:00:00Z")


def test_identical_sha_of_same_distribution_cannot_claim_different_rows():
    first=rev("ENTRY_BOOK","A",entries=(REG,))
    second=rev("ENTRY_BOOK","B",source=first.source_id,captured=LATE,entries=(REG2,))
    with pytest.raises(GateError,match="SAME_ORIGINAL_SHA_CANNOT_CHANGE"):
        replay(target=frame(),revisions=(first,second),
               as_of="2026-11-02T12:30:31Z")


def test_date_precision_overlap_with_same_day_second_cannot_be_ordered():
    first=rev("ENTRY_BOOK","A",entries=(REG,),
              captured="2026-10-31T00:00:00Z",precision="DATE")
    second=replace(rev("ENTRY_BOOK","B",source=first.source_id,
                       captured="2026-10-31T12:00:00Z",precision="SECOND",
                       entries=(REG2,)),original_sha_claim="d"*64)
    with pytest.raises(GateError,match="CONFLICTING_REVISIONS"):
        replay(target=frame(),revisions=(first,second),
               as_of="2026-11-01T00:00:00Z")


def test_no_false_real_certificate_and_no_first_public_hack():
    src=rev("ENTRY_BOOK","A",entries=(REG,))
    with pytest.raises(GateError,match="SCIENCE_PROMOTION"):
        replace(src,all_received_certified=True)
    with pytest.raises(GateError,match="SCIENCE_PROMOTION"):
        replace(src,independent_denominator_certified=True)
    with pytest.raises(GateError,match="SCIENCE_PROMOTION"):
        replace(src,first_public_at="2020-01-01T00:00:00Z")
    with pytest.raises(GateError,match="REVISION_NOT_SYNTHETIC"):
        replace(src,revision_id="PUBLIC:ENTRY001")


def test_date_only_precision_safe_at_following_midnight():
    x=rev("ENTRY_BOOK","A",entries=(REG,),
          captured="2026-10-31T00:00:00Z",precision="DATE")
    assert replay(target=frame(),revisions=(x,),
                  as_of="2026-10-31T23:59:59Z")["visible_entry_ids"] is None
    assert replay(target=frame(),revisions=(x,),
                  as_of="2026-11-01T00:00:00Z")["visible_entry_ids"]==1


def test_date_document_future_and_invalid_resource_inputs_fail():
    with pytest.raises(GateError,match="DOCUMENTED_EVENT_AFTER_CAPTURE"):
        rev("DECISION_EVENTS","A",events=(
            EventClaim(CASE,"REJECTED","2026-12-01","2026-12-01"),))
    with pytest.raises(GateError,match="REVISION_RESOURCE"):
        rev("ENTRY_BOOK","B",entries=[REG])


def test_census_excluded_when_all_revisions_synthetic():
    src=rev("ENTRY_BOOK","A",entries=(REG,))
    data=replay(target=frame(),revisions=(src,),as_of="2026-11-01T00:00:00Z")
    assert data["scientific_cycles"]==0
    assert data["real_originals_verified"] is False
    assert data["independent_all_received_denominator"] is None
    assert data["first_public_at"] is None
