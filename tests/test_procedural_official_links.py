"""Adversarial synthetic cases for registration-to-expediente link provenance."""
from dataclasses import replace

import pytest

from politics_fantasy.procedural_index_contract import FrameScope, GateError
from politics_fantasy.procedural_official_links import (
    ScopedRef, EntryRef, CaseRef, DualIdDocumentLink, audit_explicit_links,
)


SCOPE = FrameScope(
    institution="SYNTHETIC_CHAMBER", legislature="XI",
    family="SYNTHETIC_ILP", risk_entry="SOURCE_REPORTED_REGISTRATION",
    selection_rule="ALL_REGISTERED_AT_RISK",
    registry_scope="ALL_PRESENTED_CLAIM_UNATTESTED",
)


def entry(k: str, received="2024-01-02") -> EntryRef:
    return EntryRef(ScopedRef("SYNTHETIC_CHAMBER", "XI", "SYNTHETIC_ILP", "REGISTRY", k), received)


def file(k: str, opened="2024-01-05") -> CaseRef:
    return CaseRef(ScopedRef("SYNTHETIC_CHAMBER", "XI", "SYNTHETIC_ILP", "EXPEDIENTE", k), opened)


def link(a: EntryRef, b: CaseRef, *, sha="a"*64, doc="2024-01-04") -> DualIdDocumentLink:
    return DualIdDocumentLink(
        a.key, b.key, sha, "https://fictional.example.test/documented-dual-id",
        document_dated_on=doc,
    )


def audit(entries=(), cases=(), links=(), as_of=None, **kw):
    return audit_explicit_links(
        scope=kw.pop("scope", SCOPE), entries=entries, cases=cases, links=links,
        capture_completed_at="2026-10-31T08:12:02.500Z",
        as_of=as_of, **kw,
    )


def test_many_to_one_requires_explicit_edges_and_does_not_certify_population():
    a,b,c=entry("R1"),entry("R2"),entry("R3")
    d,e=file("P1"),file("P2")
    x=audit([a,b,c],[d,e],[link(a,d),link(b,d,sha="b"*64)])
    assert x["entry_rows"]==3 and x["file_rows"]==2
    assert x["linked_entries"]==2 and x["linked_files"]==1
    assert x["files_with_multiple_entry_links"]==1
    assert x["entries_without_documented_file_link_in_this_snapshot"]==1
    assert x["files_without_documented_entry_link_in_this_snapshot"]==1
    assert x["denominator_for_survival_estimation"] is None
    assert x["complete_all_received_register_independently_verified"] is False
    assert not x["rights_to_use_identifiers_adjudicated"]
    assert x["statuses_or_terminal_outcomes_admitted"] is False
    assert x["first_public_at"] is None
    assert "R1" not in str(x) and "P1" not in str(x)


def test_same_textual_id_on_two_levels_is_not_an_implicit_link():
    a,b=entry("ONE"),file("ONE")
    x=audit([a],[b],[])
    assert x["linked_entries"]==0 and x["linked_files"]==0
    assert x["entries_without_documented_file_link_in_this_snapshot"]==1


def test_orphan_document_links_do_not_create_or_kill_institutional_cases():
    a,b=entry("A"),file("B")
    unobserved=entry("UNKNOWN")
    x=audit([a],[b],[link(unobserved,b)])
    assert x["linked_entries"]==0
    assert x["candidate_links_referring_to_unobserved_entries"]==1
    assert x["entries_without_documented_file_link_in_this_snapshot"]==1
    assert x["link_orphan_is_not_negative_decision"]


def test_capture_clock_and_diagnostics_never_leak_at_past_cut():
    a,b=entry("A"),file("B")
    l=link(a,b)
    for t in ["2023-01-01T00:00:00Z", "2026-10-31T08:12:02.999999Z"]:
        x=audit([a],[b],[l],as_of=t)
        assert x["entry_rows"] is None and x["source_scope"] is None
        assert x["local_capture_safe_by"] is None
        assert x["document_links"] is None
        assert "2026-10-31T08:12" not in str(x)
        assert "SYNTHETIC_CHAMBER" not in str(x)
    x=audit([a],[b],[l],as_of="2026-10-31T08:12:03Z")
    assert x["entry_rows"]==1
    assert x["local_capture_safe_by"]=="2026-10-31T08:12:03+00:00"


def test_namespace_and_jurisdiction_collision_rejected():
    a,b=entry("A"),file("B")
    wrong=replace(b,key=replace(b.key,institution="OTHER_CHAMBER"))
    with pytest.raises(GateError,match="CROSS_SCOPE_ENTRY_OR_FILE"):
        audit([a],[wrong],[])
    with pytest.raises(GateError,match="CROSS_SCOPE_DOCUMENT_RELATION"):
        audit([a],[b],[replace(link(a,b),case=wrong.key)])
    with pytest.raises(GateError,match="MIXED_REGISTRY_AND_CASE_ID_NAMESPACE"):
        audit([a],[replace(b,key=replace(b.key,namespace="REGISTRY"))],[])


def test_denominator_or_legal_rights_cannot_be_self_asserted():
    a,b=entry("A"),file("B")
    with pytest.raises(TypeError):
        audit([a],[b],[link(a,b)], independent_denominator=2)
    with pytest.raises(TypeError):
        audit([a],[b],[link(a,b)], source_rights_approved=True)
    with pytest.raises(GateError,match="DOCUMENT_FIRST_PUBLICATION_NOT_ESTABLISHED"):
        DualIdDocumentLink(a.key,b.key,"a"*64,"https://fictional.example.test/",
                           first_public_at="2024-01-03T00:00:00Z")


def test_invalid_provenance_and_nominal_matching_rejected():
    a,b=entry("A"),file("B")
    with pytest.raises(GateError,match="LINK_BY_NAME_TITLE_OR_DATE_FORBIDDEN"):
        replace(link(a,b),relation_basis="FUZZY_TITLE_MATCH")
    with pytest.raises(GateError,match="DOCUMENT_SOURCE_URI_INVALID"):
        replace(link(a,b),claimed_official_uri="http://bad.example/")
    with pytest.raises(GateError,match="DOCUMENT_ORIGINAL_SHA_CLAIM_MISSING"):
        replace(link(a,b),claimed_original_sha256="not-a-sha")


def test_deduplication_ambiguity_and_chronology_anomaly():
    a,b=entry("A"),file("B")
    one=link(a,b)
    with pytest.raises(GateError,match="DUPLICATE_LINK_DOCUMENT_REPLAY"):
        audit([a],[b],[one,one])
    x=audit([a],[b],[replace(one,document_dated_on="2023-12-01")])
    assert x["links_dated_before_entry_as_documentary_anomalies"]==1
    assert x["unique_claimed_dual_id_relations"]==1
    with pytest.raises(GateError,match="DOCUMENT_DATE_AFTER_CAPTURE"):
        audit([a],[b],[replace(one,document_dated_on="2027-01-01")])


def test_resource_and_entry_gate():
    with pytest.raises(GateError,match="LINK_AUDIT_REQUIRES_REGISTRATION_ENTRY_FRAME"):
        audit(scope=replace(SCOPE,risk_entry="OFFICIAL_ADMISSION"))
    with pytest.raises(GateError,match="DUPLICATE_SOURCE_LOCAL_ID"):
        audit(entries=[entry("A"),entry("A")])
    with pytest.raises(GateError,match="REGISTRATION_DATE_AFTER_CAPTURE"):
        audit(entries=[entry("FUTURE",received="2027-01-01")])
    with pytest.raises(GateError,match="TIMESTAMP_NEEDS_TZ"):
        audit(as_of="2026-10-31T08:12:03")
