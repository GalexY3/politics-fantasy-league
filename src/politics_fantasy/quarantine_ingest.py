"""Offline capture -> source-schema audit -> quarantine, NOT an HTTP ingest API.

All returned metadata are local, document-scoped and non-release-grade. No
signature, historical first-public timestamp, rights or personal identity can be
verified by parsing bytes. Never add real original documents to Git.
"""
from __future__ import annotations
import json
from pathlib import Path

from .ingest import import_url
from .secure_store import append_private_jsonl, preflight_private_storage, read_private_object
from .source_original_qa import audit_congress_vote
from .source_original_senate_qa import audit_original_senate_session

DOCUMENT_KINDS = {
    "congreso_vote": "congreso",
    "senado_session": "senado",
}


def capture_validate_quarantine(*, url: str, source: str, document_kind: str,
                                root: Path, opener=None,
                                min_interval: float = 3.0) -> dict:
    """Capture a single allowed source and audit format; never release it.

    Invalid source-kind requests fail BEFORE network. Invalid document schemas
    and tampered stored bytes remain quarantined with no original content in
    the returned result. Only an authorized private local caller may invoke it.
    """
    if document_kind not in DOCUMENT_KINDS:
        raise ValueError("UNSUPPORTED_DOCUMENT_KIND")
    if DOCUMENT_KINDS[document_kind] != source:
        raise ValueError("SOURCE_DOCUMENT_KIND_MISMATCH")
    root = Path(root)
    preflight_private_storage(root, "quarantine_reviews.jsonl")
    snapshot = import_url(url=url, source=source, root=root, opener=opener,
                          min_interval=min_interval)
    result = {
        "capture_id": snapshot["capture_id"],
        "source_id": source,
        "document_kind": document_kind,
        "sha256": snapshot["sha256"],
        "raw_object": snapshot["raw_object"],
        "capture_manifest": "manifest.jsonl",
        "quarantine_state": "QUARANTINED_SCHEMA_FAILED",
        "schema_checked": False,
        "validator_result": None,
        "error_code": None,
        "first_public_at": None,
        "original_publisher_signature_verified": False,
        "senate_no_votan_institutional_semantics_verified": False,
        "source_license_approved": False,
        "stable_person_identity_certified": False,
        "release_grade": False,
        "real_person_scoring": False,
        "http_ingest_endpoint_connected": False,
    }
    try:
        raw_bytes = read_private_object(root, snapshot["raw_object"], snapshot["sha256"])
    except (ValueError, TypeError, OSError) as exc:
        result["quarantine_state"] = "QUARANTINED_INTEGRITY_FAILED"
        # No source-authored paths or exception details are exported.
        result["error_code"] = (
            "RAW_SHA_MISMATCH" if str(exc) == "RAW_SHA_MISMATCH"
            else "RAW_OBJECT_INTEGRITY_OR_ACCESS_FAILED"
        )
    else:
        try:
            if document_kind == "congreso_vote":
                validated = audit_congress_vote(json.loads(raw_bytes.decode("utf-8")))
            else:
                validated = audit_original_senate_session(raw_bytes)
            result["schema_checked"] = True
            result["quarantine_state"] = "QUARANTINED_SCHEMA_PASSED"
            result["validator_result"] = validated
        except (ValueError, TypeError, KeyError, UnicodeError, OSError) as exc:
            result["error_code"] = type(exc).__name__
    append_private_jsonl(root, "quarantine_reviews.jsonl", result)
    return result
