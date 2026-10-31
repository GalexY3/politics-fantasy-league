"""Small, immutable, offline-only R21 institutional-lineage demonstrator.

Neither names, SHA claims, dates nor IDs in this fixture refer to real units.
The endpoints expose counts and gates only, never source records or outcomes.
"""
from __future__ import annotations

from datetime import datetime, timezone

from .synthetic_institutional_lineage import (
    InstitutionalVersion, InstitutionalLink, StageInstitutionBinding,
    audit_institutional_lineage,
)
from .synthetic_registration_graph import (
    OfficialStageKey, StageVersion, TypedStageEdge,
)
from .synthetic_temporal_witness import KnowledgeInterval
from .procedural_index_contract import GateError, utc


def known(iso: str) -> KnowledgeInterval:
    return KnowledgeInterval(iso, iso)


def unit(code: str, legal: str, namespace: str, label: str,
         jurisdiction: str, competence: str, first: str,
         last: str | None, observed: str) -> InstitutionalVersion:
    return InstitutionalVersion(
        version_id="SYNTHETIC:"+code,
        legal_key_claim="SYNTHETIC:"+legal,
        institution_namespace="SYNTHETIC:"+namespace,
        label="SYNTHETIC:"+label,
        jurisdiction="SYNTHETIC:"+jurisdiction,
        competence="SYNTHETIC:"+competence,
        regime="SYNTHETIC:RULES_A", valid_from=first, valid_until=last,
        observed=known(observed), captured_at=observed,
        original_sha_claim="a"*64,
    )


def link(code: str, src: str, dst: str, relation: str, reorg: str,
         effective: str, document: str, observed: str,
         predecessors=1, successors=1) -> InstitutionalLink:
    return InstitutionalLink(
        link_id="SYNTHETIC:"+code,
        source_version="SYNTHETIC:"+src,
        target_version="SYNTHETIC:"+dst,
        relation=relation, reorganization_id="SYNTHETIC:"+reorg,
        effective_on=effective, document_on=document,
        observed=known(observed), captured_at=observed,
        original_sha_claim="b"*64,
        dual_official_keys_documented=(relation!="DOCUMENTARY_REFERENCE"),
        expected_predecessors=predecessors, expected_successors=successors,
    )


def fixture():
    old = unit("UNIT_A_OLD","LEGAL_A","BODY_A","SECRETARIADO","ZONE_A",
               "LAW","2017-01-01","2020-12-31","2026-01-02T00:00:00Z")
    renamed = unit("UNIT_A_NEW","LEGAL_A","BODY_A","OFICINA_COMUN","ZONE_A",
                   "LAW","2021-01-01","2022-12-31","2026-01-03T00:00:00Z")
    coincident = unit("UNIT_B","LEGAL_B","BODY_B","OFICINA_COMUN","ZONE_B",
                      "ECONOMY","2018-01-01",None,"2026-01-03T00:00:00Z")
    merging = unit("UNIT_D","LEGAL_D","BODY_D","SECCION_ALFA","ZONE_A",
                   "MEDIA","2018-01-01","2022-12-31","2026-01-04T00:00:00Z")
    successor = unit("UNIT_C","LEGAL_C","BODY_C","ENTIDAD_CONJUNTA","ZONE_A",
                     "LAW","2023-01-01",None,"2026-01-04T00:00:00Z")
    rename_link = link("RENAMED","UNIT_A_OLD","UNIT_A_NEW",
                       "LEGAL_RENAME_SAME_KEY","RENAME_A",
                       "2021-01-01","2021-01-01","2026-03-02T00:00:00Z")
    merger_a = link("MERGER_A","UNIT_A_NEW","UNIT_C",
                    "MERGER_PREDECESSOR","MERGER_2_TO_1",
                    "2023-01-01","2023-01-01","2026-07-02T00:00:00Z",2,1)
    merger_d = link("MERGER_D","UNIT_D","UNIT_C",
                    "MERGER_PREDECESSOR","MERGER_2_TO_1",
                    "2023-01-01","2023-01-01","2026-07-02T00:00:00Z",2,1)
    # The label "OFICINA_COMUN" appears in A and B. This document link
    # remains NON-LEGAL and cannot invent a shared juridical/legal identity.
    ref = link("REFERENCE_B","UNIT_A_NEW","UNIT_B",
               "DOCUMENTARY_REFERENCE","REFERENCE_NONLEGAL",
               "2021-01-01","2021-01-01","2026-03-02T00:00:00Z")
    reg = OfficialStageKey("SYNTHETIC:BODY_A","SYNTHETIC:RULES_A",
                           "SYNTHETIC:PETITION","REGISTRATION","SYNTHETIC:ENTRY_1")
    file = OfficialStageKey("SYNTHETIC:BODY_A","SYNTHETIC:RULES_A",
                            "SYNTHETIC:PETITION","FILE","SYNTHETIC:FILE_1")
    seen = known("2026-01-06T00:00:00Z")
    stages = tuple(StageVersion(
        key=k, revision="SYNTHETIC:V1", event_on="2020-03-01",
        document_on="2020-03-02", publisher_edition_at=None,
        observed=seen, captured_at="2026-01-06T00:00:00Z",
        original_sha_claim="c"*64,
    ) for k in (reg,file))
    stage_edges = (TypedStageEdge(
        edge_id="SYNTHETIC:EDGE_A", origin=reg, destination=file,
        relation="REGISTER_TO_FILE", document_on="2020-03-03",
        publisher_edition_at=None, observed=seen,
        captured_at="2026-01-06T00:00:00Z",
        original_sha_claim="d"*64,
    ),)
    bindings = tuple(StageInstitutionBinding(
        stage=k, version_id=old.version_id, observed=seen,
        captured_at="2026-01-06T00:00:00Z",
        evidence_sha_claim="e"*64,
    ) for k in (reg,file))
    return ((old,renamed,coincident,merging,successor),
            (rename_link,merger_a,merger_d,ref),
            bindings, stages, stage_edges)


def report(*, as_of: str | None = None, cut_on: str = "2023-12-31") -> dict:
    """CURRENT is explicit rather than a silent fallback after invalid as_of."""
    snapshot_type = "CURRENT_SYNTHETIC_LAB" if as_of is None else "HISTORICAL_SYNTHETIC_LAB"
    when = (datetime.now(timezone.utc).isoformat(timespec="seconds")
            if as_of is None else as_of)
    utc(when)
    units, links, bindings, stages, edges = fixture()
    result = audit_institutional_lineage(
        versions=units, links=links, bindings=bindings, stages=stages,
        stage_edges=edges, cut_on=cut_on, as_of=when,
        legal_calendar_zone="Europe/Madrid",
    )
    return {**result, "snapshot_mode":snapshot_type,
            "fixture_only":True, "real_institution_names_included":False,
            "official_source_ingestion":False}
