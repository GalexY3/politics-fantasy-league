"""Offline verification of a browser-downloaded S9 synthetic snapshot receipt.

Usage: python scripts/verify_scientific_snapshot.py <downloaded JSON>

Only Python's standard library is used: no network, SQLite, private originals,
user account store, or server startup. This verifies the closed *synthetic*
public projection and its own SHA; it cannot authenticate an external publisher.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import sys


SCHEMA = "pfl.scientific_snapshot_offline_verification.v1"
MAX_INPUT_BYTES = 1_048_576
MAX_CANONICAL_BYTES = 524_288
CUTS = {"early": "2026-10-15T12:00:00Z", "late": "2026-11-01T12:00:00Z"}
VALID_DAYS = frozenset(("2026-09-11", "2026-09-15", "2026-10-10"))
FAMILIES = frozenset(("all", "PP04", "CHAIN", "CHRONICLE"))
PUBLICATION_CEILINGS = frozenset((
    "2026-09-19T12:00:00Z", "2026-10-30T12:00:00Z", *CUTS.values(),
))
SHA_RE = re.compile(r"^[a-f0-9]{64}$")
UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
PUBLIC_NODE_LABELS = {
    "ACTOR": "Actor ficticio", "ORGANIZATION": "Organización ficticia",
    "COMMUNICATION": "Comunicación ficticia",
    "DECISION": "Decisión ficticia", "PROCESS": "Proceso ficticio",
    "ROLE": "Rol documental ficticio", "EVENT": "Evento documental ficticio",
}
PUBLIC_GRAPH_RELATIONS = frozenset((
    "ASSOCIATED_WITH_SYNTHETIC", "AUTHORED_SYNTHETIC",
    "REFERS_TO_PROCESS_SYNTHETIC", "TERMINAL_STAGE_DOCUMENTED_SYNTHETIC",
    "DOCUMENTS_OFFICE_ROLE", "FIXTURE_ROLE_RELATION",
))
PUBLIC_SOURCE_KEYS = frozenset((
    "public_id", "family", "revision", "descriptor_recipe",
    "sha256_public_descriptor", "descriptor_byte_length", "issuer_fixture",
    "first_public_at_fixture", "captured_at_fixture", "real_first_public_at",
    "real_publisher_authenticated", "coverage_temporal", "quality_gate",
    "provenance", "requested_purpose", "rights_for_public_display",
    "empirical_admitted", "immutable_revision",
))

# Pin the six VERSIONED, AUTHOR-CLOSED public descriptors. These hashes are
# not publisher signatures and do not establish rights or external provenance.
# Order matches the canonical SQL source-ID ordering of the closed fixture.
PUBLIC_FIXTURES = (
    ("S9:PUBLIC_02", "CHAIN", "fixture_v1", 133,
     "2026-09-20T12:00:00Z", "2026-09-19T12:00:00Z",
     "INTERNAL_CHAIN_SHA_AND_TYPED_KEY_CHECK_ONLY",
     "60b0a06f18473afcc23b2537becde3a064d7ea89b951f79d70440a7106a8fe2e"),
    ("S9:PUBLIC_04", "CHAIN", "fixture_v2", 133,
     "2026-10-31T12:00:00Z", "2026-10-30T12:00:00Z",
     "INTERNAL_CHAIN_SHA_AND_TYPED_KEY_CHECK_ONLY",
     "d5cfd4566c8e55f1ae135f9f1be1a10880a1843cdc0a5d8c06541ed39d7d4cd7"),
    ("S9:PUBLIC_01", "CHRONICLE", "fixture_v1", 137,
     "2026-09-20T12:00:00Z", "2026-09-19T12:00:00Z",
     "INTERNAL_CHRONICLE_SHA_AND_REVISION_CHECK_ONLY",
     "4be0c63195fb43d54c2e2d32a531267fbbb9d4c9bae0117b629d38494ef172ea"),
    ("S9:PUBLIC_03", "CHRONICLE", "fixture_v2", 137,
     "2026-10-31T12:00:00Z", "2026-10-30T12:00:00Z",
     "INTERNAL_CHRONICLE_SHA_AND_REVISION_CHECK_ONLY",
     "97cde4936b0efe6dfd835892288233570cf0200ce4ca6be119947d79aae9a4a7"),
    ("S9:PUBLIC_06", "PP04", "fixture_v1", 132,
     "2026-10-31T12:00:00Z", "2026-10-30T12:00:00Z",
     "SOURCE_LOCAL_IAEN_PARSER_FIXTURE_NOT_OUTCOME",
     "39ac5d288691c2e783631caafd44818cb6a53aafd7931d6afc4ea1d153799b6b"),
    ("S9:PUBLIC_05", "PP04", "fixture_v1", 132,
     "2026-10-31T12:00:00Z", "2026-10-30T12:00:00Z",
     "SOURCE_LOCAL_PAN_PARSER_FIXTURE_NOT_OUTCOME",
     "4240a177c1364d5c40c775c3a9f9bb3746931200f9815c558e4d3cc7a89f738b"),
)
INTAKE_FAMILY = {
    "S9:INTAKE_01": ("A", 1, "2026-09-11", "SANDBOX_VALIDATED", None),
    "S9:INTAKE_02": ("B", 1, "2026-10-10", "SANDBOX_VALIDATED", None),
    "S9:INTAKE_03": ("A", 2, "2026-09-15", "SANDBOX_VALIDATED", "S9:INTAKE_01"),
    "S9:INTAKE_04": ("X", 1, "2026-09-15", "SANDBOX_REJECTED", None),
}
INTAKE_AUTHORED_CLOCKS_AND_LABELS = {
    "S9:INTAKE_01": (
        "Documento ficticio A · versión 1", "2026-10-31T12:00:00Z",
        "2026-10-31T12:10:00Z", "2026-10-31T12:20:00Z",
    ),
    "S9:INTAKE_02": (
        "Documento ficticio B · versión 1", "2026-10-31T12:30:00Z",
        "2026-10-31T12:40:00Z", "2026-10-31T12:50:00Z",
    ),
    "S9:INTAKE_03": (
        "Documento ficticio A · versión 2", "2026-10-31T13:00:00Z",
        "2026-10-31T13:10:00Z", "2026-10-31T13:20:00Z",
    ),
    "S9:INTAKE_04": (
        "Documento ficticio con emisor inválido", "2026-10-31T13:30:00Z",
        "2026-10-31T13:40:00Z", "2026-10-31T13:50:00Z",
    ),
}
ASSESSMENT_CANDIDATES = (
    "baseline", "sha_spoof", "issuer_spoof", "rights_missing",
    "first_public_missing", "crosswalk_missing", "denominator_missing",
    "coverage_missing",
)
ASSESSMENT_PUBLIC_SHA = (
    "3974984fa5b7aceb6de5916f1c0171a54b5dee7b40d712fb17949109f3aaf89b",
    "9eaff2f768faf2e3156e3e20705d455d2150818c4013e8e3f6ec6d3ba7037921",
    "c4c6603ab55ea8d39f253757324f05b97e7f564c047949a996f4bd64f4e5cf27",
    "f0b584b8440fcbbf335776c9e8a16e4ad4eb0ffeefeebd45a1593dfed246cb06",
    "5561cd166bab853c86bc788c025935ef634434c586b21d5bab1e99da70037fd7",
    "c434bc912f854a76736bad8f2231e903fc629fd28a64a272942d12dc9da45af5",
    "c93ef6c54d580b5c3c1de2766d4d32740a8f94612e67a72732c36960f9fada00",
    "b097b53f70502ed0690bde869a092a0092513889005525e0eb9db8536ff4c69b",
)
FALSE_FLAGS = frozenset((
    "external_authenticity_certified", "rights_for_public_display_admitted",
    "rights_for_public_display", "empirical_admitted", "empirical_model_admitted",
    "real_publisher_authenticated", "real_issuer_authenticated",
    "official_issuer_authenticated", "real_original_admitted",
    "real_admission_allowed", "scientific_admission_allowed",
    "real_source_ingestion_allowed", "originals_accepted",
    "real_publisher_authenticated", "real_admission_allowed",
    "source_bytes_exposed", "private_source_ids_exposed",
    "source_local_identifiers_exposed", "cross_issuer_links_created",
    "unobserved_is_negative", "right_censor_independently_attested",
    "unplanned_is_a_terminal_negative", "independent_crosswalk_between_pan_iaen",
    "amendments_count_as_new_people_or_decisions",
))
ZERO_FIELDS = frozenset((
    "release_gates_passed", "scientific_ab_cycles", "source_rows_ingested",
    "source_rows_imported", "canonical_source_rows_imported",
    "source_rows_added_to_canonical", "logical_decisions_count",
))
NULL_FIELDS = frozenset((
    "independent_denominator", "source_local_all_received_denominator",
    "real_first_public_at", "real_enrollment_at",
))
PRIVATE_KEY_NAMES = frozenset((
    "source_id", "source_local_id", "source_local_key", "source_bytes",
    "descriptor_bytes", "receipt_bytes", "private_id", "account_id",
    "username", "password", "csrf", "cookie", "session_token",
))
PRIVATE_VALUE_RE = re.compile(
    r"(?:SYN:|REAL:|AUTHOR_[A-Z_]+:|\b[AB]:LOCAL_|-----BEGIN |(?:access|refresh)_token)",
    re.IGNORECASE,
)


class VerificationError(Exception):
    """Only stable, authored error codes are propagated to the CLI."""


def require(ok: bool, code: str) -> None:
    if not ok:
        raise VerificationError(code)


def exact_fields(value: object, fields: set[str] | frozenset[str], code: str) -> dict:
    require(type(value) is dict and value.keys() == fields, code)
    return value


def number(value: object, *, maximum: int = 100_000) -> bool:
    return type(value) is int and 0 <= value <= maximum


def is_sha(value: object) -> bool:
    return type(value) is str and SHA_RE.fullmatch(value) is not None


def utc(value: object) -> bool:
    if type(value) is not str or not UTC_RE.fullmatch(value):
        return False
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ) == value
    except ValueError:
        return False


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def unique_pairs(pairs: list[tuple[str, object]]) -> dict:
    output = {}
    for key, value in pairs:
        require(key not in output, "JSON_DUPLICATE_KEY")
        output[key] = value
    return output


def reject_constant(_: str) -> None:
    raise VerificationError("JSON_NONFINITE_NUMBER")


def parse_json(raw: bytes) -> object:
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_pairs,
                          parse_constant=reject_constant)
    except VerificationError:
        raise
    except (UnicodeDecodeError, ValueError, RecursionError) as exc:
        raise VerificationError("JSON_INVALID") from exc


def no_private_or_promoted_claims(value: object) -> None:
    """Scan the whole download, including the canonical JSON string itself."""
    if type(value) is dict:
        for key, child in value.items():
            require(key not in PRIVATE_KEY_NAMES, "PRIVATE_SOURCE_OR_ACCOUNT_FIELD")
            if key in FALSE_FLAGS:
                require(child is False, "UNAUTHORIZED_REAL_OR_RIGHTS_CLAIM")
            if key in ZERO_FIELDS:
                require(type(child) is int and child == 0, "UNAUTHORIZED_REAL_OR_RIGHTS_CLAIM")
            if key in NULL_FIELDS:
                require(child is None, "UNAUTHORIZED_REAL_OR_RIGHTS_CLAIM")
            no_private_or_promoted_claims(child)
    elif type(value) is list:
        for child in value:
            no_private_or_promoted_claims(child)
    elif type(value) is str:
        require(PRIVATE_VALUE_RE.search(value) is None, "PRIVATE_SOURCE_IDENTIFIER")


def validate_sources(distributions: object, *, cut: str, family: str,
                     as_of: str, ceiling: str) -> int:
    require(type(distributions) is list, "DESCRIPTORS_INVALID")
    expected = [
        fixture for fixture in PUBLIC_FIXTURES
        if fixture[4] <= as_of and fixture[5] <= ceiling
        and (family == "all" or fixture[1] == family)
    ]
    require(len(distributions) == len(expected), "DESCRIPTORS_NOT_CLOSED")
    for descriptor, fixture in zip(distributions, expected):
        require(type(descriptor) is dict and descriptor.keys() == PUBLIC_SOURCE_KEYS,
                "DESCRIPTORS_INVALID")
        ident, kind, revision, length, captured, published, quality, sha = fixture
        require(
            descriptor["public_id"] == ident and descriptor["family"] == kind
            and descriptor["revision"] == revision
            and type(descriptor["descriptor_byte_length"]) is int
            and descriptor["descriptor_byte_length"] == length
            and descriptor["captured_at_fixture"] == captured
            and descriptor["first_public_at_fixture"] == published
            and descriptor["sha256_public_descriptor"] == sha
            and descriptor["quality_gate"] == quality
            and descriptor["issuer_fixture"] == "FICTIONAL_" + kind
            and descriptor["descriptor_recipe"] == "S9_PUBLIC_SYNTHETIC_DESCRIPTOR_V1"
            and descriptor["coverage_temporal"] == "DISTRIBUTION_COVERAGE_UNATTESTED"
            and descriptor["provenance"] == "AUTHORED_SYNTHETIC_FIXTURE_NOT_OFFICIAL"
            and descriptor["requested_purpose"] == "PUBLIC_AGGREGATE_DISPLAY"
            and descriptor["real_first_public_at"] is None
            and descriptor["real_publisher_authenticated"] is False
            and descriptor["rights_for_public_display"] is False
            and descriptor["empirical_admitted"] is False
            and descriptor["immutable_revision"] is True,
            "DESCRIPTORS_NOT_CLOSED",
        )
    return len(distributions)


def validate_graph(graph: object, *, kind: str) -> None:
    if graph is None:
        return
    g = exact_fields(graph, {
        "nodes", "edges", "node_count", "edge_count", "issuer",
        "amendments_count_as_new_people_or_decisions",
    }, "GRAPH_INVALID")
    nodes, edges = g["nodes"], g["edges"]
    require(type(nodes) is list and type(edges) is list
            and g["node_count"] == len(nodes) and g["edge_count"] == len(edges)
            and g["issuer"] == "FICTIONAL_" + kind
            and g["amendments_count_as_new_people_or_decisions"] is False,
            "GRAPH_INVALID")
    ids = set()
    for node in nodes:
        require(type(node) is dict and node.keys() == {
            "id", "kind", "label", "documentary_revision_count",
        } and type(node["kind"]) is str
            and node["kind"] in PUBLIC_NODE_LABELS and type(node["id"]) is str
            and re.fullmatch(r"S9:" + kind + r":NODE_[0-9]{2}", node["id"])
            and node["label"] == PUBLIC_NODE_LABELS[node["kind"]]
            and number(node["documentary_revision_count"], maximum=4),
            "GRAPH_INVALID")
        require(node["id"] not in ids, "GRAPH_DUPLICATE_NODE")
        ids.add(node["id"])
    for edge in edges:
        require(type(edge) is dict and edge.keys() == {"from", "to", "kind"}
                and edge["from"] in ids and edge["to"] in ids
                and edge["kind"] in PUBLIC_GRAPH_RELATIONS,
                "GRAPH_INVALID")


def validate_assessments(payload: object, *, as_of: str, ceiling: str,
                         family: str) -> int:
    x = exact_fields(payload, {
        "schema", "assessment_count", "registered_count",
        "assessed_rejected_r5_count", "history_event_count", "assessments",
        "assessment_temporal_axis", "source_rows_ingested",
        "independent_denominator", "real_admission_allowed",
        "source_local_identifiers_exposed", "official_issuer_authenticated",
    }, "ASSESSMENTS_INVALID")
    assessments = x["assessments"]
    expected = 8 if (family == "all" and as_of >= "2026-10-31T13:00:00Z"
                     and ceiling >= "2026-10-31T13:00:00Z") else 0
    require(x["schema"] == "pfl.synthetic_admission_assessments.v1"
            and x["assessment_temporal_axis"] == "AS_OF_NOT_FACT_VALID_AT"
            and type(assessments) is list and len(assessments) == expected
            and all(type(x[key]) is int and x[key] == expected
                    for key in ("assessment_count", "registered_count",
                                "assessed_rejected_r5_count"))
            and type(x["history_event_count"]) is int
            and x["history_event_count"] == 2 * expected,
            "ASSESSMENTS_NOT_CLOSED")
    for index, item in enumerate(assessments, 1):
        require(type(item) is dict and item.keys() == {
            "assessment_id", "candidate", "status", "revision",
            "captured_at_fixture", "registered_at", "assessed_at", "history",
            "checks", "blockers", "rights_for_public_display",
            "real_original_admitted", "real_issuer_authenticated",
            "real_first_public_at", "source_rows_imported",
            "public_receipt_sha256",
        } and item["assessment_id"] == f"S9:ASSESS_{index:02d}"
            and item["candidate"] == ASSESSMENT_CANDIDATES[index - 1]
            and item["status"] == "ASSESSED_REJECTED_R5"
            and item["revision"] == "assessment_v1"
            and type(item["history"]) is list and len(item["history"]) == 2
            and [h.get("status") for h in item["history"] if type(h) is dict]
                == ["REGISTERED", "ASSESSED_REJECTED_R5"]
            and all(type(h) is dict and h.keys() == {"status", "recorded_at"}
                    and utc(h["recorded_at"]) for h in item["history"])
            and type(item["checks"]) is dict
            and type(item["blockers"]) is list and len(item["blockers"]) > 0
            and all(type(blocker) is str and len(blocker) <= 160
                    for blocker in item["blockers"])
            and item["rights_for_public_display"] is False
            and item["real_original_admitted"] is False
            and item["real_issuer_authenticated"] is False
            and item["real_first_public_at"] is None
            and type(item["source_rows_imported"]) is int
            and item["source_rows_imported"] == 0
            and is_sha(item["public_receipt_sha256"])
            and item["public_receipt_sha256"] == ASSESSMENT_PUBLIC_SHA[index - 1]
            and item["public_receipt_sha256"] == hashlib.sha256(
                canonical({k: v for k, v in item.items()
                           if k != "public_receipt_sha256"})
            ).hexdigest(), "ASSESSMENTS_NOT_CLOSED")
    return expected


def validate_intake(payload: object, *, as_of: str, ceiling: str,
                    valid_at: str, family: str) -> tuple[int, int, int]:
    data = exact_fields(payload, {
        "schema", "intake_count", "registered_count", "validated_count",
        "rejected_count", "history_event_count", "logical_source_count",
        "documentary_revision_count", "logical_decisions_count", "entries",
        "graph", "temporal_axis", "real_enrollment_at",
        "source_rows_added_to_canonical", "independent_denominator",
        "real_source_ingestion_allowed", "source_local_identifiers_exposed",
        "rights_for_public_display", "scientific_admission_allowed",
    }, "INTAKE_INVALID")
    entries = data["entries"]
    require(type(entries) is list and len(entries) <= 4, "INTAKE_INVALID")
    require(data["schema"] == "pfl.synthetic_intake_overlay.v1"
            and data["temporal_axis"]
                == "AUTHOR_STIPULATED_FIXTURE_CLOCKS_NOT_REAL_ENROLLMENT_TIME"
            and all(number(data[field], maximum=8) for field in (
                "intake_count", "registered_count", "validated_count",
                "rejected_count", "history_event_count", "logical_source_count",
                "documentary_revision_count"))
            and data["intake_count"] == data["registered_count"] == len(entries)
            and data["validated_count"] + data["rejected_count"] == len(entries)
            and data["history_event_count"] == 2 * len(entries),
            "INTAKE_COUNT_INVALID")
    # For current closed cuts, the completed 2-event intake is only visible at
    # late/as_of (not early, not a 30-Oct publication ceiling, not other families).
    visible = family == "all" and as_of == CUTS["late"] and ceiling == CUTS["late"]
    require(visible or not entries, "INTAKE_TEMPORAL_LEAK")
    ids = []
    for entry in entries:
        require(type(entry) is dict and entry.keys() == {
            "intake_id", "label", "status", "reason_code", "revision",
            "amendment_of", "quality_gate", "provenance", "valid_from",
            "captured_at_fixture", "source_first_public_at_fixture",
            "receipt_first_public_at_fixture", "registered_at_fixture",
            "validated_at_fixture", "history", "rights_for_public_display",
            "real_first_public_at", "real_issuer_authenticated",
            "empirical_admitted", "canonical_source_rows_imported",
            "public_descriptor_sha256",
        } and entry["intake_id"] in INTAKE_FAMILY
            and entry["intake_id"] not in ids, "INTAKE_ENTRY_INVALID")
        group, version, valid_from, expected_status, predecessor = INTAKE_FAMILY[entry["intake_id"]]
        label, captured, registered, assessed = INTAKE_AUTHORED_CLOCKS_AND_LABELS[
            entry["intake_id"]
        ]
        require(entry["status"] == expected_status
                and entry["revision"] == "fixture_v" + str(version)
                and entry["valid_from"] == valid_from
                and entry["amendment_of"] == predecessor
                and entry["quality_gate"] == "AUTHOR_CLOSED_SANDBOX_ONLY"
                and entry["provenance"] == "AUTHOR_CLOSED_SANDBOX_FICTION_NOT_AN_ORIGINAL"
                and entry["reason_code"] == (
                    "ISSUER_NOT_ALLOWLISTED" if group == "X" else "NONE")
                and entry["label"] == label
                and entry["captured_at_fixture"] == captured
                and entry["source_first_public_at_fixture"] == "2026-10-30T12:00:00Z"
                and entry["receipt_first_public_at_fixture"] == assessed
                and entry["registered_at_fixture"] == registered
                and entry["validated_at_fixture"] == assessed
                and all(utc(entry[k]) for k in (
                    "captured_at_fixture", "source_first_public_at_fixture",
                    "receipt_first_public_at_fixture", "registered_at_fixture",
                    "validated_at_fixture"))
                and entry["captured_at_fixture"] <= as_of
                and entry["source_first_public_at_fixture"] <= entry["captured_at_fixture"]
                and entry["receipt_first_public_at_fixture"] <= ceiling
                and entry["registered_at_fixture"] <= entry["validated_at_fixture"]
                and type(entry["history"]) is list and len(entry["history"]) == 2
                and all(type(event) is dict and event.keys() == {
                    "status", "recorded_at_fixture",
                } and utc(event["recorded_at_fixture"]) for event in entry["history"])
                and [event["status"] for event in entry["history"]]
                    == ["SANDBOX_REGISTERED", expected_status]
                and [event["recorded_at_fixture"] for event in entry["history"]]
                    == [registered, assessed]
                and entry["real_first_public_at"] is None
                and entry["real_issuer_authenticated"] is False
                and entry["rights_for_public_display"] is False
                and entry["empirical_admitted"] is False
                and type(entry["canonical_source_rows_imported"]) is int
                and entry["canonical_source_rows_imported"] == 0
                and is_sha(entry["public_descriptor_sha256"])
                and entry["public_descriptor_sha256"] == hashlib.sha256(
                    canonical({k: v for k, v in entry.items()
                               if k != "public_descriptor_sha256"})
                ).hexdigest(), "INTAKE_ENTRY_INVALID")
        ids.append(entry["intake_id"])
    require(ids == sorted(ids)
            and ("S9:INTAKE_03" not in ids or "S9:INTAKE_01" in ids),
            "INTAKE_REVISION_PARENT_MISSING")
    validated = [INTAKE_FAMILY[i] for i in ids if INTAKE_FAMILY[i][3] == "SANDBOX_VALIDATED"]
    distinct_groups = {x[0] for x in validated}
    require(data["validated_count"] == len(validated)
            and data["rejected_count"] == len(ids) - len(validated)
            and data["logical_source_count"] == len(distinct_groups)
            and data["documentary_revision_count"] == len(validated),
            "INTAKE_COUNT_INVALID")
    graph = exact_fields(data["graph"], {
        "nodes", "edges", "node_count", "edge_count",
        "logical_source_count_valid_at", "cross_issuer_links_created",
        "revisions_are_not_new_actors_or_decisions",
    }, "INTAKE_GRAPH_INVALID")
    nodes, edges = graph["nodes"], graph["edges"]
    require(type(nodes) is list and type(edges) is list
            and graph["node_count"] == len(nodes)
            and graph["edge_count"] == len(edges)
            and graph["revisions_are_not_new_actors_or_decisions"] is True
            and graph["cross_issuer_links_created"] is False,
            "INTAKE_GRAPH_INVALID")
    expected_groups = {g for g, _rev, valid, _state, _parent in validated
                       if valid <= valid_at}
    require(type(graph["logical_source_count_valid_at"]) is int
            and graph["logical_source_count_valid_at"] == len(expected_groups),
            "INTAKE_VALID_AT_INVALID")
    expected_revision_count = {
        group: sum(v[0] == group and v[2] <= valid_at for v in validated)
        for group in expected_groups
    }
    require(len(nodes) == 3 * len(expected_groups)
            and len(edges) == 2 * len(expected_groups),
            "INTAKE_GRAPH_INVALID")
    node_ids = set()
    for node in nodes:
        require(type(node) is dict and node.keys() == {
            "id", "kind", "label", "documentary_revision_count",
            "logical_identity_count",
        } and type(node["id"]) is str
            and re.fullmatch(r"S9:INTAKE_0[12]:N_(ACTOR|ORGANIZATION|PROCESS)",
                             node["id"])
            and node["kind"] in ("ACTOR", "ORGANIZATION", "PROCESS")
            and node["id"].endswith("_" + node["kind"])
            and node["label"] == PUBLIC_NODE_LABELS[node["kind"]]
            and node["id"][10:12] in ("01", "02")
            and ("A" if node["id"][10:12] == "01" else "B") in expected_groups
            and type(node["documentary_revision_count"]) is int
            and node["documentary_revision_count"] ==
                expected_revision_count["A" if node["id"][10:12] == "01" else "B"]
            and type(node["logical_identity_count"]) is int
            and node["logical_identity_count"] == 1,
            "INTAKE_GRAPH_INVALID")
        require(node["id"] not in node_ids, "INTAKE_GRAPH_DUPLICATE_NODE")
        node_ids.add(node["id"])
    for edge in edges:
        require(type(edge) is dict and edge.keys() == {"from", "to", "kind"}
                and edge["from"] in node_ids and edge["to"] in node_ids
                and edge["kind"] in (
                    "AUTHOR_CLOSED_DOCUMENTARY_ASSOCIATION",
                    "AUTHOR_CLOSED_DOCUMENTARY_PROCESS_LINK",
                ), "INTAKE_GRAPH_INVALID")
    expected_node_ids = {
        f"S9:INTAKE_{'01' if group == 'A' else '02'}:N_{kind}"
        for group in expected_groups for kind in ("ACTOR", "ORGANIZATION", "PROCESS")
    }
    expected_edges = {
        (f"S9:INTAKE_{'01' if group == 'A' else '02'}:N_ACTOR",
         f"S9:INTAKE_{'01' if group == 'A' else '02'}:N_ORGANIZATION",
         "AUTHOR_CLOSED_DOCUMENTARY_ASSOCIATION")
        for group in expected_groups
    } | {
        (f"S9:INTAKE_{'01' if group == 'A' else '02'}:N_ORGANIZATION",
         f"S9:INTAKE_{'01' if group == 'A' else '02'}:N_PROCESS",
         "AUTHOR_CLOSED_DOCUMENTARY_PROCESS_LINK")
        for group in expected_groups
    }
    require(node_ids == expected_node_ids
            and {(edge["from"], edge["to"], edge["kind"]) for edge in edges}
                == expected_edges, "INTAKE_GRAPH_INVALID")
    require((not nodes and not edges) if not expected_groups else bool(nodes),
            "INTAKE_GRAPH_INVALID")
    return len(entries), len(validated), len(ids) - len(validated)


def verify(payload: object) -> dict:
    outer = exact_fields(payload, {
        "schema", "evidence_class", "query", "source_contract",
        "receipt_schema", "snapshot_receipt", "R5", "release_gates_passed",
        "scientific_ab_cycles", "external_authenticity_certified",
        "rights_for_public_display_admitted",
    }, "EXPORT_CONTRACT_INVALID")
    require(outer["schema"] == "pfl.synthetic_scientific_registry_browser_export.v1"
            and outer["source_contract"] == "pfl.synthetic_scientific_registry.v1"
            and outer["evidence_class"] == "SYNTHETIC_LAB_ONLY"
            and outer["R5"] == "STOP_R5"
            and type(outer["release_gates_passed"]) is int
            and outer["release_gates_passed"] == 0
            and type(outer["scientific_ab_cycles"]) is int
            and outer["scientific_ab_cycles"] == 0
            and outer["external_authenticity_certified"] is False
            and outer["rights_for_public_display_admitted"] is False,
            "EXPORT_NOT_SYNTHETIC_BLOCKED")
    query = exact_fields(outer["query"], {
        "cut", "as_of", "valid_at", "family", "published_until",
    }, "QUERY_INVALID")
    cut, valid_at, family = (query["cut"], query["valid_at"], query["family"])
    require(type(cut) is str and cut in CUTS
            and type(valid_at) is str and valid_at in VALID_DAYS
            and type(family) is str and family in FAMILIES,
            "QUERY_NOT_ALLOWLISTED")
    as_of, ceiling = query["as_of"], query["published_until"]
    require(as_of == CUTS[cut] and type(ceiling) is str
            and ceiling in PUBLICATION_CEILINGS and utc(ceiling)
            and ceiling <= as_of, "QUERY_FUTURE_PUBLICATION")
    receipt = exact_fields(outer["snapshot_receipt"], {
        "schema", "canonicalization", "content_scope", "bytes", "sha256",
        "canonical_json", "external_authenticity_certified",
    }, "RECEIPT_CONTRACT_INVALID")
    require(outer["receipt_schema"] == receipt["schema"]
            == "pfl.synthetic_registry_snapshot_receipt.v1"
            and receipt["canonicalization"] == "JSON_UTF8_SORTED_KEYS_COMPACT_V1"
            and receipt["content_scope"] == "CLOSED_PUBLIC_SYNTHETIC_QUERY_ONLY"
            and receipt["external_authenticity_certified"] is False
            and type(receipt["canonical_json"]) is str
            and is_sha(receipt["sha256"])
            and type(receipt["bytes"]) is int
            and 0 < receipt["bytes"] <= MAX_CANONICAL_BYTES,
            "RECEIPT_CONTRACT_INVALID")
    canonical_bytes = receipt["canonical_json"].encode("utf-8")
    require(len(canonical_bytes) == receipt["bytes"], "RECEIPT_LENGTH_MISMATCH")
    digest = hashlib.sha256(canonical_bytes).hexdigest()
    require(digest == receipt["sha256"], "RECEIPT_SHA_MISMATCH")
    scope = parse_json(canonical_bytes)
    scope = exact_fields(scope, {
        "schema", "cut", "as_of", "valid_at", "family", "published_until",
        "distributions", "snapshot",
    }, "CANONICAL_SCOPE_INVALID")
    require(canonical(scope) == canonical_bytes, "CANONICAL_BYTES_NOT_EXACT")
    require(scope["schema"] == "pfl.synthetic_scientific_registry_snapshot.v1"
            and all(scope[key] == query[key] for key in query)
            and type(scope["distributions"]) is list,
            "CANONICAL_SCOPE_QUERY_MISMATCH")
    rebuilt = {
        "schema": "pfl.synthetic_scientific_registry_snapshot.v1",
        **query,
        "distributions": scope["distributions"],
        "snapshot": scope["snapshot"],
    }
    require(canonical(rebuilt) == canonical_bytes, "CANONICAL_SCOPE_REBUILD_MISMATCH")
    no_private_or_promoted_claims(outer)
    no_private_or_promoted_claims(scope)
    descriptors = validate_sources(scope["distributions"], cut=cut,
                                   family=family, as_of=as_of, ceiling=ceiling)
    snapshot = exact_fields(scope["snapshot"], {
        "knowledge_as_of", "valid_at", "graph", "episodes", "pp04",
        "admission_assessments", "synthetic_intake",
    }, "SNAPSHOT_CONTRACT_INVALID")
    require(snapshot["knowledge_as_of"] == as_of
            and snapshot["valid_at"] == valid_at, "SNAPSHOT_TIME_MISMATCH")
    graph = exact_fields(snapshot["graph"], {
        "chain", "chronicle", "cross_issuer_links_created",
    }, "SNAPSHOT_GRAPH_INVALID")
    require(graph["cross_issuer_links_created"] is False
            and (family in ("all", "CHAIN") or graph["chain"] is None)
            and (family in ("all", "CHRONICLE") or graph["chronicle"] is None),
            "SNAPSHOT_GRAPH_INVALID")
    validate_graph(graph["chain"], kind="CHAIN")
    validate_graph(graph["chronicle"], kind="CHRONICLE")
    episodes = exact_fields(snapshot["episodes"], {
        "chain_process_state", "explicit_negative_documented",
        "explicit_approval_documented", "pending_documented_not_negative",
        "right_censor_independently_attested", "unobserved_is_negative",
        "source_local_all_received_denominator",
    }, "EPISODES_INVALID")
    require(episodes["chain_process_state"] in {
        "APPROVED_AS_OF_SYNTHETIC_EVIDENCE", "PENDING_NOT_NEGATIVE",
        "UNKNOWN_FOLLOWUP_NOT_NEGATIVE", "NOT_YET_DOCUMENTED",
    } and all(number(episodes[k], maximum=8) for k in (
        "explicit_negative_documented", "explicit_approval_documented",
        "pending_documented_not_negative",
    )), "EPISODES_INVALID")
    pp04 = exact_fields(snapshot["pp04"], {
        "included_planned_approved", "included_pending_not_negative",
        "not_included_source_local_not_negative",
        "unplanned_is_a_terminal_negative", "independent_crosswalk_between_pan_iaen",
    }, "PP04_INVALID")
    require(all(number(pp04[k], maximum=8) for k in (
        "included_planned_approved", "included_pending_not_negative",
        "not_included_source_local_not_negative",
    )), "PP04_INVALID")
    assessments = validate_assessments(snapshot["admission_assessments"],
                                       as_of=as_of, ceiling=ceiling, family=family)
    intake, validated, rejected = validate_intake(
        snapshot["synthetic_intake"], as_of=as_of, ceiling=ceiling,
        valid_at=valid_at, family=family,
    )
    return {
        "schema": SCHEMA,
        "status": "PASS",
        "sha256": digest,
        "cut": cut,
        "as_of": as_of,
        "valid_at": valid_at,
        "family": family,
        "published_until": ceiling,
        "synthetic_only": True,
        "source_descriptors": descriptors,
        "intake_count": intake,
        "validated_synthetic_intakes": validated,
        "rejected_synthetic_intakes": rejected,
        "synthetic_assessments_rejected_r5": assessments,
        "R5": "STOP_R5",
        "release_gates_passed": 0,
        "scientific_ab_cycles": 0,
        "public_release_eligible": False,
        "publisher_identity_verified": False,
        "real_source_admission_verified": False,
        "rights_for_public_display_admitted": False,
    }


class SafeArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        del message
        raise VerificationError("ARGUMENTS_INVALID")


def main(argv: list[str] | None = None) -> int:
    parser = SafeArgumentParser(description=(
        "Verifica offline la coherencia de una descarga S9 sintética. "
        "El SHA no autentica identidad, derechos ni fuente real."
    ))
    parser.add_argument("downloaded_json", help="Archivo JSON exportado desde S9")
    try:
        args = parser.parse_args(argv)
        path = Path(args.downloaded_json)
        with path.open("rb") as stream:
            raw = stream.read(MAX_INPUT_BYTES + 1)
        require(len(raw) <= MAX_INPUT_BYTES, "INPUT_TOO_LARGE")
        result = verify(parse_json(raw))
    except VerificationError as exc:
        result = {
            "schema": SCHEMA,
            "status": "FAIL",
            "error_code": str(exc),
            "public_release_eligible": False,
            "publisher_identity_verified": False,
        }
    except (OSError, TypeError, ValueError, OverflowError,
            UnicodeError, RecursionError) as exc:
        del exc
        result = {
            "schema": SCHEMA,
            "status": "FAIL",
            "error_code": "INPUT_UNAVAILABLE_OR_INVALID",
            "public_release_eligible": False,
            "publisher_identity_verified": False,
        }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
