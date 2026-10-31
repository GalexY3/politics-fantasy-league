"""Synthetic policy lifecycle: exact references, as-of, and non-causal status."""
from dataclasses import replace
from hashlib import sha256
import json

import pytest

from politics_fantasy.procedural_index_contract import GateError
from politics_fantasy.synthetic_policy_trace import (
    EDGE_KINDS, STAGES, FictionalPolicyNode, FictionalPolicyLink,
    audit_synthetic_policy_trace,
)


EARLY = "2026-02-10T10:00:00Z"
LATE = "2026-02-20T10:00:00Z"
REPORT = "2026-03-01T12:00:00Z"
ZONE = "Europe/Madrid"


def artificial_sha(i: int) -> str:
    return sha256(f"PURELY-FICTIONAL-DOCUMENT-{i}".encode()).hexdigest()


def fixture():
    nodes = tuple(
        FictionalPolicyNode(
            node_id=f"SYNTHETIC:N_{i}",
            kind=stage,
            issuer_namespace=f"SYNTHETIC:ISSUER_{i}",
            source_document_id=f"SYNTHETIC:DOC_{i}",
            source_sha256_claim=artificial_sha(i),
            event_on=f"2026-01-{i + 1:02d}",
            document_on=f"2026-01-{i + 1:02d}",
            captured_at=LATE if i == 6 else EARLY,
            legal_calendar_zone=ZONE,
        )
        for i, stage in enumerate(STAGES)
    )
    links = tuple(
        FictionalPolicyLink(
            link_id=f"SYNTHETIC:E_{i}",
            origin_id=nodes[i].node_id,
            destination_id=nodes[i+1].node_id,
            kind=kind,
            origin_document_reference=nodes[i].source_document_id,
            asserting_document_id=nodes[i+1].source_document_id,
            origin_sha256_claim=nodes[i].source_sha256_claim,
            asserting_sha256_claim=nodes[i+1].source_sha256_claim,
            document_on=nodes[i+1].document_on,
            captured_at=LATE if i == 5 else EARLY,
            legal_calendar_zone=ZONE,
        )
        for i, kind in enumerate(EDGE_KINDS)
    )
    return nodes, links


def audit(nodes=None, links=None, cut_on="2026-02-28", as_of=REPORT):
    n, e = fixture()
    return audit_synthetic_policy_trace(
        nodes=n if nodes is None else nodes,
        links=e if links is None else links,
        cut_on=cut_on, as_of=as_of, legal_calendar_zone=ZONE,
    )


def test_full_chain_is_documentary_not_causal():
    result = audit()
    assert result["complete_explicit_documentary_links"] == 6
    assert result["full_seven_stage_documentary_path_in_fixture"] is True
    assert result["missing_stages_in_fixture_only"] == []
    assert set(result["visible_node_counts_by_kind"]) == set(STAGES)
    assert all(v == 1 for v in result["visible_node_counts_by_kind"].values())
    assert result["documentary_reference_is_causal_effect"] is False
    assert result["source_rights_verified"] is False
    assert result["originals_authenticated"] is False
    assert result["first_public_at"] is None
    assert result["scientific_AB_cycles"] == 0
    text = json.dumps(result)
    assert "SYNTHETIC:N_" not in text
    assert "SYNTHETIC:DOC_" not in text
    assert result["person_scores"] is None
    assert result["real_policy_outcomes_or_effects"] is None


def test_future_capture_never_rewrites_historical_snapshot():
    old = audit(cut_on="2026-02-14", as_of="2026-02-15T12:00:00Z")
    latest = audit()
    assert old["full_seven_stage_documentary_path_in_fixture"] is False
    assert old["visible_node_counts_by_kind"]["OBSERVED_INDICATOR"] == 0
    assert old["complete_explicit_documentary_links"] == 5
    assert latest["full_seven_stage_documentary_path_in_fixture"] is True


def test_link_known_before_endpoint_is_unknown_not_absence():
    n, links = fixture()
    changed = (*links[:-1], replace(links[-1], captured_at=EARLY))
    old = audit(nodes=n, links=changed, cut_on="2026-02-14",
                as_of="2026-02-15T12:00:00Z")
    assert old["unknown_or_unresolved_link_endpoints"] == 1
    assert old["complete_explicit_documentary_links"] == 5
    assert not old["full_seven_stage_documentary_path_in_fixture"]


def test_temporal_future_duplicate_only_quarantines_when_known():
    n, e = fixture()
    future = replace(n[0], captured_at="2026-03-05T12:00:00Z")
    assert audit(nodes=(*n, future), links=e)["complete_explicit_documentary_links"] == 6
    with pytest.raises(GateError, match="CONFLICTING_KNOWN_IDENTITIES"):
        audit(nodes=(*n, future), links=e, cut_on="2026-03-08",
              as_of="2026-03-09T12:00:00Z")


def test_no_automatic_links_even_when_all_stages_exist():
    n, _ = fixture()
    result = audit(nodes=n, links=())
    assert result["full_seven_stage_documentary_path_in_fixture"] is False
    assert result["complete_explicit_documentary_links"] == 0
    assert result["missing_stages_in_fixture_only"] == []


def test_exact_document_reference_mismatch_fails_closed():
    n, e = fixture()
    forged = replace(e[3], origin_document_reference="SYNTHETIC:OTHER_DOC")
    with pytest.raises(GateError, match="UNSUPPORTED_EXPLICIT_REFERENCE"):
        audit(nodes=n, links=(*e[:3], forged, *e[4:]))


def test_exact_sha256_claim_mismatch_fails_closed():
    n, e = fixture()
    forged = replace(e[3], asserting_sha256_claim="0" * 64)
    with pytest.raises(GateError, match="UNSUPPORTED_EXPLICIT_REFERENCE"):
        audit(nodes=n, links=(*e[:3], forged, *e[4:]))
    with pytest.raises(GateError, match="SHA256_CLAIM_REQUIRED"):
        replace(n[0], source_sha256_claim="not a digest")


def test_cross_stage_relation_spoof_fails_closed():
    n, e = fixture()
    forged = replace(e[0], kind="NORM_REFERENCED_IN_BUDGET")
    with pytest.raises(GateError, match="UNSUPPORTED_EXPLICIT_REFERENCE"):
        audit(nodes=n, links=(forged, *e[1:]))


def test_a_claimed_edge_cannot_link_backwards_in_event_time():
    n, e = fixture()
    retro = replace(n[-1], event_on="2026-01-01")
    with pytest.raises(GateError, match="UNSUPPORTED_EXPLICIT_REFERENCE"):
        audit(nodes=(*n[:-1], retro), links=e)


def test_citation_cannot_precede_the_cited_document_creation_day():
    """A prior event does not make its future source document citable.

    The source act happened on 1 January but its only declared document was
    created on 30 January; the destination's 3 January document cannot cite
    that specific later document, even when all items are captured in February.
    """
    n, e = fixture()
    future_source_document = replace(n[0], document_on="2026-01-30")
    with pytest.raises(GateError, match="UNSUPPORTED_EXPLICIT_REFERENCE"):
        audit(nodes=(future_source_document, *n[1:]), links=e)
    # Independent control: the original dated source precedes its citation.
    assert audit(nodes=n, links=e)["complete_explicit_documentary_links"] == 6


def test_same_issuer_and_document_cannot_claim_a_documentary_self_citation():
    """Two synthetic stage IDs must not turn one document into its own source."""
    n, e = fixture()
    duplicate = replace(n[1], issuer_namespace=n[0].issuer_namespace,
                        source_document_id=n[0].source_document_id,
                        source_sha256_claim=n[0].source_sha256_claim)
    self_citation = replace(e[0],
                            asserting_document_id=n[0].source_document_id,
                            asserting_sha256_claim=n[0].source_sha256_claim)
    with pytest.raises(GateError, match="UNSUPPORTED_EXPLICIT_REFERENCE"):
        # Isolate the link: later fixture edges would independently reject
        # our replacement and mask a false-positive test of self-citation.
        audit(nodes=(n[0], duplicate), links=(self_citation,))


def test_missing_endpoint_is_unknown_not_implicit_join():
    n, e = fixture()
    altered = replace(e[-1], destination_id="SYNTHETIC:UNKNOWN")
    result = audit(nodes=n, links=(*e[:-1], altered))
    assert result["unknown_or_unresolved_link_endpoints"] == 1
    assert result["complete_explicit_documentary_links"] == 5
    assert result["full_seven_stage_documentary_path_in_fixture"] is False


def test_duplicate_known_edge_id_fails_closed():
    n, e = fixture()
    with pytest.raises(GateError, match="CONFLICTING_KNOWN_IDENTITIES"):
        audit(nodes=n, links=(*e, replace(e[-1], kind=e[0].kind)))


def test_invalid_real_or_personal_source_claims_rejected():
    n, e = fixture()
    for kw in (
        {"original_authenticated": True},
        {"rights_verified": True},
        {"first_public_at": "2026-01-01T00:00:00Z"},
        {"personal_identifiers": ("REAL_PERSON",)},
    ):
        with pytest.raises(GateError, match="REAL_EVIDENCE_FORBIDDEN"):
            replace(n[0], **kw)
    for kw in (
        {"independently_authenticated": True},
        {"rights_verified": True},
        {"first_public_at": "2026-01-01T00:00:00Z"},
    ):
        with pytest.raises(GateError, match="REAL_LINK_AUTHENTICATION_FORBIDDEN"):
            replace(e[0], **kw)


def test_real_identifier_and_implicit_source_reference_rejected():
    n, e = fixture()
    with pytest.raises(GateError, match="SYNTHETIC_NODES_ONLY"):
        replace(n[0], node_id="REAL-ENTITY-1")
    with pytest.raises(GateError, match="SYNTHETIC_LINKS_ONLY"):
        replace(e[0], origin_document_reference="REAL-DOC-1")


def test_bad_capture_and_noncanonical_or_future_event_dates():
    n, e = fixture()
    with pytest.raises(GateError, match="CAPTURE_BEFORE_DOCUMENT_DAY"):
        replace(n[0], document_on="2026-03-01")
    with pytest.raises(GateError, match="DOCUMENT_BEFORE_EVENT"):
        replace(n[0], event_on="2026-02-20")
    # An otherwise valid March node does not enter the February legal cut.
    march = replace(n[0], node_id="SYNTHETIC:MARCH",
                    event_on="2026-03-03", document_on="2026-03-03",
                    captured_at="2026-03-04T12:00:00Z")
    result = audit(nodes=(*n, march), links=e, as_of="2026-03-05T12:00:00Z")
    assert result["visible_node_counts_by_kind"]["POLITICAL_COMMITMENT"] == 1


def test_jurisdictional_day_completion_madrid_not_utc_date():
    result = audit_synthetic_policy_trace(
        nodes=(), links=(), cut_on="2026-10-31",
        as_of="2026-10-31T23:30:00Z", legal_calendar_zone=ZONE,
    )
    assert result["full_seven_stage_documentary_path_in_fixture"] is False
    with pytest.raises(GateError, match="CIVIL_DAY_NOT_COMPLETED"):
        audit_synthetic_policy_trace(
            nodes=(), links=(), cut_on="2026-10-31",
            as_of="2026-10-31T22:30:00Z", legal_calendar_zone=ZONE,
        )


def test_submicrosecond_future_and_missing_zone_fail_closed():
    n, e = fixture()
    with pytest.raises(GateError, match="UNSUPPORTED_SUBMICROSECOND"):
        audit(nodes=n, links=e, as_of="2026-03-01T12:00:00.0000001Z")
    with pytest.raises(GateError, match="INVALID_TIMESTAMP|TIMESTAMP_NEEDS_TZ"):
        replace(n[0], captured_at="2026-02-10T10:00:00")
    with pytest.raises(GateError, match="MIXED_NODE_CALENDAR"):
        audit(nodes=(*n[:-1], replace(n[-1], legal_calendar_zone="UTC")), links=e)


def test_resource_bound_and_type_contract():
    n, e = fixture()
    with pytest.raises(GateError, match="BOUNDED_SYNTHETIC_TUPLES"):
        audit(nodes=list(n), links=e)
    with pytest.raises(GateError, match="BOUNDED_SYNTHETIC_TUPLES"):
        audit(nodes=n * 36, links=e)
