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
