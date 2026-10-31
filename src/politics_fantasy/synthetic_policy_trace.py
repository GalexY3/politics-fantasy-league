"""Synthetic, bitemporal documentary policy traces across heterogeneous stages.

This is an offline instrumentation layer, NOT an ingest pipeline, claim of a
Spanish policy trajectory, forecast, causal estimator, or authorization to
score real people. An explicit documentary reference is not a causal edge.
All identifiers must be SYNTHETIC and no source rights are conferred here.
"""
from __future__ import annotations

from dataclasses import dataclass

from .procedural_index_contract import (
    GateError, SHA, day, utc, legal_civil_date, legal_day_completed,
)
from .synthetic_registration_graph import SYNTHETIC_ID

STAGES = (
    "POLITICAL_COMMITMENT",
    "PROCEDURAL_INITIATIVE",
    "FORMAL_DECISION",
    "NORMATIVE_INSTRUMENT",
    "BUDGET_ITEM",
    "IMPLEMENTATION_ACT",
    "OBSERVED_INDICATOR",
)
EDGE_KINDS = {
    "COMMITMENT_CITED_IN_INITIATIVE": STAGES[:2],
    "INITIATIVE_REFERENCED_IN_DECISION": STAGES[1:3],
    "DECISION_REFERENCED_IN_NORM": STAGES[2:4],
    "NORM_REFERENCED_IN_BUDGET": STAGES[3:5],
    "BUDGET_REFERENCED_IN_ACT": STAGES[4:6],
    "ACT_ASSOCIATED_WITH_INDICATOR": STAGES[5:7],
}
MAX_NODES = 250
MAX_LINKS = 750


def _synthetic(value: object) -> bool:
    return type(value) is str and SYNTHETIC_ID.fullmatch(value) is not None


def _captured_not_before_document(document_on: str, captured_at: str,
                                  legal_calendar_zone: str) -> None:
    # A document day cannot postdate the local civil day of its own capture.
    if legal_civil_date(captured_at, legal_calendar_zone) < day(document_on):
        raise GateError("POLICY_TRACE_CAPTURE_BEFORE_DOCUMENT_DAY")


@dataclass(frozen=True)
class FictionalPolicyNode:
    node_id: str
    kind: str
    issuer_namespace: str
    source_document_id: str
    source_sha256_claim: str
    event_on: str
    document_on: str
    captured_at: str
    legal_calendar_zone: str
    original_authenticated: bool = False
    first_public_at: None = None
    rights_verified: bool = False
    personal_identifiers: None = None

    def __post_init__(self) -> None:
        if not all(_synthetic(v) for v in (
            self.node_id, self.issuer_namespace, self.source_document_id,
        )) or type(self.kind) is not str or self.kind not in STAGES:
            raise GateError("POLICY_TRACE_SYNTHETIC_NODES_ONLY")
        if (type(self.source_sha256_claim) is not str
                or SHA.fullmatch(self.source_sha256_claim) is None):
            raise GateError("POLICY_TRACE_SHA256_CLAIM_REQUIRED")
        if (self.original_authenticated is not False
                or self.first_public_at is not None
                or self.rights_verified is not False
                or self.personal_identifiers is not None):
            raise GateError("POLICY_TRACE_REAL_EVIDENCE_FORBIDDEN")
        if day(self.event_on) > day(self.document_on):
            raise GateError("POLICY_TRACE_DOCUMENT_BEFORE_EVENT")
        utc(self.captured_at)
        _captured_not_before_document(
            self.document_on, self.captured_at, self.legal_calendar_zone,
        )


@dataclass(frozen=True)
class FictionalPolicyLink:
    link_id: str
    origin_id: str
    destination_id: str
    kind: str
    # The synthetic destination document asserts an EXACT reference to the
    # synthetic origin document. IDs are claims, not proof of real links.
    origin_document_reference: str
    asserting_document_id: str
    origin_sha256_claim: str
    asserting_sha256_claim: str
    document_on: str
    captured_at: str
    legal_calendar_zone: str
    independently_authenticated: bool = False
    first_public_at: None = None
    rights_verified: bool = False

    def __post_init__(self) -> None:
        if (not all(_synthetic(v) for v in (
                self.link_id, self.origin_id, self.destination_id,
                self.origin_document_reference, self.asserting_document_id))
                or type(self.kind) is not str or self.kind not in EDGE_KINDS):
            raise GateError("POLICY_TRACE_SYNTHETIC_LINKS_ONLY")
        if (type(self.origin_sha256_claim) is not str
                or SHA.fullmatch(self.origin_sha256_claim) is None
                or type(self.asserting_sha256_claim) is not str
                or SHA.fullmatch(self.asserting_sha256_claim) is None):
            raise GateError("POLICY_TRACE_LINK_SHA256_CLAIMS_REQUIRED")
        if (self.independently_authenticated is not False
                or self.first_public_at is not None
                or self.rights_verified is not False):
            raise GateError("POLICY_TRACE_REAL_LINK_AUTHENTICATION_FORBIDDEN")
        day(self.document_on)
        utc(self.captured_at)
        _captured_not_before_document(
            self.document_on, self.captured_at, self.legal_calendar_zone,
        )


def audit_synthetic_policy_trace(
    *, nodes: tuple[FictionalPolicyNode, ...],
    links: tuple[FictionalPolicyLink, ...],
    cut_on: str, as_of: str, legal_calendar_zone: str,
) -> dict:
    """Audit documentary paths known by a cut, never infer causation.

    Visibility is filtered BEFORE checking duplicate IDs or link integrity,
    so records discovered in the future cannot perturb historical answers.
    Unknown or missing links never imply a negative political event.
    """
    if (type(nodes) is not tuple or type(links) is not tuple
            or len(nodes) > MAX_NODES or len(links) > MAX_LINKS
            or any(type(n) is not FictionalPolicyNode for n in nodes)
            or any(type(e) is not FictionalPolicyLink for e in links)):
        raise GateError("POLICY_TRACE_BOUNDED_SYNTHETIC_TUPLES_REQUIRED")
    if not legal_day_completed(
        cut_on=cut_on, as_of=as_of, legal_calendar_zone=legal_calendar_zone,
    ):
        raise GateError("POLICY_TRACE_CIVIL_DAY_NOT_COMPLETED")
    at = utc(as_of)
    cut = day(cut_on)
    if any(n.legal_calendar_zone != legal_calendar_zone for n in nodes):
        raise GateError("POLICY_TRACE_MIXED_NODE_CALENDAR")
    if any(e.legal_calendar_zone != legal_calendar_zone for e in links):
        raise GateError("POLICY_TRACE_MIXED_LINK_CALENDAR")

    eligible_nodes = tuple(
        n for n in nodes if (utc(n.captured_at) <= at
                             and day(n.document_on) <= cut
                             and day(n.event_on) <= cut)
    )
    eligible_links = tuple(
        e for e in links if (utc(e.captured_at) <= at
                             and day(e.document_on) <= cut)
    )
    nids = [n.node_id for n in eligible_nodes]
    lids = [e.link_id for e in eligible_links]
    if len(nids) != len(set(nids)) or len(lids) != len(set(lids)):
        raise GateError("POLICY_TRACE_CONFLICTING_KNOWN_IDENTITIES")
    by_id = {n.node_id: n for n in eligible_nodes}
    counts = {kind: 0 for kind in STAGES}
    for n in eligible_nodes:
        counts[n.kind] += 1

    adjacency: dict[str, set[str]] = {n.node_id: set() for n in eligible_nodes}
    complete_links = 0
    dangling_links = 0
    for e in eligible_links:
        a, b = by_id.get(e.origin_id), by_id.get(e.destination_id)
        if a is None or b is None:
            # A missing endpoint is an unknown relation, not an inferred one.
            dangling_links += 1
            continue
        if (EDGE_KINDS[e.kind] != (a.kind, b.kind)
                or e.origin_document_reference != a.source_document_id
                or e.asserting_document_id != b.source_document_id
                or e.origin_sha256_claim != a.source_sha256_claim
                or e.asserting_sha256_claim != b.source_sha256_claim
                or day(a.event_on) > day(b.event_on)
                or day(e.document_on) < day(b.document_on)):
            raise GateError("POLICY_TRACE_UNSUPPORTED_EXPLICIT_REFERENCE")
        adjacency[a.node_id].add(b.node_id)
        complete_links += 1

    # Finite, ordered stage traversal; no automatic join on name, date,
    # party, issuer, or thematic similarity. Cardinality can be N:M.
    reachable = {
        n.node_id for n in eligible_nodes if n.kind == STAGES[0]
    }
    for destination_kind in STAGES[1:]:
        reachable = {
            target for src in reachable for target in adjacency[src]
            if by_id[target].kind == destination_kind
        }
    has_full_chain = bool(reachable)
    return {
        "schema": "pfl.synthetic_policy_document_trace.v1",
        "evidence_class": "SYNTHETIC_LAB_ONLY",
        "cut_on": cut_on,
        "as_of": as_of,
        "legal_calendar_zone": legal_calendar_zone,
        "visible_node_counts_by_kind": counts,
        "complete_explicit_documentary_links": complete_links,
        "unknown_or_unresolved_link_endpoints": dangling_links,
        "full_seven_stage_documentary_path_in_fixture": has_full_chain,
        "missing_stages_in_fixture_only": [
            kind for kind in STAGES if counts[kind] == 0
        ],
        "documentary_reference_is_causal_effect": False,
        "registered_population_independently_attested": False,
        "originals_authenticated": False,
        "source_rights_verified": False,
        "first_public_at": None,
        "real_policy_outcomes_or_effects": None,
        "person_scores": None,
        "scientific_AB_cycles": 0,
    }
