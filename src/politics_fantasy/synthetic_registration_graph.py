"""Bitemporal registration-first N:M stage graph — strictly SYNTHETIC.

Every vertex, revision and *edge* has its own observation interval and capture.
Publisher/editorial dates do not establish a historical as-of. A claimed
SHA or typed cross-institution relation is never an authenticated official
original, first_public_at, rights grant, population denominator, or outcome.

No network, user data, case identifiers, real source ingestion or ratings.
All summaries are synthetic counts that may be inspected by future contracts.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable
import re

from .procedural_index_contract import GateError, day, utc
from .synthetic_temporal_witness import KnowledgeInterval

SYNTHETIC_ID = re.compile(r"SYNTHETIC:[A-Z0-9_:-]{1,100}\Z")
SHA = re.compile(r"[0-9a-f]{64}\Z")
STAGES = ("REGISTRATION", "FILE", "ACTION", "DECISION", "PUBLICATION")
EDGES = {
    "REGISTER_TO_FILE": ("REGISTRATION", "FILE"),
    "FILE_TO_ACTION": ("FILE", "ACTION"),
    "ACTION_TO_DECISION": ("ACTION", "DECISION"),
    "DECISION_TO_PUBLICATION": ("DECISION", "PUBLICATION"),
}
MAX_RECORDS = 600
MAX_EDGES = 2400


def _id(value: str) -> bool:
    return isinstance(value, str) and bool(SYNTHETIC_ID.fullmatch(value))


@dataclass(frozen=True)
class OfficialStageKey:
    institution: str
    regime: str
    family: str
    stage: str
    local_id: str

    def __post_init__(self) -> None:
        if not all(_id(x) for x in (self.institution, self.regime,
                                   self.family, self.local_id)):
            raise GateError("SYNTHETIC_OFFICIAL_STAGE_KEYS_ONLY")
        if self.stage not in STAGES:
            raise GateError("INVALID_OFFICIAL_STAGE_ROLE")

    def frame(self) -> tuple[str, str, str]:
        return self.institution, self.regime, self.family


def _knowledge_safe_by(
    *, observed: KnowledgeInterval, captured_at: str | None,
) -> datetime | None:
    if not isinstance(observed, KnowledgeInterval):
        raise GateError("INVALID_KNOWLEDGE_INTERVAL")
    if captured_at is None or observed.upper() is None:
        return None
    captured = utc(captured_at)
    if (observed.observed_not_before is not None
            and captured < utc(observed.observed_not_before)):
        raise GateError("CAPTURE_BEFORE_FIRST_OBSERVATION_LOWER_BOUND")
    return max(observed.upper(), captured)


@dataclass(frozen=True)
class StageVersion:
    key: OfficialStageKey
    revision: str
    event_on: str
    document_on: str
    publisher_edition_at: str | None
    observed: KnowledgeInterval
    captured_at: str | None
    original_sha_claim: str
    original_authenticated: bool = False
    first_public_at: None = None

    def __post_init__(self) -> None:
        if (not isinstance(self.key, OfficialStageKey)
                or not _id(self.revision) or not isinstance(self.original_sha_claim,str)
                or not SHA.fullmatch(self.original_sha_claim)
                or self.original_authenticated is not False
                or self.first_public_at is not None):
            raise GateError("SYNTHETIC_STAGE_VERSION_ONLY")
        if day(self.event_on)>day(self.document_on):
            raise GateError("DOCUMENT_PRECEDES_STAGE_EVENT")
        if self.publisher_edition_at is not None:
            utc(self.publisher_edition_at)
        safe = _knowledge_safe_by(observed=self.observed,
                                  captured_at=self.captured_at)
        if safe is not None and day(self.document_on)>safe.date():
            raise GateError("DOCUMENT_FUTURE_TO_CAPTURE")

    def safe_by(self) -> datetime | None:
        return _knowledge_safe_by(observed=self.observed,
                                  captured_at=self.captured_at)


@dataclass(frozen=True)
class TypedStageEdge:
    edge_id: str
    origin: OfficialStageKey
    destination: OfficialStageKey
    relation: str
    document_on: str
    publisher_edition_at: str | None
    observed: KnowledgeInterval
    captured_at: str | None
    original_sha_claim: str
    independently_authenticated: bool = False
    first_public_at: None = None

    def __post_init__(self) -> None:
        if (not _id(self.edge_id)
                or not isinstance(self.origin, OfficialStageKey)
                or not isinstance(self.destination, OfficialStageKey)
                or not isinstance(self.original_sha_claim,str)
                or not SHA.fullmatch(self.original_sha_claim)
                or self.independently_authenticated is not False
                or self.first_public_at is not None):
            raise GateError("SYNTHETIC_STAGE_EDGE_ONLY")
        if self.relation == "EXPLICIT_TRANSFER_WITH_DUAL_OFFICIAL_IDS":
            if (self.origin.stage!="FILE" or self.destination.stage!="FILE"
                    or self.origin.institution==self.destination.institution):
                raise GateError("TRANSFER_REQUIRES_DIFFERENT_INSTITUTION_FILE_IDS")
        elif self.relation in EDGES:
            if (self.origin.stage,self.destination.stage)!=EDGES[self.relation]:
                raise GateError("INVALID_STAGE_EDGE_ROLES")
            if self.origin.frame()!=self.destination.frame():
                raise GateError("SPURIOUS_CROSS_FRAME_JOIN")
        else:
            raise GateError("FUZZY_OR_UNDEFINED_LINK_NOT_ALLOWED")
        day(self.document_on)
        if self.publisher_edition_at is not None:
            utc(self.publisher_edition_at)
        safe = _knowledge_safe_by(observed=self.observed,
                                  captured_at=self.captured_at)
        if safe is not None and day(self.document_on)>safe.date():
            raise GateError("EDGE_DOCUMENT_FUTURE_TO_CAPTURE")

    def safe_by(self) -> datetime | None:
        return _knowledge_safe_by(observed=self.observed,
                                  captured_at=self.captured_at)


def audit_graph(
    *, records: tuple[StageVersion,...],
    edges: tuple[TypedStageEdge,...],
    cut_on: str, as_of: str,
) -> dict:
    """Non-additive, ID-redacted, temporally conservative synthetic inventory.

    Stage role counts are *visible source-local documentary vertices*, NOT an
    intake registry, decision population or independent denominator. An edge
    can become visible only when the edge witness AND both exact ID endpoints
    were known; future links do not rewrite old snapshots.
    """
    c = day(cut_on)
    a = utc(as_of)
    if c>a.date():
        raise GateError("LEGAL_EVENT_CUT_AFTER_KNOWLEDGE")
    # Event-time cut_on covers an entire civil day. A same-day observation,
    # even one second after midnight, is not a completed-day risk horizon.
    # This is distinct from whether individual documentary nodes were seen.
    if c==a.date():
        raise GateError("LEGAL_EVENT_DAY_NOT_COMPLETED_AT_KNOWLEDGE")
    if (type(records) is not tuple or type(edges) is not tuple
            or len(records)>MAX_RECORDS or len(edges)>MAX_EDGES
            or any(not isinstance(r,StageVersion) for r in records)
            or any(not isinstance(e,TypedStageEdge) for e in edges)):
        raise GateError("BAD_SYNTHETIC_GRAPH_BUDGET_OR_TYPES")
    base = {
        "schema": "pfl.synthetic_registration_graph.v1",
        "synthetic_only": True, "scientific_cycles": 0,
        "real_decisions_observed": None, "real_negative_outcomes": None,
        "independent_all_received_denominator": None,
        "actual_pending_at_cut": None, "real_right_censoring": None,
        "registered_at_risk_population_certified": False,
        "originals_authenticated": False, "source_rights_adjudicated": False,
        "historical_first_public_at": None, "causal_feedback_identified": False,
        "official_cross_institution_links_authenticated": False,
        "source_counts_additive": False, "missing_link_is_not_rejection": True,
    }
    no_data = {
        "visible_stages": None, "visible_stage_total": None,
        "visible_claimed_edges": None, "claimed_transfer_edges": None,
        "multifile_registrations": None, "multi_entry_files": None,
        "unlinked_visible_registrations": None, "orphan_claims_at_cut": None,
        "revision_keys": None,
    }
    # First establish which revisions were known. Cutting on event date here
    # would discard a newly known correction moving an event out of the legal
    # window, leaving a superseded old revision falsely visible at that cut.
    known = [r for r in records
             if r.safe_by() is not None and r.safe_by() <= a]
    if not known:
        return {**base,**no_data,"status":"NO_SYNTHETIC_GRAPH_KNOWN_AT_CUT"}
    by_revision: dict[tuple[OfficialStageKey,str],StageVersion]={}
    for r in known:
        key=(r.key,r.revision)
        if key in by_revision and by_revision[key]!=r:
            return {**base,**no_data,
                    "status":"VISIBLE_CONFLICTING_STAGE_REVISION_QUARANTINED"}
        by_revision[key]=r
    # A newer revision supersedes its own key only after its independent
    # local observation. Its nominal publisher date cannot cause backfill.
    by_key: dict[OfficialStageKey,StageVersion]={}
    for r in by_revision.values():
        old=by_key.get(r.key)
        if (old is None or
                (r.safe_by(),r.revision)>(old.safe_by(),old.revision)):
            by_key[r.key]=r
    # Only the effective version at as_of determines event-time membership.
    # A known revision can remove an earlier documentary vertex from cut_on,
    # but an unseen future revision cannot rewrite an earlier as_of snapshot.
    by_key={k:r for k,r in by_key.items() if day(r.event_on)<=c}
    # Resolve conflicts in *known* claims by edge identity before the legal
    # document cut. Otherwise a newer, known incompatible claim dated outside
    # cut_on vanishes before conflict detection and its obsolete link survives.
    known_edges=[e for e in edges if e.safe_by() is not None
                 and e.safe_by()<=a]
    seen_ids: dict[str, TypedStageEdge]={}
    duplicate_document=set()
    for e in known_edges:
        if e.edge_id in seen_ids and seen_ids[e.edge_id]!=e:
            return {**base,**no_data,
                    "status":"VISIBLE_CONFLICTING_EDGE_CLAIM_QUARANTINED"}
        seen_ids[e.edge_id]=e
    edge_candidates=[e for e in seen_ids.values()
                     if day(e.document_on)<=c]
    by_document: set[tuple[OfficialStageKey,OfficialStageKey,str,str]]=set()
    for e in edge_candidates:
        d=(e.origin,e.destination,e.relation,e.original_sha_claim)
        if d in by_document:
            duplicate_document.add(d)
        by_document.add(d)
    if duplicate_document:
        return {**base,**no_data,"status":"DUPLICATE_EDGE_DOCUMENT_QUARANTINED"}
    complete=[e for e in edge_candidates
              if e.origin in by_key and e.destination in by_key]
    orphans=len(edge_candidates)-len(complete)
    links={(e.origin,e.destination,e.relation) for e in complete}
    registration=[k for k in by_key if k.stage=="REGISTRATION"]
    files=[k for k in by_key if k.stage=="FILE"]
    reg_edges={(x,y) for x,y,role in links if role=="REGISTER_TO_FILE"}
    per_reg={k:set() for k in registration}
    per_file={k:set() for k in files}
    for x,y in reg_edges:
        per_reg[x].add(y)
        per_file[y].add(x)
    stage_counts={stage:sum(k.stage==stage for k in by_key) for stage in STAGES}
    return {
        **base, "status":"SYNTHETIC_DOCUMENTARY_GRAPH_ONLY",
        "visible_stages":stage_counts,
        "visible_stage_total":len(by_key),
        "visible_claimed_edges":len(links),
        "claimed_transfer_edges":sum(role=="EXPLICIT_TRANSFER_WITH_DUAL_OFFICIAL_IDS"
                                     for x,y,role in links),
        "multifile_registrations":sum(len(v)>1 for v in per_reg.values()),
        "multi_entry_files":sum(len(v)>1 for v in per_file.values()),
        "unlinked_visible_registrations":sum(not v for v in per_reg.values()),
        "orphan_claims_at_cut":orphans,
        "revision_keys":len(by_revision),
        "all_links_claimed_not_authenticated":True,
        "units_kept_distinct_by_stage_and_institution":True,
        "event_cut_not_equivalent_to_historical_asof":True,
    }
