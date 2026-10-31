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
    assert d["source_groups_visible"]==37


def test_source_scope_mutations_do_not_self_attest_census():
    x=report()
    sources=x["institutional_sources"]
    sources[0]["observed_metadata_rows"]=-1
    with pytest.raises(GateError,match="BAD_OBSERVED_COUNT"):
        derive_denominator_evidence(
            real_sources=sources,
            r9_documentary_status="R9_DISCOVERY_NOT_KNOWN_AT_CUT",
            r9_regional_highlights=[],r9_national_highlights=[])


def test_bad_source_registry_and_claimed_r9_promotion_rejected():
    x=report()
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
