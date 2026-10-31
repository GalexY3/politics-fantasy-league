"""R21 C15: bitemporal institutional identity & registration graph, SYNTHETIC.

Do not equate nominal labels, documentary references, legal persons, offices,
competence or functional systems. All keys are fictional and all alleged
original hashes and dual-ID bridges remain UNAUTHENTICATED. The read-only
laboratory only demonstrates safety contracts; it acquires no official cases.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re

from .procedural_index_contract import GateError, day, legal_day_completed, utc, LEGAL_CIVIL_ZONES
from .synthetic_temporal_witness import KnowledgeInterval
from .synthetic_registration_graph import (
    OfficialStageKey, StageVersion, TypedStageEdge, audit_graph,
)

SYN = re.compile(r"SYNTHETIC:[A-Z0-9_:-]{1,100}\Z")
SHA = re.compile(r"[a-f0-9]{64}\Z")
LINK_KINDS = frozenset({
    "LEGAL_RENAME_SAME_KEY", "MERGER_PREDECESSOR", "SPLIT_SUCCESSOR",
    "COMPETENCE_TRANSFER", "JURISDICTION_TRANSFER", "DOCUMENTARY_REFERENCE",
})
SUCCESSION_KINDS = frozenset({"MERGER_PREDECESSOR", "SPLIT_SUCCESSOR"})
MAX_UNITS, MAX_LINKS, MAX_BINDINGS = 200, 600, 900


def _syn(x: object) -> bool:
    return type(x) is str and SYN.fullmatch(x) is not None


def _knowledge(observed: KnowledgeInterval, captured_at: str | None) -> datetime | None:
    if not isinstance(observed, KnowledgeInterval):
        raise GateError("LINEAGE_KNOWLEDGE_INTERVAL_REQUIRED")
    upper = observed.upper()
    if captured_at is None or upper is None:
        return None
    captured = utc(captured_at)
    if (observed.observed_not_before is not None
            and captured < utc(observed.observed_not_before)):
        raise GateError("LINEAGE_CAPTURE_PRECEDES_OBSERVATION")
    return max(upper, captured)


@dataclass(frozen=True)
class InstitutionalVersion:
    version_id: str
    legal_key_claim: str
    institution_namespace: str
    label: str
    jurisdiction: str
    competence: str
    regime: str
    valid_from: str
    valid_until: str | None
    observed: KnowledgeInterval
    captured_at: str | None
    original_sha_claim: str
    legal_original_authenticated: bool = False
    first_public_at: None = None

    def __post_init__(self):
        if (not all(_syn(x) for x in (
                self.version_id, self.legal_key_claim, self.institution_namespace,
                self.label, self.jurisdiction, self.competence, self.regime))
                or type(self.original_sha_claim) is not str
                or SHA.fullmatch(self.original_sha_claim) is None
                or self.legal_original_authenticated is not False
                or self.first_public_at is not None):
            raise GateError("SYNTHETIC_LEGAL_IDENTITY_ONLY")
        start = day(self.valid_from)
        if self.valid_until is not None and day(self.valid_until) < start:
            raise GateError("INVERTED_INSTITUTIONAL_VALIDITY")
        safe = self.safe_by()
        if safe is not None and start > safe.date():
            # A prospective rule may become valid after its document is
            # observed, but this lab disallows that without a separate
            # prospective-effective-time contract.
            raise GateError("FUTURE_LEGAL_UNIT_AT_CAPTURE")

    def safe_by(self) -> datetime | None:
        return _knowledge(self.observed, self.captured_at)


@dataclass(frozen=True)
class InstitutionalLink:
    link_id: str
    source_version: str
    target_version: str
    relation: str
    reorganization_id: str
    effective_on: str
    document_on: str
    observed: KnowledgeInterval
    captured_at: str | None
    original_sha_claim: str
    dual_official_keys_documented: bool = False
    expected_predecessors: int = 1
    expected_successors: int = 1
    original_authenticated: bool = False
    first_public_at: None = None

    def __post_init__(self):
        if (not all(_syn(x) for x in (
                self.link_id, self.source_version, self.target_version,
                self.reorganization_id))
                or self.relation not in LINK_KINDS
                or self.source_version == self.target_version
                or type(self.original_sha_claim) is not str
                or SHA.fullmatch(self.original_sha_claim) is None
                or type(self.expected_predecessors) is not int
                or type(self.expected_successors) is not int
                or not (1 <= self.expected_predecessors <= MAX_UNITS)
                or not (1 <= self.expected_successors <= MAX_UNITS)
                or type(self.dual_official_keys_documented) is not bool
                or self.original_authenticated is not False
                or self.first_public_at is not None):
            raise GateError("SYNTHETIC_INSTITUTIONAL_LINK_ONLY")
        if self.relation == "MERGER_PREDECESSOR" and (
                self.expected_predecessors < 2 or self.expected_successors != 1):
            raise GateError("MERGER_CARDINALITY_CONTRACT_REQUIRED")
        if self.relation == "SPLIT_SUCCESSOR" and (
                self.expected_successors < 2 or self.expected_predecessors != 1):
            raise GateError("SPLIT_CARDINALITY_CONTRACT_REQUIRED")
        if self.relation not in SUCCESSION_KINDS and (
                self.expected_predecessors != 1 or self.expected_successors != 1):
            raise GateError("ONE_TO_ONE_LINK_CARDINALITY_REQUIRED")
        day(self.effective_on)
        day(self.document_on)
        safe = self.safe_by()
        if safe is not None and day(self.document_on) > safe.date():
            raise GateError("LINEAGE_DOCUMENT_FUTURE_TO_CAPTURE")

    def safe_by(self) -> datetime | None:
        return _knowledge(self.observed, self.captured_at)


@dataclass(frozen=True)
class StageInstitutionBinding:
    stage: OfficialStageKey
    version_id: str
    observed: KnowledgeInterval
    captured_at: str | None
    evidence_sha_claim: str
    independently_authenticated: bool = False

    def __post_init__(self):
        if (not isinstance(self.stage, OfficialStageKey)
                or not _syn(self.version_id)
                or type(self.evidence_sha_claim) is not str
                or SHA.fullmatch(self.evidence_sha_claim) is None
                or self.independently_authenticated is not False):
            raise GateError("SYNTHETIC_STAGE_BINDING_ONLY")
        self.safe_by()

    def safe_by(self) -> datetime | None:
        return _knowledge(self.observed, self.captured_at)


def audit_institutional_lineage(
    *, versions: tuple[InstitutionalVersion, ...],
    links: tuple[InstitutionalLink, ...],
    bindings: tuple[StageInstitutionBinding, ...],
    stages: tuple[StageVersion, ...],
    stage_edges: tuple[TypedStageEdge, ...],
    cut_on: str, as_of: str, legal_calendar_zone: str,
) -> dict:
    """Replay as-known documentary claims; never deduce legal identity from names.

    Strictly separates (1) recorded versions, (2) claimed legal continuity,
    (3) competence/territorial transfers, (4) functional-system hypotheses.
    All public summary fields are redacted aggregates and explicit null gates.
    """
    if (type(legal_calendar_zone) is not str
            or legal_calendar_zone not in LEGAL_CIVIL_ZONES):
        raise GateError("LINEAGE_EXPLICIT_JURISDICTION_ZONE_REQUIRED")
    cut = day(cut_on)
    knowledge_at = utc(as_of)
    if not legal_day_completed(
            cut_on=cut_on, as_of=as_of,
            legal_calendar_zone=legal_calendar_zone):
        raise GateError("LINEAGE_LEGAL_DAY_INCOMPLETE")
    if (type(versions) is not tuple or type(links) is not tuple
            or type(bindings) is not tuple or type(stages) is not tuple
            or type(stage_edges) is not tuple
            or len(versions) > MAX_UNITS or len(links) > MAX_LINKS
            or len(bindings) > MAX_BINDINGS
            or any(type(v) is not InstitutionalVersion for v in versions)
            or any(type(l) is not InstitutionalLink for l in links)
            or any(type(b) is not StageInstitutionBinding for b in bindings)
            or any(type(s) is not StageVersion for s in stages)
            or any(type(e) is not TypedStageEdge for e in stage_edges)):
        raise GateError("SYNTHETIC_INSTITUTIONAL_INVENTORY_REQUIRED")
    known = [v for v in versions if v.safe_by() is not None
             and v.safe_by() <= knowledge_at]
    visible_versions: dict[str, InstitutionalVersion] = {}
    for v in known:
        previous = visible_versions.get(v.version_id)
        if previous is not None and previous != v:
            return _quarantined(as_of, cut_on, legal_calendar_zone,
                                "CONFLICTING_KNOWN_INSTITUTIONAL_VERSION")
        visible_versions[v.version_id] = v
    # A legal entity can have successive versions, but concurrent competing
    # descriptions of the same legal ID must be quarantined, not silently
    # resolve by label, filename, order or the last editorial timestamp.
    active = [v for v in visible_versions.values()
              if day(v.valid_from) <= cut and (
                  v.valid_until is None or cut <= day(v.valid_until))]
    by_legal_key: dict[str, InstitutionalVersion] = {}
    for v in active:
        prev = by_legal_key.get(v.legal_key_claim)
        if prev is not None and prev != v:
            return _quarantined(as_of, cut_on, legal_calendar_zone,
                                "COMPETING_ACTIVE_LEGAL_KEY_DESCRIPTIONS")
        by_legal_key[v.legal_key_claim] = v
    known_links = [l for l in links if l.safe_by() is not None
                   and l.safe_by() <= knowledge_at]
    by_link_id: dict[str, InstitutionalLink] = {}
    for l in known_links:
        previous = by_link_id.get(l.link_id)
        if previous is not None and previous != l:
            return _quarantined(as_of, cut_on, legal_calendar_zone,
                                "CONFLICTING_KNOWN_LINEAGE_LINK")
        by_link_id[l.link_id] = l
    eligible = [l for l in by_link_id.values()
                if day(l.effective_on) <= cut and day(l.document_on) <= cut]
    if any(l.source_version not in visible_versions
           or l.target_version not in visible_versions for l in eligible):
        return _quarantined(as_of, cut_on, legal_calendar_zone,
                            "LINEAGE_LINK_ENDPOINT_UNKNOWN_AT_ASOF")
    groups: dict[str, list[InstitutionalLink]] = {}
    for l in eligible:
        groups.setdefault(l.reorganization_id, []).append(l)
    complete_links: list[InstitutionalLink] = []
    incomplete_reorganization_groups = 0
    for group in groups.values():
        expected = {(l.relation, l.expected_predecessors,
                     l.expected_successors) for l in group}
        if len(expected) != 1:
            return _quarantined(as_of, cut_on, legal_calendar_zone,
                                "INCONSISTENT_REORGANIZATION_SIGNATURE")
        relation, n_pre, n_post = next(iter(expected))
        pre = {l.source_version for l in group}
        post = {l.target_version for l in group}
        if (len(pre) > n_pre or len(post) > n_post
                or len({(l.source_version, l.target_version) for l in group})
                != len(group)):
            return _quarantined(as_of, cut_on, legal_calendar_zone,
                                "DUPLICATE_OR_EXCESS_SUCCESSION_LINKS")
        if len(pre) != n_pre or len(post) != n_post:
            incomplete_reorganization_groups += 1
            continue
        for l in group:
            src, dest = visible_versions[l.source_version], visible_versions[l.target_version]
            if (day(src.valid_from) > day(l.effective_on)
                    or day(dest.valid_from) > day(l.effective_on)):
                return _quarantined(as_of, cut_on, legal_calendar_zone,
                                    "LINEAGE_EFFECT_BEFORE_ENTITY_EXISTS")
            if (l.relation == "LEGAL_RENAME_SAME_KEY"
                    and src.legal_key_claim != dest.legal_key_claim):
                return _quarantined(as_of, cut_on, legal_calendar_zone,
                                    "RENAME_CHANGED_LEGAL_KEY")
            if (l.relation in SUCCESSION_KINDS
                    and src.legal_key_claim == dest.legal_key_claim):
                return _quarantined(as_of, cut_on, legal_calendar_zone,
                                    "SUCCESSION_COLLAPSES_LEGAL_PERSON")
            if (l.relation != "DOCUMENTARY_REFERENCE"
                    and l.dual_official_keys_documented is not True):
                # A matching title is NOT a legal/competence lineage link.
                return _quarantined(as_of, cut_on, legal_calendar_zone,
                                    "NO_EXPLICIT_DUAL_OFFICIAL_KEY_EVIDENCE")
        complete_links.extend(group)
    legal_types = ("LEGAL_RENAME_SAME_KEY", "MERGER_PREDECESSOR",
                   "SPLIT_SUCCESSOR")
    counts = {kind: sum(l.relation == kind for l in complete_links)
              for kind in LINK_KINDS}
    # Bind stage vertices only through exact, separately witnessed identity
    # references, never through matching display name or retrospective alias.
    stage_binding: dict[OfficialStageKey, StageInstitutionBinding] = {}
    for b in bindings:
        if b.safe_by() is None or b.safe_by() > knowledge_at:
            continue
        v = visible_versions.get(b.version_id)
        if v is None or b.stage.institution != v.institution_namespace:
            return _quarantined(as_of, cut_on, legal_calendar_zone,
                                "STAGE_INSTITUTION_NAMESPACE_MISMATCH")
        previous = stage_binding.get(b.stage)
        if previous is not None and previous != b:
            return _quarantined(as_of, cut_on, legal_calendar_zone,
                                "MULTIPLE_UNATTESTED_STAGE_IDENTITY_BINDINGS")
        stage_binding[b.stage] = b
    # Resolve known stage revisions before validating their assignment to a
    # *legally effective* unit edition. A common institution namespace (or
    # name) is insufficient to assign a 2020 event to a 2021 legal version.
    effective_stages: dict[OfficialStageKey, StageVersion] = {}
    known_revisions: dict[tuple[OfficialStageKey, str], StageVersion] = {}
    for s in stages:
        if (s.key not in stage_binding or s.safe_by() is None
                or s.safe_by() > knowledge_at):
            continue
        claim_key = (s.key, s.revision)
        if claim_key in known_revisions and known_revisions[claim_key] != s:
            return _quarantined(as_of, cut_on, legal_calendar_zone,
                                "STAGE_REVISION_CONFLICT_AT_IDENTITY_JOIN")
        known_revisions[claim_key] = s
    for s in known_revisions.values():
        old = effective_stages.get(s.key)
        if old is None or (s.safe_by(), s.revision) > (old.safe_by(), old.revision):
            effective_stages[s.key] = s
    for key, s in effective_stages.items():
        if day(s.event_on) > cut:
            continue
        v = visible_versions[stage_binding[key].version_id]
        if (day(s.event_on) < day(v.valid_from)
                or (v.valid_until is not None and day(s.event_on) > day(v.valid_until))):
            return _quarantined(as_of, cut_on, legal_calendar_zone,
                                "STAGE_EVENT_OUTSIDE_INSTITUTIONAL_VALIDITY")
    selected_stages = tuple(s for s in stages if s.key in stage_binding)
    selected_edges = tuple(e for e in stage_edges
                           if e.origin in stage_binding and e.destination in stage_binding)
    graph = audit_graph(records=selected_stages, edges=selected_edges,
                        cut_on=cut_on, as_of=as_of,
                        legal_calendar_zone=legal_calendar_zone)
    return {
        **_base(as_of, cut_on, legal_calendar_zone),
        "status": "SYNTHETIC_LINEAGE_DOCUMENTARY_ONLY",
        "known_version_claims": len(visible_versions),
        "distinct_active_legal_key_claims": len(by_legal_key),
        "complete_explicit_lineage_links": len(complete_links),
        "link_classes": counts,
        "incomplete_reorganization_groups": incomplete_reorganization_groups,
        "documentary_reference_not_legal_continuity": counts["DOCUMENTARY_REFERENCE"],
        "legal_continuity_claimed_not_authenticated": sum(
            counts[k] for k in legal_types),
        "competence_and_jurisdiction_transfer_claims_not_causal": (
            counts["COMPETENCE_TRANSFER"] + counts["JURISDICTION_TRANSFER"]),
        "stage_graph": graph,
    }


def _base(as_of: str, cut_on: str, zone: str) -> dict:
    return {
        "schema": "pfl.synthetic_institutional_lineage.v1",
        "evidence_class": "SYNTHETIC_LAB_ONLY",
        "as_of": as_of, "cut_on": cut_on, "legal_calendar_zone": zone,
        "source_originals_authenticated": False,
        "all_received_denominator": None,
        "historical_first_public_at": None,
        "source_reuse_rights_verified": False,
        "real_pending": None, "real_censoring": None, "real_negative_outcomes": None,
        "legal_identity_authenticated": False,
        "functional_system_continuity_identified": False,
        "causal_feedback_or_reintroduction_identified": False,
        "scientific_AB_cycles": 0, "registered_at_risk_certified": False,
        "unknown_is_not_zero": True, "source_counts_additive": False,
    }


def _quarantined(as_of: str, cut_on: str, zone: str, reason: str) -> dict:
    # Deliberately do not disclose IDs, hashes, names or even the number of
    # competing future records in a quarantined diagnostic.
    return {**_base(as_of, cut_on, zone),
            "status": "SYNTHETIC_IDENTITY_CONFLICT_QUARANTINED",
            "quarantine_reason": reason,
            "known_version_claims": None,
            "distinct_active_legal_key_claims": None,
            "complete_explicit_lineage_links": None,
            "link_classes": None,
            "incomplete_reorganization_groups": None,
            "documentary_reference_not_legal_continuity": None,
            "legal_continuity_claimed_not_authenticated": None,
            "competence_and_jurisdiction_transfer_claims_not_causal": None,
            "stage_graph": None}
