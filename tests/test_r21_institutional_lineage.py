"""R21 C15 adversarial legal/documentary identity scenarios, synthetic only."""
from dataclasses import replace
from fractions import Fraction
import json

import pytest

from politics_fantasy.procedural_index_contract import GateError
from politics_fantasy.synthetic_institutional_demo import fixture, report
from politics_fantasy.synthetic_institutional_lineage import (
    InstitutionalVersion, InstitutionalLink, StageInstitutionBinding,
    audit_institutional_lineage,
)
from politics_fantasy.synthetic_temporal_witness import KnowledgeInterval

EARLY = "2026-04-01T00:00:00Z"
LATE = "2026-08-01T00:00:00Z"
BEFORE = "2026-02-01T00:00:00Z"


def audit(*, units=None, links=None, bindings=None, stages=None,
          stage_edges=None, as_of=LATE, cut_on="2023-12-31"):
    u,l,b,s,e=fixture()
    return audit_institutional_lineage(
        versions=u if units is None else units,
        links=l if links is None else links,
        bindings=b if bindings is None else bindings,
        stages=s if stages is None else stages,
        stage_edges=e if stage_edges is None else stage_edges,
        cut_on=cut_on, as_of=as_of,
        legal_calendar_zone="Europe/Madrid")


def test_r21_public_demo_explicit_current_versus_asof_never_real_data():
    earlier=report(as_of=EARLY)
    later=report(as_of=LATE)
    assert earlier["snapshot_mode"]=="HISTORICAL_SYNTHETIC_LAB"
    assert earlier["evidence_class"]=="SYNTHETIC_LAB_ONLY"
    assert earlier["complete_explicit_lineage_links"]==2
    assert later["complete_explicit_lineage_links"]==4
    assert earlier["link_classes"]["MERGER_PREDECESSOR"]==0
    assert later["link_classes"]["MERGER_PREDECESSOR"]==2
    assert earlier["distinct_active_legal_key_claims"]==2
    assert later["distinct_active_legal_key_claims"]==2
    assert later["legal_continuity_claimed_not_authenticated"]==3
    assert later["documentary_reference_not_legal_continuity"]==1
    assert later["all_received_denominator"] is None
    assert later["legal_identity_authenticated"] is False
    assert later["source_reuse_rights_verified"] is False
    assert later["functional_system_continuity_identified"] is False
    assert later["historical_first_public_at"] is None
    assert later["scientific_AB_cycles"]==0
    assert "SYNTHETIC:UNIT_A" not in json.dumps(later)
    assert "SECRETARIADO" not in json.dumps(later)
    assert "BODY_A" not in json.dumps(later)


def test_retroactive_alias_from_future_is_invisible_before_capture():
    before=audit(as_of=BEFORE)
    early=audit(as_of=EARLY)
    assert before["complete_explicit_lineage_links"]==0
    assert early["link_classes"]["LEGAL_RENAME_SAME_KEY"]==1
    assert before["known_version_claims"]==5
    assert before["stage_graph"]["visible_claimed_edges"]==1
    assert before["stage_graph"]["registered_at_risk_population_certified"] is False
    assert before["documentary_reference_not_legal_continuity"]==0


def test_same_nominal_label_across_unrelated_jurisdictions_creates_no_identity():
    u,l,b,s,e=fixture()
    # The two units already share a name; changing the label of a *third*
    # unit to match cannot change a single legal key, event, link, stage.
    mutated=tuple(replace(x,label="SYNTHETIC:OFICINA_COMUN")
                  if x.version_id=="SYNTHETIC:UNIT_C" else x for x in u)
    assert audit(units=mutated)==audit()
    assert audit()["distinct_active_legal_key_claims"]==2
    assert audit()["complete_explicit_lineage_links"]==4


def test_documentary_reference_is_not_legal_or_functional_continuity():
    out=audit()
    assert out["documentary_reference_not_legal_continuity"]==1
    assert out["legal_continuity_claimed_not_authenticated"]==3
    assert out["causal_feedback_or_reintroduction_identified"] is False


def test_only_one_known_merger_predecessor_does_not_become_one_to_one():
    u,l,b,s,e=fixture()
    only_first=tuple(x for x in l if x.link_id!="SYNTHETIC:MERGER_D")
    out=audit(links=only_first)
    assert out["link_classes"]["MERGER_PREDECESSOR"]==0
    assert out["incomplete_reorganization_groups"]==1
    assert out["complete_explicit_lineage_links"]==2
    assert out["real_pending"] is None


def test_split_two_successors_stays_distinct_no_entity_deduplication():
    u,l,b,s,e=fixture()
    splitter=replace(l[1], link_id="SYNTHETIC:SPLIT_1",
                     relation="SPLIT_SUCCESSOR", reorganization_id="SYNTHETIC:SPLIT",
                     source_version="SYNTHETIC:UNIT_A_NEW",
                     target_version="SYNTHETIC:UNIT_C",
                     expected_predecessors=1,expected_successors=2)
    split2=replace(splitter,link_id="SYNTHETIC:SPLIT_2",
                   target_version="SYNTHETIC:UNIT_B")
    out=audit(links=(splitter,split2))
    assert out["link_classes"]["SPLIT_SUCCESSOR"]==2
    assert out["distinct_active_legal_key_claims"]==2
    assert out["source_counts_additive"] is False


def test_same_version_id_with_conflicting_known_metadata_quarantines():
    u,l,b,s,e=fixture()
    injected=replace(u[0],label="SYNTHETIC:RETRO_FAKE")
    after=audit(units=(*u,injected))
    assert after["status"]=="SYNTHETIC_IDENTITY_CONFLICT_QUARANTINED"
    assert after["known_version_claims"] is None
    assert after["stage_graph"] is None
    assert "RETRO_FAKE" not in str(after)


def test_conflicting_future_unit_does_not_taint_older_knowledge():
    u,l,b,s,e=fixture()
    mutated=replace(u[0],label="SYNTHETIC:RETRO_FAKE",
                    observed=KnowledgeInterval(LATE,LATE),captured_at=LATE)
    assert audit(units=(*u,mutated),as_of=EARLY)==audit(as_of=EARLY)
    assert audit(units=(*u,mutated),as_of=LATE)[
        "status"]=="SYNTHETIC_IDENTITY_CONFLICT_QUARANTINED"


def test_overlap_same_legal_key_active_at_cut_fails_closed():
    u,l,b,s,e=fixture()
    bogus=replace(u[0],version_id="SYNTHETIC:OVERLAPPING",
                  valid_from="2022-01-01",valid_until=None)
    # Both UNIT_A_NEW and the forged version are active in June 2022.
    x=audit(units=(*u,bogus),cut_on="2022-06-01")
    assert x["status"]=="SYNTHETIC_IDENTITY_CONFLICT_QUARANTINED"
    assert x["quarantine_reason"]=="COMPETING_ACTIVE_LEGAL_KEY_DESCRIPTIONS"


def test_rename_to_different_legal_key_not_a_rename():
    u,l,b,s,e=fixture()
    bad=replace(l[0],target_version="SYNTHETIC:UNIT_B")
    r=audit(links=(bad,*l[1:]))
    assert r["status"]=="SYNTHETIC_IDENTITY_CONFLICT_QUARANTINED"
    assert r["quarantine_reason"]=="RENAME_CHANGED_LEGAL_KEY"


def test_merger_does_not_collapse_source_and_target_legal_key():
    u,l,b,s,e=fixture()
    mutated=replace(u[4],legal_key_claim="SYNTHETIC:LEGAL_A")
    x=audit(units=(*u[:4],mutated))
    assert x["status"]=="SYNTHETIC_IDENTITY_CONFLICT_QUARANTINED"


def test_spurious_transfer_without_explicit_dual_keys_is_quarantined():
    u,l,b,s,e=fixture()
    bad=replace(l[1],dual_official_keys_documented=False)
    result=audit(links=(l[0],bad,*l[2:]))
    assert result["quarantine_reason"]=="NO_EXPLICIT_DUAL_OFFICIAL_KEY_EVIDENCE"
    assert result["complete_explicit_lineage_links"] is None


def test_replayed_identical_link_is_not_independent_corrobation():
    u,l,b,s,e=fixture()
    assert audit(links=(*l,l[0]))==audit()


def test_conflicting_link_id_cannot_rewrite_before_known_capture():
    u,l,b,s,e=fixture()
    fake=replace(l[1],source_version="SYNTHETIC:UNIT_B",
                 observed=KnowledgeInterval("2026-10-01T00:00:00Z",
                                            "2026-10-01T00:00:00Z"),
                 captured_at="2026-10-01T00:00:00Z")
    assert audit(links=(*l,fake),as_of=LATE)==audit(as_of=LATE)
    later=audit(links=(*l,fake),as_of="2026-11-01T00:00:00Z")
    assert later["status"]=="SYNTHETIC_IDENTITY_CONFLICT_QUARANTINED"
    assert later["quarantine_reason"]=="CONFLICTING_KNOWN_LINEAGE_LINK"


def test_undefined_link_and_bogus_rights_and_ids_fail_at_construction():
    u,l,b,s,e=fixture()
    with pytest.raises(GateError):
        replace(l[0],relation="SIMILAR_NAMES")
    with pytest.raises(GateError):
        replace(l[0],original_authenticated=True)
    with pytest.raises(GateError):
        replace(u[0],legal_original_authenticated=True)
    with pytest.raises(GateError):
        replace(u[0],legal_key_claim="REAL_LEGAL_ID")
    with pytest.raises(GateError):
        replace(l[0],first_public_at="2020-01-01T00:00:00Z")
    with pytest.raises(GateError):
        replace(l[1],expected_predecessors=1)
    with pytest.raises(GateError):
        replace(l[1],expected_predecessors=1.0)


def test_unknown_future_stage_binding_does_not_join_by_label():
    u,l,b,s,e=fixture()
    delayed=replace(b[1],
                    observed=KnowledgeInterval(LATE,LATE),
                    captured_at=LATE)
    before=audit(bindings=(b[0],delayed),as_of=EARLY)
    after=audit(bindings=(b[0],delayed),as_of=LATE)
    assert before["stage_graph"]["visible_claimed_edges"]==0
    assert after["stage_graph"]["visible_claimed_edges"]==1
    assert before["stage_graph"]["unlinked_visible_registrations"]==1


def test_binding_across_mismatched_institution_namespace_rejected():
    u,l,b,s,e=fixture()
    wrong=replace(b[0],version_id="SYNTHETIC:UNIT_B")
    x=audit(bindings=(wrong,b[1]))
    assert x["status"]=="SYNTHETIC_IDENTITY_CONFLICT_QUARANTINED"
    assert x["quarantine_reason"]=="STAGE_INSTITUTION_NAMESPACE_MISMATCH"


def test_stage_binding_cannot_assign_2020_registration_to_2021_legal_version():
    # Same institution namespace/alias, different effective legal interval:
    # a future legal version cannot retrospectively own an earlier receipt.
    u,l,b,s,e=fixture()
    impossible=replace(b[0],version_id="SYNTHETIC:UNIT_A_NEW")
    x=audit(bindings=(impossible,b[1]))
    assert x["status"]=="SYNTHETIC_IDENTITY_CONFLICT_QUARANTINED"
    assert x["quarantine_reason"]=="STAGE_EVENT_OUTSIDE_INSTITUTIONAL_VALIDITY"
    assert x["stage_graph"] is None


def test_empty_or_preobservation_cut_never_leaks_future_named_entities():
    x=audit(as_of="2025-12-31T00:00:00Z")
    assert x["known_version_claims"]==0
    assert x["stage_graph"]["visible_stages"] is None
    assert "BODY" not in str(x) and "UNIT_" not in str(x)


def test_invalid_cut_lacks_fallback_to_current():
    with pytest.raises(GateError):
        report(as_of="invalid")
    with pytest.raises(GateError):
        report(as_of=EARLY,cut_on="2026-04-01")
    with pytest.raises(GateError):
        audit_institutional_lineage(
            versions=(),links=(),bindings=(),stages=(),stage_edges=(),
            cut_on="2023-12-31",as_of=LATE,
            legal_calendar_zone="SYNTHETIC:UNSUPPORTED_ZONE")


def test_result_is_immune_to_python_floats_and_poisoned_fields():
    u,l,b,s,e=fixture()
    with pytest.raises(GateError):
        audit(units=(*u,None))
    with pytest.raises(GateError):
        replace(l[1],expected_successors=False)
    with pytest.raises(GateError):
        replace(b[0],independently_authenticated=True)
