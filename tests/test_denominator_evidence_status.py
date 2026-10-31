"""Real source-scoped coverage is non-additive and history-safe."""
import pytest

from politics_fantasy.denominator_evidence_status import derive_denominator_evidence
from politics_fantasy.procedural_population_readiness import report
from politics_fantasy.procedural_index_contract import GateError


def test_actual_metadata_returns_frames_not_inferred_denominators():
    x=report()
    d=x["denominator_evidence"]
    assert d["schema"]=="pfl.denominator_evidence_nonadditive.v1"
    assert not d["source_groups_additive"]
    assert d["eligible_risk_denominator"] is None
    assert d["case_level_right_censoring_observed_for_analysis"] is None
    assert len(d["reported_sources"])==37
    assert [s["observed_source_local_items"] for s in d["reported_sources"][:2]]==[1754,20]
    assert d["index_discovery_without_original_not_counted_as_frame"]
    assert all(s["eligible_all_received_denominator"] is None for s in d["reported_sources"])
    assert all(s["known_pending_case_count"] is None for s in d["reported_sources"])
    assert all(s["known_terminal_case_count"] is None for s in d["reported_sources"])
    assert all(not s["case_level_competing_risks_admitted"] for s in d["reported_sources"])


def test_prior_cut_not_leak_r9_catalogue_or_local_source_counts():
    d=report(as_of="2024-01-01T00:00:00Z")["denominator_evidence"]
    assert d["source_groups_visible"]==0
    assert d["reported_sources"]==[]
    assert "Galicia" not in str(d)
    assert "Catalunya" not in str(d)
    assert "CONGRESO_XV" not in str(d)
    assert d["eligible_risk_denominator"] is None
    d=report(as_of="2026-11-01T00:00:00Z")["denominator_evidence"]
    assert d["source_groups_visible"]==47
    assert all(s["eligible_all_received_denominator"] is None for s in d["reported_sources"][-4:])
    assert len({s["source_id"] for s in d["reported_sources"][-4:]})==4
    assert all(s["observed_source_local_items"] is None for s in d["reported_sources"][-4:])


def test_source_scope_mutations_do_not_self_attest_census():
    x=report(as_of="2026-11-01T00:00:00Z")
    sources=x["institutional_sources"]
    sources[0]["observed_metadata_rows"]=-1
    with pytest.raises(GateError,match="BAD_OBSERVED_COUNT"):
        derive_denominator_evidence(
            real_sources=sources,
            r9_documentary_status="R9_DISCOVERY_NOT_KNOWN_AT_CUT",
            r9_regional_highlights=[],r9_national_highlights=[])


def test_bad_source_registry_and_claimed_r9_promotion_rejected():
    x=report(as_of="2026-11-01T00:00:00Z")
    with pytest.raises(GateError,match="REAL_SOURCE_REGISTRY"):
        derive_denominator_evidence(real_sources=x["institutional_sources"][:2],
            r9_documentary_status="R9_DISCOVERY_NOT_KNOWN_AT_CUT",
            r9_regional_highlights=[],r9_national_highlights=[])
    regions=x["r9_regional_highlights"]
    regions[0]["source_eligible"]=True
    with pytest.raises(GateError,match="R9_SOURCE_SCOPING_PROMOTION"):
        derive_denominator_evidence(real_sources=x["institutional_sources"],
            r9_documentary_status="R9_DISCOVERY_ONLY_RIGHTS_AND_DENOMINATORS_BLOCKED",
            r9_regional_highlights=regions,
            r9_national_highlights=x["r9_national_highlights"])


def test_documentary_denominator_assembler_needs_real_source_owned_asof():
    p=report(as_of="2026-11-01T00:00:00Z")
    kwargs=dict(real_sources=p["institutional_sources"],
                r9_documentary_status="R9_DISCOVERY_ONLY_RIGHTS_AND_DENOMINATORS_BLOCKED",
                r9_regional_highlights=p["r9_regional_highlights"],
                r9_national_highlights=p["r9_national_highlights"])
    with pytest.raises(GateError,match="DOCUMENTARY_SOURCE_NOT_IN_KNOWLEDGE_AT_CUT"):
        derive_denominator_evidence(as_of="2010-01-01T00:00:00Z",**kwargs)
    with pytest.raises(GateError,match="DOCUMENTARY_SOURCE_NOT_IN_KNOWLEDGE_AT_CUT"):
        derive_denominator_evidence(**kwargs)
    with pytest.raises(GateError,match="MIXED_HISTORICAL_AND_CURRENT_KNOWLEDGE_MODE"):
        derive_denominator_evidence(as_of="2026-11-01T00:00:00Z",
            explicit_current_mode=True,**kwargs)
    current=derive_denominator_evidence(explicit_current_mode=True,**kwargs)
    assert current["source_groups_visible"]>2
    assert current["eligible_risk_denominator"] is None
    visible=derive_denominator_evidence(as_of="2026-11-01T00:00:00Z",**kwargs)
    assert visible["source_groups_visible"]>2
    assert visible["eligible_risk_denominator"] is None
