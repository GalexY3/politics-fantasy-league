"""Synthetic contractual tests; no real case or outcome admission."""
from dataclasses import replace
import json
from hashlib import sha256

import pytest

from politics_fantasy.procedural_index_contract import (
    CaseRef, FrameScope, GateError, PageEvidence, audit_pages, RegistryEntry,
    StructuralAct, reconcile_registry_to_acts, prospective_capture_delta,
)

SCOPE = FrameScope(
    institution="PARLAMENTO_LAB", legislature="XI", family="PREGUNTA",
    risk_entry="SOURCE_REPORTED_REGISTRATION",
    selection_rule="UNKNOWN", registry_scope="PARTIAL_EDITORIAL_INDEX")


def make_page(n=1, total_pages=2, cases=("p1", "p2"), scope=SCOPE,
              stamp="2026-10-31T07:15:02Z", public_total=4, **kw):
    rows = tuple(CaseRef(x, "2026-10-22") for x in cases)
    return PageEvidence(
        page=n, expected_pages=total_pages,
        next_page=(n+1 if n<total_pages else None),
        source_sha256=sha256(f"page {n} {stamp} {cases}".encode()).hexdigest(),
        source_url=f"https://example.org/official/{n}",
        captured_at=stamp, source_reported_total=public_total,
        scope=scope, cases=rows,
        original_rights="GENERAL_NOTICE_UNRESOLVED", **kw)


def test_partial_index_is_not_a_denominator():
    frame = audit_pages([make_page()])
    assert frame.page_count==1 and frame.expected_pages==2
    assert frame.observed_case_rows==2
    assert frame.missing_pages==(2,)
    assert frame.source_reported_total==4
    assert frame.denominator_eligible_for_survival is None
    r=frame.report()
    assert r["publisher_total"]==4 and r["distinct_case_keys"]==2
    assert not r["publisher_index_complete_from_pagination"]
    assert r["risk_population_denominator"] is None
    assert not r["outcomes_admitted"] and not r["transitions_admitted"]
    assert "p1" not in json.dumps(r) and "p2" not in json.dumps(r)


def test_all_pages_equal_total_still_does_not_certify_registry_population():
    pages=[make_page(),make_page(n=2,cases=("p3","p4"),stamp="2026-10-31T07:15:03Z")]
    audit=audit_pages(pages,require_all_pages=True)
    report=audit.report()
    assert audit.distinct_case_keys==4
    assert audit.internal_publisher_count_equal is True
    assert not report["missing_pages"]
    assert report["publisher_index_complete_from_pagination"] is True
    assert not report["all_registered_confirmed_by_independent_registry"]
    assert report["risk_population_denominator"] is None
    assert report["censoring_estimable"] is False


def test_historical_asof_does_not_leak_future_page_or_count():
    audit=audit_pages([make_page()],require_all_pages=False)
    for instant in ("2026-10-30T00:00:00Z", "2026-10-31T07:15:02Z",
                    "2026-10-31T07:15:02.999999Z"):
        result=audit.report(as_of=instant)
        assert result["status"]=="INDEX_NOT_YET_OBSERVED_AT_CUT"
        assert result["observed_case_rows"] is None
        assert "p1" not in json.dumps(result)
        assert "4" not in json.dumps(result)
    visible=audit.report(as_of="2026-10-31T07:15:03Z")
    assert visible["observed_case_rows"]==2
    assert visible["local_observation_is_first_public_at"] is False


def test_mixed_source_types_incompatible_even_when_page_numbers_match():
    alt=replace(SCOPE, family="PROYECTO")
    with pytest.raises(GateError,match="SOURCE_FILTER_OR_EDITORIAL_TOTAL_DRIFT"):
        audit_pages([make_page(),make_page(n=2,scope=alt,cases=("p3","p4"))])


def test_pagination_must_not_merge_different_host_even_with_same_schema():
    page2=make_page(n=2,cases=("p3","p4"),stamp="2026-10-31T07:15:03Z")
    with pytest.raises(GateError,match="MIXED_SOURCE_HOSTS_OR_PUBLISHERS"):
        audit_pages([make_page(),replace(page2,source_url="https://other.example.org/official/2")])


def test_total_changes_during_pagination_is_never_silently_combined():
    with pytest.raises(GateError,match="SOURCE_FILTER_OR_EDITORIAL_TOTAL_DRIFT"):
        audit_pages([make_page(),make_page(n=2,cases=("p3","p4"),public_total=5)])


def test_pages_duplicated_out_of_order_or_gapped():
    with pytest.raises(GateError,match="DUPLICATE_OR_OUT_OF_ORDER_PAGES"):
        audit_pages([make_page(),make_page()])
    with pytest.raises(GateError,match="DUPLICATE_OR_OUT_OF_ORDER_PAGES"):
        audit_pages([make_page(n=2,cases=("p3","p4")),make_page()])
    with pytest.raises(GateError,match="NONCONTIGUOUS_PAGINATION"):
        audit_pages([make_page(total_pages=3),make_page(n=3,total_pages=3)])


def test_one_missing_page_is_not_a_zero_and_full_gate_rejects():
    with pytest.raises(GateError,match="MISSING_PAGES_AT_CENSUS_GATE"):
        audit_pages([make_page()], require_all_pages=True)
    report=audit_pages([make_page()]).report()
    assert report["missing_pages"]==[2]
    assert report["internal_publisher_count_equal"] is None


def test_source_ids_replay_conflict_and_duplicates():
    p1=make_page(cases=("same","p2"))
    p2=make_page(n=2,cases=("same","p3"),public_total=3,
                 stamp="2026-10-31T07:15:03Z")
    report=audit_pages([replace(p1,source_reported_total=3),p2]).report()
    assert report["duplicate_case_keys"]==1
    assert report["distinct_case_keys"]==3
    conflicting=replace(p2,cases=(CaseRef("same","2026-10-23"),CaseRef("p3","2026-10-22")))
    with pytest.raises(GateError,match="CONTRADICTORY_SOURCE_CASE_ENTRY"):
        audit_pages([replace(p1,source_reported_total=3),conflicting])


def test_replayed_source_page_sha_and_drift_in_capture_time_rejected():
    p1=make_page()
    p2=make_page(n=2,cases=("p3","p4"),stamp="2026-10-31T07:15:03Z")
    with pytest.raises(GateError,match="REPLAYED_OR_DUPLICATE_SOURCE_PAGE"):
        audit_pages([p1,replace(p2,source_sha256=p1.source_sha256)])
    with pytest.raises(GateError,match="CAPTURE_WINDOW_TOO_WIDE_FOR_STABLE_INDEX"):
        audit_pages([p1,replace(p2,captured_at="2026-11-01T08:15:02Z")])
    with pytest.raises(GateError,match="NONMONOTONE_PAGE_CAPTURES"):
        audit_pages([p1,replace(p2,captured_at="2026-10-31T07:15:01Z")])


def test_no_outcomes_or_artificial_first_publication():
    with pytest.raises(GateError,match="OUTCOME_OR_HISTORICAL_PUBLICATION_PROMOTION"):
        make_page(status_columns_inspected=True)
    with pytest.raises(GateError,match="OUTCOME_OR_HISTORICAL_PUBLICATION_PROMOTION"):
        make_page(first_public_at="2026-10-22T00:00:00Z")
    with pytest.raises(GateError,match="EVENT_DATE_AFTER_OBSERVATION"):
        PageEvidence(page=1,expected_pages=1,next_page=None,
            source_sha256="e"*64,source_url="https://example.org/source",
            captured_at="2026-10-31T00:00:00Z",source_reported_total=1,
            scope=SCOPE,cases=(CaseRef("p1","2026-11-01"),),
            original_rights="GENERAL_NOTICE_UNRESOLVED")


def test_cross_version_delta_does_not_relabel_additions_as_political_events():
    old=(make_page(total_pages=1,public_total=2,cases=("a","b")),)
    recent=(make_page(total_pages=1,public_total=2,cases=("b","c"),
            stamp="2026-11-02T07:15:02Z"),)
    d=prospective_capture_delta(old,recent)
    assert d["first_observed_only_in_later_index"]==1
    assert d["absent_from_later_index"]==1
    assert d["source_reported_entry_date_changed"]==0
    assert d["appeared_is_not_filed_event"] and d["disappeared_is_not_failed_outcome"]
    assert d["first_public_at"] is None
    assert d["events_or_outcomes_admitted"] is False
    assert '"a"' not in json.dumps(d) and '"b"' not in json.dumps(d)


def test_cross_scope_delta_fails_even_if_ids_equal():
    old=(make_page(total_pages=1,public_total=1,cases=("a",)),)
    recent=(make_page(total_pages=1,public_total=1,cases=("a"),
            scope=replace(SCOPE, institution="OTRA_CAMARA"),
            stamp="2026-11-02T07:15:02Z"),)
    with pytest.raises(GateError,match="CROSS_SCOPE_OR_INSTITUTIONAL_JOIN"):
        prospective_capture_delta(old,recent)


def test_ambiguous_timestamp_and_url_not_accepted():
    with pytest.raises(GateError,match="TIMESTAMP_NEEDS_TZ"):
        make_page(stamp="2026-10-31T07:15:02")
    with pytest.raises(GateError,match="INVALID_OFFICIAL_URL_CANDIDATE"):
        replace(make_page(),source_url="http://example.org/source")
    with pytest.raises(GateError,match="INVALID_OFFICIAL_URL_CANDIDATE"):
        replace(make_page(),source_url="https://attacker@bad.example/source")


def test_register_before_admission_is_not_identical_to_existing_case_or_event():
    scope=replace(SCOPE,selection_rule="ALL_REGISTERED_AT_RISK")
    entries=[
        RegistryEntry("E01","2026-10-01","P01"),
        RegistryEntry("E02","2026-10-02",None),
        RegistryEntry("E03","2026-10-03","P02"),
    ]
    events=[
        StructuralAct("T01","P01","2026-10-04","REFERRED_TO_DESK"),
        StructuralAct("T02","P02","2026-10-05","FILE_ASSIGNED"),
    ]
    d=reconcile_registry_to_acts(scope=scope,entries=entries,acts=events,
                                  captured_at="2026-10-31T10:00:00Z")
    assert d["recorded_entries"]==3
    assert d["registered_entries_without_process_assignment"]==1
    assert d["distinct_linked_processes"]==2
    assert d["structural_acts"]==2
    assert d["processes_in_both_register_and_act_stream"]==2
    assert d["unknown_is_not_failure"] and d["unlinked_is_not_rejected"]
    assert not d["eligible_registry_population_independently_verified"]
    assert not d["events_from_real_sources_admitted"]
    assert d["scientific_cycles"]==0
    assert "E01" not in json.dumps(d) and "T01" not in json.dumps(d)


def test_registry_unmatched_acts_and_no_act_do_not_imply_outcomes():
    scope=replace(SCOPE,selection_rule="ALL_REGISTERED_AT_RISK")
    d=reconcile_registry_to_acts(
       scope=scope,entries=[RegistryEntry("E01","2026-10-01","P01")],
       acts=[StructuralAct("T01","UNMATCHED","2026-10-20","PUBLICATION_REFERENCE")],
       captured_at="2026-10-31T08:00:00Z")
    assert d["registered_processes_without_act_in_this_stream"]==1
    assert d["act_stream_processes_without_registered_match"]==1
    assert d["unlinked_is_not_rejected"]
    assert d["terminal_outcomes_examined"] is False


@pytest.mark.parametrize("bad",[
    {"event_kind":"REJECTED"},
    {"event_kind":"APPROVED"},
    {"event_kind":"PENDING"},
    {"first_public_at":"2026-10-01T09:00:00Z"},
])
def test_no_outcome_or_fake_publication_allowed_as_structural_act(bad):
    opts=dict(event_id="T01",process_id="P01",occurred_on="2026-10-02",
              event_kind="FILE_ASSIGNED")
    with pytest.raises(GateError,match="TERMINAL_OUTCOME_KIND_FORBIDDEN|ACT_FIRST_PUBLICATION_NOT_VERIFIED"):
        StructuralAct(**(opts|bad))


def test_registration_dedup_and_impossible_date_are_adversarial():
    scope=replace(SCOPE,selection_rule="ALL_REGISTERED_AT_RISK")
    kw=dict(scope=scope,acts=(),captured_at="2026-10-31T08:00:00Z")
    with pytest.raises(GateError,match="DUPLICATE_REGISTER_ENTRY_CONFLICT"):
        reconcile_registry_to_acts(entries=[
             RegistryEntry("E01","2026-10-01","P01"),
             RegistryEntry("E01","2026-10-02","P01")],**kw)
    with pytest.raises(GateError,match="REGISTER_ISSUED_AFTER_CAPTURE"):
        reconcile_registry_to_acts(entries=[RegistryEntry("E02","2026-11-01",None)],**kw)
    with pytest.raises(GateError,match="REGISTER_FILTER_NOT_ALL_RECEIVED"):
        reconcile_registry_to_acts(entries=[],scope=SCOPE,acts=(),
                                   captured_at="2026-10-31T08:00:00Z")


def test_registry_event_dates_before_registration_flagged_not_reordered():
    scope=replace(SCOPE,selection_rule="ALL_REGISTERED_AT_RISK")
    d=reconcile_registry_to_acts(
      scope=scope,entries=[RegistryEntry("E01","2026-10-23","P01")],
      acts=[StructuralAct("T01","P01","2026-10-20","FILE_ASSIGNED")],
      captured_at="2026-10-31T08:00:00Z")
    assert d["act_dates_before_linked_register_date"]==1
    assert not d["source_first_public_at_verified"]
    assert not d["terminal_outcomes_examined"]
