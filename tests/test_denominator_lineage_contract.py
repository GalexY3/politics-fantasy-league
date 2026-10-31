"""Denominator checks: no arithmetic across units, issuers or vintages."""
import pytest

from politics_fantasy.denominator_lineage_contract import (
    PopulationTarget,SourceTotalClaim,compare_total_claims,
)
from politics_fantasy.procedural_index_contract import GateError


def frame(**kw):
    p={"institution":"SYNTHETIC_CHAMBER","family":"ILP",
       "legislature_or_regime":"IX","entry_rule":"ALL_RECEIVED_REGISTRATION",
       "unit":"PARLIAMENTARY_INITIATIVE",
       "window_first_day":"2020-01-01","window_last_day":"2020-12-31"}
    p.update(kw)
    return PopulationTarget(**p)


def claim(name,*,target=None,n=10,issuer="SYNTHETIC_ISSUER",backend=None,
          documented=None):
    return SourceTotalClaim(name,target or frame(),n,issuer,backend,
                            "EDITORIAL_PAGE_COUNT",
                            locally_documented_safe_by=documented)


def test_same_publisher_equal_counts_not_independent():
    d=compare_total_claims(first=claim("PAGE_A",backend="FRONTEND"),
                           second=claim("PAGE_B",backend="OTHER_LABEL"))
    assert d["status"]=="SAME_ISSUER_NOT_EXTERNAL_CORROBORATION"
    assert d["editorial_counts_equal"]
    assert d["eligible_risk_population"] is None
    assert not d["independent_denominator_certified"]


def test_same_backend_different_issuers_not_independent():
    d=compare_total_claims(first=claim("PAGE_A",issuer="INSTITUTION_A",backend="SHARED_STORE"),
                           second=claim("PAGE_B",issuer="INSTITUTION_B",backend="SHARED_STORE"))
    assert d["status"]=="SAME_BACKEND_RESTATEMENT"
    assert d["eligible_risk_population"] is None


def test_unknown_and_different_declared_lineages_never_authenticated():
    a=claim("PAGE_A",issuer="INSTITUTION_A",backend="PUBLISHER_DB")
    b=claim("PAGE_B",issuer="INSTITUTION_B")
    assert compare_total_claims(first=a,second=b)["status"]=="UNKNOWN_BACKEND_DEPENDENCE"
    c=claim("PAGE_C",issuer="INSTITUTION_C",backend="INDEPENDENT_DB")
    d=compare_total_claims(first=a,second=c)
    assert d["status"]=="DIFFERENT_DECLARED_SYSTEMS_STILL_UNCERTIFIED"
    assert not d["independent_denominator_certified"]


def test_geography_and_channel_mismatch_is_not_equivalent_risk_frame():
    a=claim("AREA_A",target=frame(
        jurisdiction="SYNTHETIC_REGION_A",channel_scope="ELECTRONIC_CHANNEL"))
    for b in (
        claim("AREA_B",target=frame(jurisdiction="SYNTHETIC_REGION_B",
                                   channel_scope="ELECTRONIC_CHANNEL")),
        claim("PAPER",target=frame(jurisdiction="SYNTHETIC_REGION_A",
                                  channel_scope="PAPER_CHANNEL")),
        claim("UNVERIFIED",target=frame(jurisdiction=None,
                                       channel_scope="ELECTRONIC_CHANNEL")),
    ):
        x=compare_total_claims(first=a,second=b)
        assert x["status"]=="INCOMPATIBLE_UNITS_SCOPE_OR_ENTRY_RULE"
        assert x["frame_compatible"] is False
        assert x["eligible_risk_population"] is None
    same=claim("AREA_SAME",target=frame(jurisdiction="SYNTHETIC_REGION_A",
                                        channel_scope="ELECTRONIC_CHANNEL"))
    x=compare_total_claims(first=a,second=same)
    assert x["frame_compatible"] is True
    assert x["jurisdiction_and_channel_declared_for_both"] is True
    assert x["jurisdiction_and_channel_independently_verified"] is False
    assert not x["independent_denominator_certified"]


@pytest.mark.parametrize("override",[
    {"unit":"REGISTRY_INITIAL_WRITING"},
    {"entry_rule":"ADMISSION_FIRST"},
    {"institution":"SYNTHETIC_OTHER"},
    {"family":"PETITION"},
    {"window_last_day":"2021-12-31"},
])
def test_mismatched_units_entry_rules_and_periods_do_not_make_one_risk_set(override):
    d=compare_total_claims(first=claim("PAGE_A"),second=claim("PAGE_B",target=frame(**override)))
    assert d["status"]=="INCOMPATIBLE_UNITS_SCOPE_OR_ENTRY_RULE"
    assert d["frame_compatible"] is False
    assert d["eligible_risk_population"] is None


def test_future_source_counts_and_diagnostics_redacted():
    x=compare_total_claims(first=claim("PAGE_A",n=13),
                           second=claim("PAGE_B",n=14),
                           query_as_of="2020-06-01T00:00:00Z",
                           locally_known_safe_by="2026-11-01T00:00:00Z")
    assert x["status"]=="SOURCE_CLAIMS_NOT_KNOWN_AT_CUT"
    assert x["editorial_counts_equal"] is None
    assert x["backend_relation"] is None
    assert x["counter_claims"] is None
    assert x["eligible_risk_population"] is None


def test_individual_late_claim_not_unmasked_by_global_early_safe_by():
    first=claim("ONE",n=42,issuer="INSTITUTION_A",
                documented="2026-10-01T00:00:00Z")
    second=claim("TWO",n=42,issuer="INSTITUTION_B",
                 documented="2026-11-01T00:00:00Z")
    early=compare_total_claims(first=first,second=second,
        query_as_of="2026-10-11T00:00:00Z",
        locally_known_safe_by="2026-10-02T00:00:00Z")
    assert early["status"]=="SOURCE_CLAIMS_NOT_KNOWN_AT_CUT"
    assert early["counter_claims"] is None
    assert early["editorial_counts_equal"] is None
    assert early["backend_relation"] is None
    assert early["frame_compatible"] is None
    late=compare_total_claims(first=first,second=second,
        query_as_of="2026-11-01T00:00:00Z",
        locally_known_safe_by="2026-10-02T00:00:00Z")
    assert late["source_claims_visible"]
    assert late["independent_denominator_certified"] is False
    assert late["first_public_at"] is None


def test_missing_claim_specific_clock_fails_closed_for_historical_replay():
    one=claim("ONE",documented="2026-10-01T00:00:00Z")
    unknown=claim("TWO")
    old=compare_total_claims(first=one,second=unknown,
        query_as_of="2026-12-01T00:00:00Z",
        locally_known_safe_by="2026-10-01T00:00:00Z")
    assert not old["source_claims_visible"]
    assert old["counter_claims"] is None
    with pytest.raises(GateError):
        claim("BAD",documented="2026-10-31")


def test_future_claim_with_own_clock_never_defaults_to_present_when_cut_missing():
    a=claim("ONE",n=2,documented="2099-01-01T00:00:00Z")
    b=claim("TWO",n=4,documented="2099-01-02T00:00:00Z")
    r=compare_total_claims(first=a,second=b)
    assert r["status"]=="HISTORICAL_AS_OF_REQUIRED_FOR_DATED_CLAIMS"
    assert r["editorial_counts_equal"] is None
    assert r["counter_claims"] is None
    assert r["backend_relation"] is None
    assert r["frame_compatible"] is None
    assert not r["source_claims_visible"]
    assert r["first_public_at"] is None


def test_self_witness_replay_not_external_evidence():
    a=claim("PAGE_A")
    with pytest.raises(GateError,match="SELF_WITNESS_REPLAY"):
        compare_total_claims(first=a,second=a)


def test_no_first_public_promotion():
    with pytest.raises(GateError,match="INVALID_OR_PROMOTED"):
        SourceTotalClaim("S1",frame(),1,"ISSUER",None,"EDITORIAL_PAGE_COUNT",
                         historical_first_public_at="2020-01-01T00:00:00Z")


def test_invalid_claims_rejected():
    with pytest.raises(GateError):
        claim("WRONG",n=-1)
    with pytest.raises(GateError):
        frame(window_last_day="2019-01-01")
    with pytest.raises(GateError):
        SourceTotalClaim("S1",frame(),True,"ISSUER",None,"EDITORIAL_PAGE_COUNT")
