"""Source-specific views must be historically non-enumerative."""
from copy import deepcopy
import pytest

from politics_fantasy.procedural_population_readiness import report
from politics_fantasy.source_scope_query import filter_denominator_source
from politics_fantasy.procedural_index_contract import GateError


def test_only_source_local_scope_can_be_selected_without_mixing_denominators():
    d=report(as_of="2026-11-01T00:00:00Z")["denominator_evidence"]
    x=filter_denominator_source(d,"PARCAN_SOURCE_LOCAL")
    assert x["source_groups_visible"]==1
    assert len(x["reported_sources"])==1
    assert x["reported_sources"][0]["source_id"]=="PARCAN_SOURCE_LOCAL"
    assert x["reported_sources"][0]["observed_source_local_items"]==1754
    assert x["reported_sources"][0]["eligible_all_received_denominator"] is None
    assert x["eligible_risk_denominator"] is None
    assert x["case_level_right_censoring_observed_for_analysis"] is None
    assert x["selection_status"]=="SOURCE_VISIBLE_WITH_LIMITATIONS"


def test_new_r11_administrative_source_cannot_promote_documentary_claim_to_case_frame():
    d=report(as_of="2026-11-01T00:00:00Z")["denominator_evidence"]
    x=filter_denominator_source(d,"R11_A_PLACSP")
    assert x["source_groups_visible"]==1
    assert x["reported_sources"][0]["source_status"]=="DOCUMENTARY_ONLY_NO_ORIGINAL_OR_ACCEPTED_TERMS"
    assert x["reported_sources"][0]["eligible_all_received_denominator"] is None


def test_future_source_request_indistinguishable_from_unknown_at_past_cut():
    d=report(as_of="2024-01-01T00:00:00Z")["denominator_evidence"]
    a=filter_denominator_source(d,"R10_A_CTBG_APPEALS")
    b=filter_denominator_source(d,"NOT_A_SOURCE")
    assert a==b
    assert a["reported_sources"]==[]
    assert a["source_groups_visible"]==0
    assert a["selection_status"]=="SOURCE_NOT_KNOWN_AT_CUT_OR_UNAVAILABLE"
    assert "CTBG" not in str(a)
    assert "ANDALUCIA" not in str(a)


def test_source_missing_in_visible_window_still_no_leak_of_prepared_pool():
    d=report()["denominator_evidence"]
    unknown=filter_denominator_source(d,"R100_PENDING_FUTURE")
    assert unknown["selection_status"]=="SOURCE_NOT_KNOWN_AT_CUT_OR_UNAVAILABLE"
    assert unknown["eligible_risk_denominator"] is None
    assert unknown["real_case_outcomes_observed_for_analysis"] is None


@pytest.mark.parametrize("bad",[
    "", "X"*161, "source name", "foo&source_id=other",
    "<script>", "a\nitem", "á", "..\\private",
])
def test_untrusted_source_id_is_rejected(bad):
    with pytest.raises(GateError,match="INVALID_PUBLIC_SOURCE_ID"):
        filter_denominator_source(report()["denominator_evidence"],bad)


def test_duplicate_source_identity_fails_closed():
    d=deepcopy(report()["denominator_evidence"])
    d["reported_sources"].append(d["reported_sources"][0])
    with pytest.raises(GateError,match="DUPLICATE_INSTITUTIONAL_SOURCE_ID"):
        filter_denominator_source(d,d["reported_sources"][0]["source_id"])


def test_no_select_is_existing_aggregate_not_new_risk_set():
    d=report()["denominator_evidence"]
    assert filter_denominator_source(d,None) is d
    assert d["eligible_risk_denominator"] is None


def test_bad_input_is_rejected():
    with pytest.raises(GateError,match="UNTRUSTED_DENOMINATOR_AGGREGATE"):
        filter_denominator_source({"schema":"bad"},"PARCAN_SOURCE_LOCAL")


def test_unrequested_extraneous_fields_cannot_ride_along_in_full_projection():
    d=deepcopy(report(as_of="2026-11-01T00:00:00Z")["denominator_evidence"])
    d["reported_sources"][1]["mock_later_decision"]="SYNTHETIC:OUTCOME"
    for choice in (None,"PARCAN_SOURCE_LOCAL"):
        with pytest.raises(GateError,match="UNTRUSTED_DENOMINATOR_SOURCE_FIELDS"):
            filter_denominator_source(d,choice)


@pytest.mark.parametrize("key,value",[
    ("eligible_all_received_denominator",999),
    ("known_pending_case_count",0),
    ("right_censored_case_count",3),
    ("known_terminal_case_count",100),
    ("official_cross_institution_links_admitted",True),
])
def test_outcome_or_census_promotions_cannot_pass_projection(key,value):
    d=deepcopy(report(as_of="2026-11-01T00:00:00Z")["denominator_evidence"])
    d["reported_sources"][0][key]=value
    with pytest.raises(GateError,match="UNATTESTED_DENOMINATOR_SOURCE_PROMOTION"):
        filter_denominator_source(d,"R13_A")


def test_duplicate_elsewhere_does_not_pass_full_or_other_source_query():
    d=deepcopy(report(as_of="2026-11-01T00:00:00Z")["denominator_evidence"])
    d["reported_sources"].append(d["reported_sources"][-1])
    for choice in (None,"PARCAN_SOURCE_LOCAL"):
        with pytest.raises(GateError,match="DUPLICATE_INSTITUTIONAL_SOURCE_ID"):
            filter_denominator_source(d,choice)


def test_inconsistent_aggregate_count_or_top_level_extra_data_rejected():
    d=deepcopy(report(as_of="2026-11-01T00:00:00Z")["denominator_evidence"])
    d["source_groups_visible"]+=1
    with pytest.raises(GateError,match="UNTRUSTED_DENOMINATOR_SOURCE_ROWS"):
        filter_denominator_source(d,None)
    d=deepcopy(report(as_of="2026-11-01T00:00:00Z")["denominator_evidence"])
    d["future_sensitive_hash"]="syntheticprivate"
    with pytest.raises(GateError,match="UNTRUSTED_DENOMINATOR_AGGREGATE"):
        filter_denominator_source(d,None)


@pytest.mark.parametrize("field,value",[
    ("editorial_total_equals_rows_proves_census",True),
    ("source_groups_additive",True),
    ("index_discovery_without_original_not_counted_as_frame",False),
    ("boe_only_approved_laws_not_full_intake",False),
    ("synthetic_denominator_comparisons_are_not_empirical",False),
    ("post_admission_selection_is_not_pre_mesa_rejection",False),
])
def test_flags_cannot_be_changed_into_census_by_pass_through(field,value):
    d=deepcopy(report(as_of="2026-11-01T00:00:00Z")["denominator_evidence"])
    d[field]=value
    with pytest.raises(GateError,match="UNATTESTED_DENOMINATOR_AGGREGATE_PROMOTION"):
        filter_denominator_source(d,"PARCAN_SOURCE_LOCAL")


@pytest.mark.parametrize("field,value",[
    ("source_status","CERTIFIED_ALL_RECEIVED_REGISTER"),
    ("entry_rule_status","REGISTERED_ALL_CHANNELS_INCLUSIVE"),
    ("institution",3),
])
def test_synthetic_caller_cannot_forge_entry_classification(field,value):
    d=deepcopy(report(as_of="2026-11-01T00:00:00Z")["denominator_evidence"])
    d["reported_sources"][0][field]=value
    with pytest.raises(GateError,match="UNTRUSTED_DENOMINATOR_SOURCE_CLASSIFICATION"):
        filter_denominator_source(d,None)
