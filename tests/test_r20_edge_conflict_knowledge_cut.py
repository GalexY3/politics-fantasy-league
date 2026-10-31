"""R20 synthetic falsifier: known edge conflicts must precede event-day cuts.

The test was written against R19 HEAD, before inspecting its outcomes. It
uses no official IDs, original documents, private data or political outcomes.
"""
from dataclasses import replace

from politics_fantasy.synthetic_registration_graph import (
    OfficialStageKey, StageVersion, TypedStageEdge, audit_graph,
)
from politics_fantasy.synthetic_temporal_witness import KnowledgeInterval


def key(stage):
    return OfficialStageKey(
        "SYNTHETIC:ASSEMBLY", "SYNTHETIC:REGIME", "SYNTHETIC:PROCESS",
        stage, f"SYNTHETIC:{stage}_1",
    )


def stage(k):
    known = "2026-01-01T00:00:00Z"
    return StageVersion(
        key=k, revision="SYNTHETIC:V1", event_on="2020-06-01",
        document_on="2020-06-02", publisher_edition_at=None,
        observed=KnowledgeInterval(known, known),
        captured_at="2026-01-02T00:00:00Z", original_sha_claim="a" * 64,
    )


def edge_pair():
    earlier = TypedStageEdge(
        edge_id="SYNTHETIC:EDGE_1", origin=key("REGISTRATION"),
        destination=key("FILE"), relation="REGISTER_TO_FILE",
        document_on="2020-06-02", publisher_edition_at=None,
        observed=KnowledgeInterval(
            "2026-01-01T00:00:00Z", "2026-01-01T00:00:00Z"),
        captured_at="2026-01-02T00:00:00Z", original_sha_claim="b" * 64,
    )
    # Same claimed edge ID, but a later separately observed document dates the
    # assertion in 2021. Without edge revision/authentication, quarantine is
    # appropriate, not silent selection of the older edge at a 2020 event cut.
    later = replace(
        earlier, document_on="2021-06-02",
        observed=KnowledgeInterval(
            "2026-02-01T00:00:00Z", "2026-02-01T00:00:00Z"),
        captured_at="2026-02-02T00:00:00Z", original_sha_claim="c" * 64,
    )
    return earlier, later


def report(edges, as_of):
    return audit_graph(
        records=(stage(key("REGISTRATION")), stage(key("FILE"))),
        edges=edges, cut_on="2020-12-31", as_of=as_of,
    )


def test_later_known_conflicting_edge_cannot_be_hidden_by_document_cut():
    old, later = edge_pair()
    before = report((old, later), "2026-01-15T00:00:00Z")
    after = report((old, later), "2026-03-01T00:00:00Z")
    assert before["status"] == "SYNTHETIC_DOCUMENTARY_GRAPH_ONLY"
    assert before["visible_claimed_edges"] == 1
    # New R20 oracle: the later known document is a conflict with the same
    # claimed edge identity, even when its document date lies outside cut_on.
    assert after["status"] == "VISIBLE_CONFLICTING_EDGE_CLAIM_QUARANTINED"
    assert after["visible_claimed_edges"] is None
    assert after["official_cross_institution_links_authenticated"] is False


def test_conflicting_edge_with_unknown_future_capture_does_not_taint_older_asof():
    old, future = edge_pair()
    assert report((old, future), "2026-01-15T00:00:00Z") == report(
        (old,), "2026-01-15T00:00:00Z")


def test_nonconflicting_later_document_outside_cut_does_not_gain_edge():
    old, later = edge_pair()
    unrelated = replace(later, edge_id="SYNTHETIC:EDGE_2")
    result = report((old, unrelated), "2026-03-01T00:00:00Z")
    assert result["status"] == "SYNTHETIC_DOCUMENTARY_GRAPH_ONLY"
    assert result["visible_claimed_edges"] == 1
    assert result["scientific_cycles"] == 0
