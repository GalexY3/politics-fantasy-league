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


def claim(name,*,target=None,n=10,issuer="SYNTHETIC_ISSUER",backend=None):
    return SourceTotalClaim(name,target or frame(),n,issuer,backend,
                            "EDITORIAL_PAGE_COUNT")


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
